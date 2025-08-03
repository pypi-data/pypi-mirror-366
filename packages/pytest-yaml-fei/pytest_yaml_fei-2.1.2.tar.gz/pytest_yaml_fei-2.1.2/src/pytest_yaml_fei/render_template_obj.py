import re
from .log import log
import jinja2
import yaml


# 解决 yaml 文件中日期被转成 datetime 类型
yaml.SafeLoader.yaml_implicit_resolvers = {
    k: [r for r in v if r[0] != 'tag:yaml.org,2002:timestamp'] for
    k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def add(value, num=0):
    """jinja2 过滤器 add函数"""
    return int(value)+num


def to_str(value):
    return f'"{value}"'


env_filter = jinja2.Environment(
    variable_start_string='${', variable_end_string='}'
)
env_filter.filters["add"] = add
env_filter.filters["str"] = to_str


def rend_template_str(template_str, *args, **kwargs):
    """
       渲染模板字符串, 改写了默认的引用变量语法{{var}}, 换成${var}
            模板中引用变量语法 ${var},
            调用函数 ${fun()}
        :return: 渲染之后的值
    """
    # -------------解决函数内部参数引用变量-------
    def re_replace_template_str(match) -> str:
        """
        匹配的值--渲染模板加载内部引用变量
        """
        res_result = match.group()
        res_result_ = str(res_result).lstrip('${').rstrip('}')
        if '${' in res_result_ and '}' in res_result_ and res_result_.find('${') < res_result_.find('}'):
            instance_temp = env_filter.from_string(res_result_)
            temp_render_res = instance_temp.render(*args, **kwargs)
            return '${' + temp_render_res + '}'
        else:
            return res_result

    # 特殊处理${P()}表达式，支持带引号和不带引号的路径参数
    if template_str.startswith("${P(") and template_str.endswith(")}"):
        template_raw_str = template_str[4:-2].strip()
        if not (template_raw_str.startswith("'") and template_raw_str.endswith("'")) and \
                not (template_raw_str.startswith('"') and template_raw_str.endswith('"')):
            # 如果路径参数没有引号，自动加上单引号
            template_str = "${P('" + template_raw_str + "')}"

    # 正则替换
    template_str = re.sub('\$\{(.+)\}', re_replace_template_str, template_str) # noqa
    instance_template = env_filter.from_string(template_str)
    template_render_res = instance_template.render(*args, **kwargs)
    if template_str.startswith("${") and template_str.endswith("}") and template_str.count('${') == 1:
        template_raw_str = template_str.rstrip('}').lstrip('${')
        if kwargs.get(template_raw_str):
            log.info(f"取值表达式: {template_raw_str}, 取值结果：{kwargs.get(template_raw_str)} {type(kwargs.get(template_raw_str))}")
            return kwargs.get(template_raw_str)
        if template_raw_str.startswith("str(") and template_raw_str.endswith(")"):
            log.info(f"取值表达式: {template_raw_str}, 取值结果：{template_render_res} {type(template_render_res)}")
            return str(template_render_res)
        try:
            result_value = yaml.safe_load(template_render_res)
            log.info(f"取值表达式: {template_raw_str}, 取值结果：{result_value} {type(result_value)}")
            return result_value
        except Exception as msg:   # noqa
            log.info(f"取值表达式: {template_raw_str}, 取值结果：{template_render_res}  {type(template_render_res)}")
            return template_render_res
    else:
        return template_render_res


def rend_template_obj(t_obj: dict, *args, **kwargs):
    """
       传 dict 对象，通过模板字符串递归查找模板字符串，转行成新的数据
    """
    if isinstance(t_obj, dict):
        for key, value in t_obj.items():
            if isinstance(value, str):
                t_obj[key] = rend_template_str(value, *args, **kwargs)
            elif isinstance(value, dict):
                rend_template_obj(value, *args, **kwargs)
            elif isinstance(value, list):
                t_obj[key] = rend_template_array(value, *args, **kwargs)
            else:
                pass
    return t_obj


def rend_template_array(t_array, *args, **kwargs):
    """
       传 list 对象，通过模板字符串递归查找模板字符串
    """
    if isinstance(t_array, list):
        new_array = []
        for item in t_array:
            if isinstance(item, str):
                new_array.append(rend_template_str(item, *args, **kwargs))
            elif isinstance(item, list):
                new_array.append(rend_template_array(item, *args, **kwargs))
            elif isinstance(item, dict):
                new_array.append(rend_template_obj(item, *args, **kwargs))
            else:
                new_array.append(item)
        return new_array
    else:
        return t_array


def rend_template_any(any_obj, *args, **kwargs):
    """渲染模板对象:str, dict, list"""
    if isinstance(any_obj, str):
        return rend_template_str(any_obj, *args, **kwargs)
    elif isinstance(any_obj, dict):
        return rend_template_obj(any_obj, *args, **kwargs)
    elif isinstance(any_obj, list):
        return rend_template_array(any_obj, *args, **kwargs)
    else:
        return any_obj
