from . import create_funtion
import types
from inspect import Parameter
from . import validate
from . import extract
from . import my_builtins
from . import render_template_obj
from . import exceptions
import copy
import yaml
from pathlib import Path
import inspect
import allure
from .log import log
from .db import ConnectMysql
from .redis import ConnectRedis
import mimetypes
from requests_toolbelt import MultipartEncoder
import time
import json


class RunYaml(object):
    """ 运行yaml """

    def __init__(self, raw: dict, module: types.ModuleType, g: dict):
        self.raw = raw  # 读取yaml 原始数据
        self.module = module  # 动态创建的 module 模型
        self.module_variable = {}  # 模块变量
        self.context = {}
        self.hooks = {}  # 全局hooks
        self.g = g  # 全局配置

    def run(self):
        if not self.raw.get('config'):
            self.raw['config'] = {}
        # config 获取用例名称 name 和 base_url
        # config_name = self.raw.get('config').get('name', '')
        base_url = self.raw.get('config').get('base_url', None)
        config_variables = self.raw.get('config').get('variables', {})
        config_fixtures = self.raw.get('config').get('fixtures', [])
        config_params = self.raw.get('config').get('parameters', [])
        config_hooks = self.raw.get('config').get('hooks', {})
        config_exports = self.raw.get('config').get('export', [])  # 新增全局导出变量
        config_mark = self.raw.get('config').get('mark', None)  # 获取config中的mark标记
        config_allure = self.raw.get('config', {}).get('allure', {})

        # 模块变量渲染
        self.context.update(__builtins__)  # noqa 内置函数加载
        self.context.update(my_builtins.__dict__)  # 自定义函数对象
        db_obj = self.execute_mysql()
        redis_obj = self.execute_redis()
        self.context.update(**self.g)  # 加载全局配置
        self.context.update(**db_obj)  # 加载操作mysql 内置函数
        self.context.update(**redis_obj)  # 加载操作redis 内置函数
        self.module_variable = render_template_obj.rend_template_any(config_variables, **self.context)

        # 模块变量 添加到模块全局变量
        if isinstance(self.module_variable, dict):
            self.context.update(self.module_variable)

        # 支持 2 种参数化格式数据
        config_params = render_template_obj.rend_template_any(config_params, **self.context)
        config_fixtures = render_template_obj.rend_template_any(config_fixtures, **self.context)
        config_fixtures, config_params = self.parameters_date(config_fixtures, config_params)
        case = {}  # 收集用例名称和执行内容
        ordered_cases = []
        unordered_cases = []

        for case_name, case_value in self.raw.items():
            case_fixtures = []
            case_params = []
            if case_name == 'config':
                continue  # 跳过config 非用例部分

            # case_name 必须 test 开头
            if not str(case_name).startswith('test'):
                case_name = 'test_' + str(case_name)

            case_data = case_value if isinstance(case_value, list) else [case_value]

            # 检查是否有order设置
            case_order = None
            if isinstance(case_value, dict):
                case_order = case_value.get('order')
            elif isinstance(case_value, list) and len(case_value) > 0 and isinstance(case_value[0], dict):
                case_order = case_value[0].get('order')

            if case_order is not None:
                ordered_cases.append((case_order, case_name, case_data))
            else:
                unordered_cases.append((case_name, case_data))

        # 按order值排序用例
        ordered_cases.sort(key=lambda x: x[0])

        # 合并有序和无序用例
        for order, case_name, case_data in ordered_cases:
            case[case_name] = case_data

        for case_name, case_data in unordered_cases:
            case[case_name] = case_data

            # 用例参数获取
            if len(case[case_name]) < 1:
                log.debug('test case not item to run !')
            else:
                if 'fixtures' in case[case_name][0]:
                    case_raw_fixtures = case[case_name][0].get('fixtures', [])
                    case_fixtures = render_template_obj.rend_template_any(case_raw_fixtures, **self.context)

                if "parameters" in case[case_name][0]:
                    log.info('parameters 参数化执行用例')
                    case_raw_parameters = case[case_name][0].get('parameters', [])
                    # case_raw_fixtures = case[case_name][0].get('fixtures', [])
                    # 支持 2 种参数化格式数据
                    case_params = render_template_obj.rend_template_any(case_raw_parameters, **self.context)
                    # case_fixtures = render_template_obj.rend_template_any(case_raw_fixtures, **self.context)
                    # case 中的参数化 覆盖 config 的参数化

                case_fixtures, case_params = self.parameters_date(case_fixtures, case_params)

            def execute_yaml_case(args):
                # 获取被调用函数名称
                log.info(f'执行文件-> {self.module.__name__}.yml')
                log.info(f'base_url-> {base_url or args.get("request").config.option.base_url}')
                log.info(f'config variables-> {self.module_variable}')
                call_function_name = inspect.getframeinfo(inspect.currentframe().f_back)[2]
                log.info(f'运行用例-> {call_function_name}')

                # 更新 fixture 的值 到context
                self.context.update(args)
                for step in case[call_function_name]:
                    # 添加 allure 报告--> case
                    case_allure = step.get('allure', {})
                    # config中allure属性优先级高于case中的allure属性，两者都有，优先取config中的
                    allure_attr = {**case_allure, **config_allure}
                    # 如果feature和title不在allure_attr中，则使用默认值
                    if 'feature' not in allure_attr:
                        allure_attr['feature'] = f'{self.module.__name__}.yml'
                    if 'title' not in allure_attr:
                        allure_attr['title'] = call_function_name
                    allure_attr = render_template_obj.rend_template_any(allure_attr, **self.context)
                    try:
                        for k, v in allure_attr.items():
                            eval(f'allure.dynamic.{k}')(v)
                    except Exception as msg:
                        raise exceptions.ParserError(f'Parsers error: {msg}') from None

                    response = None
                    api_validate = []
                    step_name = step.get('name', 'not step name')
                    step_context = self.context.copy()  # 步骤变量

                    # 添加 allure 报告--> step
                    with allure.step(step_name):
                        pass

                    if 'validate' not in step.keys():
                        step['validate'] = []

                    for item, value in step.items():
                        # 执行用例里面的方法
                        if item == 'name':
                            pass  # noqa
                        elif item == 'parameters':
                            pass
                        elif item == 'fixtures':
                            pass
                        elif item == 'variables':  # step 步骤变量获取
                            copy_value = copy.deepcopy(value)
                            if not isinstance(copy_value, dict):
                                log.error('step variables->variables must be dict type!')
                            else:
                                step_variables_value = render_template_obj.rend_template_any(
                                    copy_value, **self.context
                                )
                                step_context.update(step_variables_value)
                        elif item == 'testcase':
                            testcase_result = self.run_testcase_step(args, step, context=step_context)
                            # 将testcase的返回值更新到上下文
                            if isinstance(testcase_result, dict):
                                step_context.update(testcase_result)
                                self.context.update(testcase_result)
                            continue
                        elif item == 'api':
                            root_dir = args.get('request').config.rootdir  # 内置request 获取root_dir
                            api_path = Path(root_dir).joinpath(value)
                            raw_api = yaml.safe_load(api_path.open(encoding='utf-8'))
                            api_validate = raw_api.get('validate', [])
                            copy_value = copy.deepcopy(raw_api.get('request'))  # 深拷贝一份新的value
                            response = self.run_request(args, copy_value, config_hooks, base_url, context=step_context)
                        elif item == 'request':
                            copy_value = copy.deepcopy(value)  # 深拷贝一份新的value
                            copy_config_hooks = copy.deepcopy(config_hooks)
                            response = self.run_request(args, copy_value, copy_config_hooks, base_url,
                                                        context=step_context)
                        elif item == 'extract':
                            # 提取变量
                            copy_value = copy.deepcopy(value)
                            extract_value = render_template_obj.rend_template_any(copy_value, **step_context)
                            extract_result = self.extract_response(response, extract_value)
                            log.info(f'extract  提取变量-> {extract_result}')

                            # 添加到模块变量
                            self.module_variable.update(extract_result)
                            # 添加到步骤变量
                            step_context.update(extract_result)
                            if isinstance(self.module_variable, dict):
                                self.context.update(self.module_variable)  # 加载模块变量

                            # 处理全局导出变量
                            case_exports = step.get('export', [])  # 获取case中的export
                            all_exports = list(set(config_exports + case_exports))  # 合并config和case中的export
                            if all_exports and isinstance(extract_result, dict):
                                export_result = {}
                                for export_var in all_exports:
                                    if export_var in extract_result:
                                        export_result[export_var] = extract_result[export_var]
                                        self.g[export_var] = extract_result[export_var]
                                if export_result:
                                    log.info(f'export 全局导出变量-> {export_result}')
                        elif item == 'export':
                            pass  # export已经在extract处理中处理
                        elif item == 'validate':
                            copy_value = copy.deepcopy(value)
                            # 合并校验
                            copy_value.extend([v for v in api_validate if v not in copy_value])
                            validate_value = render_template_obj.rend_template_any(copy_value, **step_context)
                            log.info(f'validate 校验内容-> {validate_value}')
                            self.validate_response(response, validate_value)
                        elif item == 'sleep':
                            sleep_value = render_template_obj.rend_template_any(value, **step_context)
                            try:
                                log.info(f'sleep time: {sleep_value}')
                                time.sleep(sleep_value)
                            except Exception as msg:
                                log.error(f'Run error: sleep value must be int or float, error msg: {msg}')
                        elif item == 'skip':
                            skip_reason = render_template_obj.rend_template_any(value, **step_context)
                            import pytest
                            pytest.skip(skip_reason)
                        elif item == 'skipif':  # noqa
                            if_exp = render_template_obj.rend_template_any(value, **step_context)
                            log.info(f'skipif : {eval(str(if_exp))}')  # noqa
                            if eval(str(if_exp)):
                                import pytest
                                pytest.skip(str(if_exp))
                        elif item == 'mark':
                            pass  # 跳过mark标记，已在run方法中处理
                        elif item == 'allure':  # noqa
                            pass  # 跳过mark标记，已在run方法中处理
                        else:
                            value = render_template_obj.rend_template_any(value, **step_context)
                            try:
                                eval(item)(value)
                            except Exception as msg:
                                raise exceptions.ParserError(f'Parsers error: {msg}') from None

            fun_fixtures = []
            # 合并config 和 case 用例 fixtures
            fun_fixtures.extend(config_fixtures)
            [fun_fixtures.append(fixt) for fixt in case_fixtures if fixt not in fun_fixtures]
            # 参数化以 case 用例 优先
            fun_params = case_params or config_params
            f = create_funtion.create_function_from_parameters(
                func=execute_yaml_case,
                # parameters 传内置fixture 和 用例fixture
                parameters=self.function_parameters(fun_fixtures),
                documentation=case_name,
                func_name=case_name,
                func_filename=f"{self.module.__name__}.py",
            )

            # 向 module 中加入函数
            setattr(self.module, str(case_name), f)
            if fun_params:
                # 向 module 中加参数化数据的属性
                setattr(self.module, f'{case_name}_params_data', fun_params)

            # 处理mark标记
            marks = []

            def process_mark(mark):
                if isinstance(mark, str):
                    return [m.strip() for m in mark.split(',')]
                elif isinstance(mark, list):
                    return mark
                return []

            # 处理config中的mark标记
            if config_mark:
                marks.extend(process_mark(config_mark))

            # 处理case中的mark标记
            if isinstance(case_value, dict):
                case_mark = case_value.get('mark')
            else:
                case_mark = case_value[0].get('mark') if isinstance(case_value, list) and len(case_value) > 0 else None

            if case_mark:
                marks.extend(process_mark(case_mark))

            # 应用mark标记到函数
            if marks:
                import pytest
                for mark in marks:
                    if isinstance(mark, str):
                        if mark.startswith('runtime('):
                            # 处理runtime标记
                            try:
                                runtime_value = eval(mark[8:-1])
                                f = pytest.mark.runtime(runtime_value)(f)
                            except Exception as e:
                                log.error(f"Error processing runtime mark: {mark}. Error: {str(e)}")
                        else:
                            # 处理普通标记
                            marker = getattr(pytest.mark, mark, None)
                            if marker is None:
                                # 如果marker不存在，动态创建
                                marker = pytest.mark.mark(mark)
                            f = marker(f)
                    elif isinstance(mark, dict):
                        # 处理字典形式的mark，例如：{'timeout': 300}
                        for key, value in mark.items():
                            marker = getattr(pytest.mark, key, None)
                            if marker is None:
                                marker = pytest.mark.mark(key)
                            f = marker(value)(f)

            # 保存原始yaml数据到module中，供plugin.py使用
            if not hasattr(self.module, '_pytest_yaml_raw'):
                self.module._pytest_yaml_raw = self.raw

    def run_testcase_step(self, args, step, context=None):
        """运行testcase步骤"""
        if context is None:
            context = self.context.copy()

        testcase_path = step.get('testcase')
        if not testcase_path:
            raise exceptions.ParserError("testcase path is required")

        # 获取root_dir并解析testcase路径
        root_dir = args.get('request').config.rootdir
        testcase_file = Path(root_dir).joinpath(testcase_path).resolve()

        # 读取testcase文件内容
        try:
            with testcase_file.open(encoding='utf-8') as f:
                testcase_data = yaml.safe_load(f)
        except Exception as e:
            raise exceptions.ParserError(f"Failed to load testcase file: {str(e)}")

        # 创建临时RunYaml实例运行testcase
        testcase_runner = RunYaml(testcase_data, self.module, self.g)
        testcase_runner.run()

        # 实际执行testcase中的所有步骤
        result = {}
        config_hooks = testcase_data.get('config', {}).get('hooks', {})
        base_url = testcase_data.get('config', {}).get('base_url', None)

        for case_name, case_steps in testcase_data.items():
            if case_name == 'config':
                continue

            # 执行每个步骤
            for step_item in case_steps:
                if not isinstance(step_item, dict):
                    continue

                response = None
                step_context = context.copy()

                # 处理variables
                if 'variables' in step_item:
                    variables = render_template_obj.rend_template_any(
                        step_item['variables'], **step_context
                    )
                    step_context.update(variables)

                # 处理request/api
                if 'request' in step_item:
                    request_value = copy.deepcopy(step_item.get('request'))
                    response = self.run_request(args, request_value, config_hooks, base_url, context=step_context)
                elif 'api' in step_item:
                    api_path = Path(root_dir).joinpath(step_item['api'])
                    raw_api = yaml.safe_load(api_path.open(encoding='utf-8'))
                    request_value = copy.deepcopy(raw_api.get('request'))
                    response = self.run_request(args, request_value, config_hooks, base_url, context=step_context)

                # 处理extract
                if 'extract' in step_item and response:
                    extract_value = render_template_obj.rend_template_any(
                        step_item['extract'], **step_context
                    )
                    extract_result = self.extract_response(response, extract_value)
                    result.update(extract_result)
                    step_context.update(extract_result)
                    self.context.update(extract_result)

                # 处理validate
                if 'validate' in step_item and response:
                    validate_value = render_template_obj.rend_template_any(
                        step_item['validate'], **step_context
                    )
                    self.validate_response(response, validate_value)

                # 处理sleep
                if 'sleep' in step_item:
                    sleep_value = render_template_obj.rend_template_any(
                        step_item['sleep'], **step_context
                    )
                    time.sleep(sleep_value)

                # 处理export
                if 'export' in step_item:
                    export_vars = step_item.get('export', [])
                    for var in export_vars:
                        if var in result:
                            self.g[var] = result[var]

        # 获取testcase的config导出变量
        testcase_exports = testcase_data.get('config', {}).get('export', [])
        # 获取步骤中的导出变量
        step_exports = step.get('export', [])
        all_exports = list(set(testcase_exports + step_exports))

        # 提取并导出变量
        if all_exports:
            export_result = {}
            for export_var in all_exports:
                if export_var in result:
                    export_result[export_var] = result[export_var]
                    self.g[export_var] = result[export_var]
            if export_result:
                log.info(f'export 全局导出变量-> {export_result}')
                if context:
                    context.update(export_result)
                self.context.update(export_result)

        return result

    def run_request(self, args, copy_value, config_hooks, base_url, context=None):
        """运行request请求"""
        request_session = args.get('requests_function') or args.get('requests_module') or args.get('requests_session')
        # 加载参数化的值和fixture的值
        if context is None:
            context = self.context.copy()
        context.update(**self.g)  # 加载全局配置
        request_value = render_template_obj.rend_template_any(copy_value, **context)
        # request 请求参数预处理
        request_pre = self.request_hooks(config_hooks, request_value)
        if request_pre:
            # 执行 pre request 预处理
            if context:
                context.update({"req": request_value})
            else:
                self.context.update({"req": request_value})
            self.run_request_hooks(request_pre, request_value, context=context)
        # request请求 带上hooks "response"参数
        self.response_hooks(config_hooks, request_value)

        # multipart/form-data 文件上传支持
        root_dir = args.get('request').config.rootdir  # 内置request 获取root_dir
        request_value = self.multipart_encoder_request(request_value, root_dir)
        log.info(f'--------  request info ----------')
        log.info(f'yml raw  -->: {request_value}')
        log.info(f'method   -->: {request_value.get("method", "")}')
        log.info(f'url      -->: {request_value.get("url", "")}')
        request_headers = {}
        request_headers.update(request_session.headers)
        if request_value.get("headers", {}):
            request_headers.update(request_value.get("headers", {}))
        log.info(f'headers  -->: {request_headers}')
        if request_value.get('json'):
            log.info(f'json     -->: {json.dumps(request_value.get("json", {}), ensure_ascii=False)}')
        else:
            log.info(f'data     -->: {request_value.get("data", {})}')
        response = request_session.send_request(
            base_url=base_url,
            **request_value
        )
        log.info(f'------  response info  {getattr(response, "status_code")} {getattr(response, "reason", "")} ------ ')
        log.info(
            f'耗时     <--: {getattr(response, "elapsed", "").total_seconds() if getattr(response, "elapsed", "") else ""}s')
        log.info(f'url      <--: {getattr(response, "url", "")}')
        log.info(f'headers  <--: {getattr(response, "headers", "")}')
        log.info(f'cookies  <--: {dict(getattr(response, "cookies", {}))}')
        log.info(f'raw text <--: {getattr(response, "text", "")}')
        return response

    @staticmethod
    def function_parameters(config_fixtures) -> list:
        """ 测试函数传 fixture """
        # 测试函数的默认请求参数
        function_parameters = [
            Parameter('request', Parameter.POSITIONAL_OR_KEYWORD)  # 内置request fixture
        ]
        # 获取传给用例的 fixtures
        if isinstance(config_fixtures, str):
            config_fixtures = [item.strip(" ") for item in config_fixtures.split(',')]
        if not config_fixtures:
            function_parameters.append(
                Parameter('requests_session', Parameter.POSITIONAL_OR_KEYWORD),
            )
        else:
            if 'requests_function' in config_fixtures:
                function_parameters.append(
                    Parameter('requests_function', Parameter.POSITIONAL_OR_KEYWORD),
                )
            elif 'requests_module' in config_fixtures:
                function_parameters.append(
                    Parameter('requests_module', Parameter.POSITIONAL_OR_KEYWORD),
                )
            else:
                function_parameters.append(
                    Parameter('requests_session', Parameter.POSITIONAL_OR_KEYWORD),
                )
            for fixture in config_fixtures:
                if fixture not in ['requests_function', 'requests_module']:
                    function_parameters.append(
                        Parameter(fixture, Parameter.POSITIONAL_OR_KEYWORD),
                    )
        return function_parameters

    @staticmethod
    def parameters_date(fixtures, parameters):
        """
        参数化实现多种方式：
        1. 旧版本格式（保持兼容性）
        2. 新版本格式（支持单变量、多变量和笛卡尔积）

        参数化实现2种方式：
        方式1：
            config:
               name: post示例
               fixtures: username, password
               parameters:
                 - [test1, '123456']
                 - [test2, '123456']
        方式2：
            config:
               name: post示例
               parameters:
                 - {"username": "test1", "password": "123456"}
                 - {"username": "test2", "password": "1234562"}

        方式3：只有一个变量需要参数化
            config:
              parameters:
                x: ["a", "b", "c"]

        方式4：有2个变量需要参数化
            config:
                parameters:
                  x,y: [["a", "b"], ['c', 'd']]
                  # 也可以实现横线隔开
                 x-y: [["a", "b"], ['c', 'd']]

        方式5：笛卡尔积
            config:
                parameters:
                  x: ["a", 'b']
                  y: ["hello", "world"]

        :returns
        fixtures: 用例需要用到的fixtures:  ['username', 'password']
        parameters: 参数化的数据list of list : [['test1', '123456'], ['test2', '123456']]
        """
        import itertools

        if isinstance(fixtures, str):
            fixtures = [item.strip() for item in fixtures.split(',')]

        # 处理新版本格式
        if isinstance(parameters, dict):
            new_fixtures = []
            new_parameters = []

            for key, value in parameters.items():
                if ',' in key or '-' in key:
                    # 多变量参数化
                    vars = key.replace('-', ',').split(',')
                    vars = [v.strip() for v in vars]
                    new_fixtures.extend(vars)
                    if isinstance(value[0], dict):
                        # 处理字典列表格式
                        new_parameters.append([[item[var] for var in vars] for item in value])
                    elif isinstance(value[0], (list, tuple)):
                        new_parameters.append(value)
                    else:
                        new_parameters.append(list(zip(*[value] * len(vars))))
                else:
                    # 单变量参数化
                    new_fixtures.append(key)
                    # 确保value是可迭代对象
                    if isinstance(value, (str, bytes, dict)):
                        new_parameters.append([[v] for v in value])
                    else:
                        # 如果value不可迭代，将其作为单个参数值处理
                        new_parameters.append([[value]])

            # 生成笛卡尔积
            cartesian_product = list(itertools.product(*new_parameters))
            flattened_product = [list(itertools.chain(*p)) for p in cartesian_product]

            return new_fixtures, flattened_product

        # 处理旧版本格式（保持兼容性）
        if isinstance(parameters, list) and len(parameters) >= 1:
            if isinstance(parameters[0], dict):
                # list of dict
                params = list(parameters[0].keys())
                new_parameters = [list(item.values()) for item in parameters]
                # fixtures 追加参数化的参数
                for param in params:
                    if param not in fixtures:
                        fixtures.append(param)
                return fixtures, new_parameters
            else:
                # list of list
                return fixtures, parameters
        else:
            return fixtures, []

    def hooks_event(self, hooks):
        """
        获取 requests 请求执行钩子, 仅支持2个事件，request 和 response
        :param hooks: yml 文件中读取的原始数据
           hooks = {
                "response": ['fun1', 'fun2'],
                "request": ['fun3', 'fun4']
            }
        :return: 返回结果示例:
            hooks = {
                "response": [fun1, fun2],
                "request": [fun3, fun4]
            }
        """
        # response hook事件
        hooks_response = hooks.get('response', [])
        if isinstance(hooks_response, str):
            # 字符串切成list
            hooks_response = [item.strip(" ") for item in hooks_response.split(',')]
        # 获取 my_builtins 模块函数对象
        hooks_response = [self.context.get(func) for func in hooks_response if self.context.get(func)]
        hooks['response'] = hooks_response
        # request  hook事件
        hooks_request = hooks.get('request', [])
        if isinstance(hooks_request, str):
            # 字符串切成list
            hooks_request = [item.strip(" ") for item in hooks_request.split(',')]
        # 获取 my_builtins 模块函数对象
        hooks_request = [self.context.get(func) for func in hooks_request if self.context.get(func)]
        hooks['request'] = hooks_request
        return hooks

    def request_hooks(self, config_hooks: dict, request_value: dict) -> dict:
        """ 合并全局config_hooks 和 单个请求 hooks 参数
            config_hooks = {
                "response": ['fun1', 'fun2'],
                "request": ['fun3', 'fun4']
            }
            request_value = {
                "method": "GET",
                "hooks": {"response": ['fun5']}
            }
            发送请求，request上带上hooks参数
            :return {"request": ['fun3', 'fun4']} 合并后的request 预处理函数
        """
        # request hooks 事件 (requests 库只有response 事件)
        config_request_hooks = []
        if 'request' in config_hooks.keys():
            config_request_hooks = config_hooks.get('request')
            if isinstance(config_request_hooks, str):
                # 字符串切成list
                config_request_hooks = [item.strip(" ") for item in config_request_hooks.split(',')]
        req_request_hooks = request_value.get('hooks', {})
        if 'request' in req_request_hooks.keys():
            req_hooks = req_request_hooks.pop('request')
            if isinstance(req_hooks, str):
                # 字符串切成list
                req_hooks = [item.strip(" ") for item in req_hooks.split(',')]
            for h in req_hooks:
                config_request_hooks.append(h)
        # 更新 request_value
        if config_request_hooks:
            hooks = self.hooks_event({'request': config_request_hooks})
            # 去掉值为空的response 事件
            new_hooks = {key: value for key, value in hooks.items() if value}
            return new_hooks
        return {'request': []}

    def run_request_hooks(self, request_pre: dict, request_value, context=None):
        """执行请求预处理hooks内容
        request_pre: 待执行的预处理函数
        """
        funcs = request_pre.get('request', [])
        if not funcs:
            return request_value
        import inspect
        for fun in funcs:
            # 获取函数对象的入参
            ars = [arg_name for arg_name, v in inspect.signature(fun).parameters.items()]
            if 'req' in ars:
                if context:
                    fun(*[context.get(arg) for arg in ars])
                else:
                    fun(*[self.context.get(arg) for arg in ars])
            else:
                fun()
        return request_value

    def response_hooks(self, config_hooks: dict, request_value: dict) -> dict:
        """ 合并全局config_hooks 和 单个请求 hooks 参数
            config_hooks = {
                "response": ['fun1', 'fun2'],
                "request": ['fun3', 'fun4']
            }
            request_value = {
                "method": "GET",
                "hooks": {"response": ['fun5']}
            }
            发送请求，request上带上hooks参数
            :return request_value  合并后的request请求
        """
        # request hooks 事件 (requests 库只有response 事件)
        if 'response' in config_hooks.keys():
            config_response_hooks = config_hooks.get('response')
            if isinstance(config_response_hooks, str):
                # 字符串切成list
                config_response_hooks = [item.strip(" ") for item in config_response_hooks.split(',')]
        else:
            config_response_hooks = []
        req_response_hooks = request_value.get('hooks', {})
        if 'response' in req_response_hooks.keys():
            resp_hooks = req_response_hooks.get('response')
            if isinstance(resp_hooks, str):
                # 字符串切成list
                resp_hooks = [item.strip(" ") for item in resp_hooks.split(',')]
            for h in resp_hooks:
                config_response_hooks.append(h)
        # 更新 request_value
        if config_response_hooks:
            hooks = self.hooks_event({'response': config_response_hooks})
            # 去掉值为空的response 事件
            new_hooks = {key: value for key, value in hooks.items() if value}
            request_value['hooks'] = new_hooks
        return request_value

    @staticmethod
    def extract_response(response, extract_obj: dict):
        """extract 提取返回结果"""
        extract_result = {}
        if isinstance(extract_obj, dict):
            for extract_var, extract_expression in extract_obj.items():
                extract_var_value = extract.extract_by_object(response, extract_expression)  # 实际结果
                extract_result[extract_var] = extract_var_value
            return extract_result
        else:
            return extract_result

    @staticmethod
    def validate_response(response, validate_check: list) -> None:
        """校验结果"""
        for check in validate_check:
            for check_type, check_value in check.items():
                actual_value = extract.extract_by_object(response, check_value[0])  # 实际结果
                expect_value = check_value[1]  # 期望结果
                log.info(f'validate 校验结果-> {check_type}: [{actual_value}, {expect_value}]')
                if check_type in ["eq", "equals", "equal"]:
                    validate.equals(actual_value, expect_value)
                elif check_type in ["lt", "less_than"]:
                    validate.less_than(actual_value, expect_value)
                elif check_type in ["le", "less_or_equals"]:
                    validate.less_than_or_equals(actual_value, expect_value)
                elif check_type in ["gt", "greater_than"]:
                    validate.greater_than(actual_value, expect_value)
                elif check_type in ["ne", "not_equal", "not_equal"]:
                    validate.not_equals(actual_value, expect_value)
                elif check_type in ["str_eq", "str_equals", "string_equals", "string_equal"]:
                    validate.string_equals(actual_value, expect_value)
                elif check_type in ["len_eq", "length_equal", "length_equals"]:
                    validate.length_equals(actual_value, expect_value)
                elif check_type in ["len_gt", "length_greater_than"]:
                    validate.length_greater_than(actual_value, expect_value)
                elif check_type in ["len_ge", "length_greater_or_equals"]:
                    validate.length_greater_than_or_equals(actual_value, expect_value)
                elif check_type in ["len_lt", "length_less_than"]:
                    validate.length_less_than(actual_value, expect_value)
                elif check_type in ["len_le", "length_less_or_equals"]:
                    validate.length_less_than_or_equals(actual_value, expect_value)
                elif check_type in ["contains", "contain"]:
                    validate.contains(actual_value, expect_value)
                elif check_type in ["bool_eq", "bool_equal", "bool_equals"]:
                    validate.bool_equals(actual_value, expect_value)
                else:
                    if hasattr(validate, check_type):
                        getattr(validate, check_type)(actual_value, expect_value)
                    else:
                        log.error(f'{check_type}  not valid check type')

    def execute_mysql(self):
        """执行 mysql 操作"""
        env_obj = self.g.get('env')  # 获取环境配置
        db_objects = {}

        # 处理多数据库配置
        for attr_name in dir(env_obj):
            attr_value = getattr(env_obj, attr_name)
            if isinstance(attr_value, ConnectMysql):
                try:
                    # 直接使用已配置的ConnectMysql实例
                    db_objects[attr_name] = {
                        "query_sql": attr_value.query_sql,
                        "execute_sql": attr_value.execute_sql
                    }
                except Exception as msg:
                    log.error(f"Failed to use database connection for {attr_name}: {msg}")

        # 处理单数据库配置
        if hasattr(env_obj, 'MYSQL_HOST') or hasattr(env_obj, 'DB_INFO'):
            try:
                if hasattr(env_obj, 'DB_INFO'):
                    db = ConnectMysql(**env_obj.DB_INFO)
                else:
                    db = ConnectMysql(
                        host=env_obj.MYSQL_HOST,
                        user=env_obj.MYSQL_USER,
                        password=env_obj.MYSQL_PASSWORD,
                        port=env_obj.MYSQL_PORT,
                        database=env_obj.MYSQL_DATABASE,
                    )
                # 将默认数据库函数直接注入到context中
                self.context["query_sql"] = db.query_sql
                self.context["execute_sql"] = db.execute_sql
            except Exception as msg:
                log.error(f"Failed to create default database connection: {msg}")
                self.context["query_sql"] = lambda x: log.error("Default database connection failed")
                self.context["execute_sql"] = lambda x: log.error("Default database connection failed")
        elif not db_objects:
            # 如果没有配置任何数据库
            self.context["query_sql"] = lambda x: log.error("No database configuration found")
            self.context["execute_sql"] = lambda x: log.error("No database configuration found")

        return db_objects

    def execute_redis(self):
        """执行 redis 操作"""
        env_obj = self.g.get('env')  # 获取环境配置
        redis_objects = {}

        # 处理多redis配置
        for attr_name in dir(env_obj):
            attr_value = getattr(env_obj, attr_name)
            if isinstance(attr_value, ConnectRedis):
                try:
                    redis_objects[attr_name] = attr_value
                except Exception as msg:
                    log.error(f"Failed to use redis connection for {attr_name}: {msg}")

        # 处理单redis配置 - 支持REDIS_*环境变量形式和REDIS字典配置
        if hasattr(env_obj, 'REDIS_HOST') or hasattr(env_obj, 'REDIS'):
            try:
                if hasattr(env_obj, 'REDIS'):
                    redis_config = env_obj.REDIS
                    if isinstance(redis_config, dict):
                        redis = ConnectRedis(**redis_config)
                else:
                    redis = ConnectRedis(
                        host=getattr(env_obj, 'REDIS_HOST', 'localhost'),
                        port=getattr(env_obj, 'REDIS_PORT', 6379),
                        password=getattr(env_obj, 'REDIS_PASSWORD', None),
                        db=getattr(env_obj, 'REDIS_DB', 0),
                        decode_responses=getattr(env_obj, 'REDIS_DECODE_RESPONSES', True)
                    )

                # 将默认redis函数直接注入到context中
                self.context["redis"] = redis
            except Exception as msg:
                log.error(f"Failed to create default redis connection: {msg}")
                self.context["redis"] = None

        return redis_objects

    @staticmethod
    def upload_file(filepath: Path):
        """根据文件路径，自动获取文件名称和文件mime类型"""
        if not filepath.exists():
            log.error(f"文件路径不存在：{filepath}")
            return
        mime_type = mimetypes.guess_type(filepath)[0]
        return (
            filepath.name, filepath.open("rb"), mime_type
        )

    def multipart_encoder_request(self, request_value: dict, root_dir):
        """判断请求头部 Content-Type: multipart/form-data 格式支持"""
        if 'files' in request_value.keys():
            fields = []
            data = request_value.get('data', {})
            fields.extend(data.items())  # 添加data数据
            for key, value in request_value.get('files', {}).items():
                if Path(root_dir).joinpath(value).is_file():
                    fields.append(
                        (key, self.upload_file(Path(root_dir).joinpath(value).resolve()))
                    )
                else:
                    fields.append((key, value))
            m = MultipartEncoder(
                fields=fields
            )
            request_value.pop('files')  # 去掉 files 参数
            request_value['data'] = m
            new_headers = request_value.get('headers', {})
            new_headers.update({'Content-Type': m.content_type})
            request_value['headers'] = new_headers
            return request_value
        else:
            return request_value
