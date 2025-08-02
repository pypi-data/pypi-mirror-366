import types
import yaml
from pathlib import Path
from _pytest.python import Module
import pytest
from requests.adapters import HTTPAdapter
from . import http_session
from . import runner
from .log import set_log_format, log
from .report_notify import ding_ding_notify, fei_shu_notify, we_com_notify, email_notify
from .create_funtion import import_from_file
import os
import platform
import time
from . import g  # 全局 g 对象，获取项目配置
from .start_project import create_start_project
from .db import ConnectMysql
from .redis import ConnectRedis


@pytest.fixture(scope="session")
def requests_session(request):
    """全局session 全部用例仅执行一次"""
    s = http_session.HttpSession()
    # max_retries=2 重试2次
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    proxies_ip = request.config.getoption("--proxies-ip") or request.config.getini("proxies_ip")
    if proxies_ip:
        # 添加全局代理
        s.proxies = {
            "http": f"http://{proxies_ip}",
            "https": f"https://{proxies_ip}"
        }
    # 添加全局base_url
    s.base_url = request.config.option.base_url
    yield s
    s.close()


@pytest.fixture()
def requests_function(request):
    """用例级别 session， 每个用例都会执行一次"""
    s = http_session.HttpSession()
    # max_retries=2 重试2次
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    proxies_ip = request.config.getoption("--proxies-ip") or request.config.getini("proxies_ip")
    if proxies_ip:
        # 添加全局代理
        s.proxies = {
            "http": f"http://{proxies_ip}",
            "https": f"https://{proxies_ip}"
        }
    # 添加全局base_url
    s.base_url = request.config.option.base_url
    yield s
    s.close()


@pytest.fixture(scope="module")
def requests_module(request):
    """模块级别 session， 每个模块仅执行一次"""
    s = http_session.HttpSession()
    # max_retries=2 重试2次
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    proxies_ip = request.config.getoption("--proxies-ip") or request.config.getini("proxies_ip")
    if proxies_ip:
        # 添加全局代理
        s.proxies = {
            "http": f"http://{proxies_ip}",
            "https": f"https://{proxies_ip}"
        }
    # 添加全局base_url
    s.base_url = request.config.option.base_url
    yield s
    s.close()


@pytest.fixture(scope="session", autouse=True)
def environ(request):
    """Return a env object"""
    config = request.config
    env_name = config.getoption("--env") or config.getini("env")
    if env_name is not None:
        return g.get('env')


@pytest.fixture(scope="session", autouse=True)
def cleanup_connections():
    """
    自动清理数据库和redis连接
    在测试会话结束时自动关闭所有数据库连接，包括MySQL和Redis
    """
    yield
    # 测试会话结束时清理所有连接
    ConnectMysql.close_all_connections()
    ConnectRedis.close_all_connections()


def pytest_collect_file(file_path: Path, parent):  # noqa
    """
        收集测试用例：
        1.测试文件以.yml 或 .yaml 后缀的文件
        2.并且以 test 开头或者 test 结尾
    """
    if file_path.suffix in [".yml", ".yaml"] and (file_path.name.startswith("test") or file_path.name.endswith("test")):
        py_module = Module.from_parent(parent, path=file_path)
        # 动态创建 module
        module = types.ModuleType(file_path.stem)
        # 解析 yaml 内容
        raw_dict = yaml.safe_load(file_path.open(encoding='utf-8'))
        if not raw_dict:
            return
        # 用例名称test_开头
        run = runner.RunYaml(raw_dict, module, g)
        run.run()  # 执行用例
        # 重写属性
        py_module._getobj = lambda: module  # noqa
        return py_module


def pytest_collection_modifyitems(config, items):
    """根据mark表达式过滤测试用例，使用pytest原始的mark过滤逻辑"""
    from _pytest.mark import MarkMatcher, _parse_expression

    # 获取mark表达式(命令行优先于ini配置)
    markexpr = config.getoption("--mark") or config.getini("mark")
    if not markexpr:
        return

    expr = _parse_expression(markexpr, "Wrong expression passed to '-m'")
    remaining = []
    deselected = []
    # item表示每个用例
    for item in items:
        if expr.evaluate(MarkMatcher.from_markers(item.iter_markers())):
            remaining.append(item)
        else:
            deselected.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = remaining


def pytest_generate_tests(metafunc):  # noqa
    """测试用例参数化功能实现
    :param metafunc:共有五个属性值
         metafunc.fixturenames:参数化收集时的参数名称
         metafunc.module:使用参数名称进行参数化的测试用例所在的模块d对象
         metafunc.config:测试用例会话
         metafunc.function:测试用例对象,即函数或方法对象
         metafunc.cls: 测试用例所属的类的类对象
    :return: none
    """
    if hasattr(metafunc.module, f'{metafunc.function.__qualname__}_params_data'):
        params_data = getattr(metafunc.module, f'{metafunc.function.__qualname__}_params_data')
        params_len = 0  # 参数化 参数的个数
        if isinstance(params_data, list):
            if isinstance(params_data[0], list):
                params_len = len(params_data[0])
            elif isinstance(params_data[0], dict):
                params_len = len(params_data[0].keys())
            else:
                params_len = 1
        params_args = metafunc.fixturenames[-params_len:]
        if len(params_args) == 1:
            if not isinstance(params_data[0], list):
                params_data = [[p] for p in params_data]
        metafunc.parametrize(
            params_args,
            params_data,
            scope="function"
        )


def pytest_addoption(parser):  # noqa
    # run env
    parser.addini('env', default=None, help='run environment by test or uat ...')
    parser.addoption(
        "--env", action="store", default=None, help="run environment by test or uat ..."
    )
    # base url
    if 'base_url' not in parser._ininames:
        parser.addini("base_url", help="base url for the api test.")
        parser.addoption(
            "--base-url",
            metavar="url",
            default=os.getenv("PYTEST_BASE_URL", None),
            help="base url for the api test.",
        )
    # proxies_ip
    parser.addini("proxies_ip", default=None, help="proxies_ip for the  test.")
    parser.addoption(
        "--proxies-ip",
        action="store", default=None,
        help="proxies_ip for the  test.",
    )
    # 创建 demo
    parser.addoption(
        "--start-project", action="store_true", help="start demo project"
    )

    # 运行时长
    parser.addini('runtime', default=None, help='run case timeout...')
    parser.addoption(
        "--runtime", action="store", default=None, help="run case timeout..."
    )

    # 添加mark配置
    parser.addini('mark', default=None, help='default mark expression to filter tests')
    parser.addoption(
        "--mark",
        action="store",
        default=None,
        help="override default mark expression to filter tests",
    )

    # fake语言参数
    parser.addini('locale', default=None, help='fake language')
    parser.addoption(
        "--locale", action="store", default=None, help="fake language"
    )


def collect_markers_from_project(root_path):
    """扫描项目收集所有使用的marker"""
    markers = set()
    yaml_files = list(Path(root_path).rglob("test*.yaml")) + list(Path(root_path).rglob("test*.yml"))

    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                if not content:
                    continue

                # 收集config级别的marker
                config_mark = content.get('config', {}).get('mark', '')
                if config_mark:
                    if isinstance(config_mark, str):
                        if config_mark.startswith('runtime('):
                            markers.add('runtime')
                        else:
                            markers.update(m.strip() for m in config_mark.split(','))
                    elif isinstance(config_mark, list):
                        for mark in config_mark:
                            if isinstance(mark, str):
                                if mark.startswith('runtime('):
                                    markers.add('runtime')
                                else:
                                    markers.add(mark.strip())

                # 收集case级别的marker
                for case_name, case_value in content.items():
                    if case_name == 'config':
                        continue
                    if isinstance(case_value, list):
                        case_data = case_value[0] if case_value and isinstance(case_value[0], dict) else {}
                    else:
                        case_data = case_value if isinstance(case_value, dict) else {}

                    case_mark = case_data.get('mark', '')
                    if case_mark:
                        if isinstance(case_mark, str):
                            if case_mark.startswith('runtime('):
                                markers.add('runtime')
                            else:
                                markers.update(m.strip() for m in case_mark.split(','))
                        elif isinstance(case_mark, list):
                            for mark in case_mark:
                                if isinstance(mark, str):
                                    if mark.startswith('runtime('):
                                        markers.add('runtime')
                                    else:
                                        markers.add(mark.strip())
        except Exception as e:
            continue

    return markers


def pytest_configure(config):  # noqa
    # 配置日志文件和格式
    g['root_path'] = config.rootpath  # 项目根路径
    set_log_format(config)
    config.addinivalue_line(
        "filterwarnings", "ignore::DeprecationWarning"
    )
    config.addinivalue_line(
        "filterwarnings", "ignore::urllib3.exceptions.InsecureRequestWarning"
    )

    # 自动收集并注册所有marker
    markers = collect_markers_from_project(config.rootdir)
    for marker in markers:
        config.addinivalue_line(
            "markers",
            f"{marker}: auto-registered marker"
        )

    # 确保runtime标记总是被注册
    if 'runtime' not in markers:
        # 运行时长
        config.addinivalue_line(
            "markers",
            "runtime: mark test with expected execution time (e.g. runtime(1.5))"
        )

    run_time = config.getoption("--runtime") or config.getini("runtime")
    if run_time is not None:
        config.option.runtime = run_time

    # 加载 项目 config 文件配置
    config_path = Path(config.rootdir).joinpath('config.py')
    if config_path.exists():
        # 如果有配置文件，加载当前运行环境的配置
        run_env_name = config.getoption('--env') or config.getini('env')
        if run_env_name:
            config_module = import_from_file(config_path)
            # config_module = __import__("config", globals(), locals(), [])
            if hasattr(config_module, 'env'):
                g["env"] = config_module.env.get(run_env_name)  # noqa
                g["env_name"] = run_env_name
    if g.get('env'):
        # 获取配置环境的 BASE_URL
        _base_url = g["env"].BASE_URL if hasattr(g.get('env'), 'BASE_URL') else None
    else:
        _base_url = None
    # base_url
    base_url = config.getoption("--base-url") or config.getini("base_url") or _base_url
    g["base_url"] = base_url
    if base_url is not None:
        config.option.base_url = base_url
        if hasattr(config, "_metadata"):
            config._metadata["base_url"] = base_url  # noqa

    # 获取 allure 报告的路径
    allure_dir = config.getoption('--alluredir')  # noqa
    if allure_dir:
        allure_report_path = Path(os.getcwd()).joinpath(allure_dir)
        if not allure_report_path.exists():
            allure_report_path.mkdir()
        allure_report_env = allure_report_path.joinpath('environment.properties')
        if not allure_report_env.exists():
            allure_report_env.touch()  # 创建
            # 写入环境信息
            root_dir = str(config.rootdir).replace("\\", "\\\\")
            allure_report_env.write_text(f'system={platform.system()}\n'
                                         f'systemVersion={platform.version()}\n'
                                         f'pythonVersion={platform.python_version()}\n'
                                         f'pytestVersion={pytest.__version__}\n'
                                         f'rootDir={root_dir}\n')


def pytest_terminal_summary(terminalreporter, exitstatus, config):  # noqa
    """收集测试结果"""
    total = terminalreporter._numcollected  # noqa
    stats = terminalreporter.stats

    if total > 0:
        passed = len([i for i in stats.get('passed', []) if i.when != 'teardown'])
        failed = len([i for i in stats.get('failed', []) if i.when != 'teardown'])
        error = len([i for i in stats.get('error', []) if i.when != 'teardown'])
        skipped = len([i for i in stats.get('skipped', []) if i.when != 'teardown'])
        deselected = len(stats.get('deselected', []))
        if total - skipped - deselected == 0:  # noqa
            successful = 0
        else:
            successful = len(stats.get('passed', [])) / total * 100  # noqa
        duration = time.time() - terminalreporter._sessionstarttime  # noqa
        is_success = exitstatus == 0
        markdown_text = f"""### 执行结果:
- 运行环境: {g.get('env_name')}
- 运行base_url: {g.get('base_url')}
- 持续时间: {duration: .2f} 秒  \n

### 本次运行结果: <font color="{'info' if is_success else 'warning'}">{'成功' if is_success else '失败'}</font>
- 总用例数: {total}
- 通过用例：{passed}
- 跳过用例：{skipped}
- 取消用例： {deselected}
- 失败用例： {failed}
- 异常用例： {error}
- 通过率： {successful: .2f} % \n
"""
        if g.get('env'):
            if hasattr(g["env"], 'DING_TALK'):
                ding_talk = g["env"].DING_TALK
                if ding_talk.get('text'):
                    ding_talk['text'] = markdown_text + ding_talk['text']
                else:
                    ding_talk['text'] = markdown_text
                ding_ding_notify(**ding_talk)

            # 添加飞书通知
            if hasattr(g["env"], 'FEI_SHU'):
                fei_shu = g["env"].FEI_SHU
                fei_shu['is_success'] = is_success
                if fei_shu.get('text'):
                    fei_shu['text'] = markdown_text + fei_shu['text']
                else:
                    fei_shu['text'] = markdown_text
                fei_shu_notify(**fei_shu)

            # 添加企业微信通知
            if hasattr(g["env"], 'WE_COM'):
                we_com = g["env"].WE_COM
                we_com['is_success'] = is_success
                if we_com.get('text'):
                    we_com['text'] = markdown_text + we_com['text']
                else:
                    we_com['text'] = markdown_text
                we_com_notify(**we_com)

            # 添加邮件通知
            if hasattr(g["env"], 'EMAIL'):
                email_config = g["env"].EMAIL
                if email_config.get('content'):
                    email_config['content'] = markdown_text + email_config['content']
                else:
                    email_config['content'] = markdown_text
                email_notify(**email_config)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    out = yield
    # 获取测试报告
    report = out.get_result()
    if report.when == 'call' and report.outcome == 'passed':
        # 1. 获取命令行参数中的runtime
        cmd_runtime = item.config.option.runtime
        cmd_runtime = float(cmd_runtime) if cmd_runtime else None

        # 2. 获取pytest.ini配置中的runtime
        ini_runtime = item.config.getini('runtime')
        ini_runtime = float(ini_runtime) if ini_runtime else None

        # 3. 获取config和case级别的runtime标记
        config_runtime = None
        case_runtime = None

        if isinstance(item.parent, Module):
            module = item.parent._getobj()
            if hasattr(module, '_pytest_yaml_raw'):
                raw_dict = module._pytest_yaml_raw

                # 获取config级别的runtime
                config_mark = raw_dict.get('config', {}).get('mark', '')
                if isinstance(config_mark, str):
                    if config_mark.startswith('runtime('):
                        try:
                            config_runtime = float(config_mark.split('(')[1].split(')')[0])
                        except (IndexError, ValueError):
                            pass
                elif isinstance(config_mark, list):
                    for mark in config_mark:
                        if isinstance(mark, str) and mark.startswith('runtime('):
                            try:
                                config_runtime = float(mark.split('(')[1].split(')')[0])
                                break
                            except (IndexError, ValueError):
                                pass

                # 获取case级别的runtime
                case_name = item.originalname or item.name
                case_value = raw_dict.get(case_name)
                if case_value:
                    if isinstance(case_value, list):
                        case_data = case_value[0] if len(case_value) > 0 and isinstance(case_value[0], dict) else {}
                    else:
                        case_data = case_value if isinstance(case_value, dict) else {}

                    # 处理mark标记
                    case_mark = case_data.get('mark', '')
                    if isinstance(case_mark, list):
                        # 如果是列表类型，查找runtime标记
                        for mark in case_mark:
                            if isinstance(mark, str) and mark.startswith('runtime('):
                                try:
                                    case_runtime = float(mark.split('(')[1].split(')')[0])
                                    break
                                except (IndexError, ValueError):
                                    pass
                    elif isinstance(case_mark, str):
                        # 支持逗号分隔的多个标记
                        marks = [m.strip() for m in case_mark.split(',')]
                        for mark in marks:
                            if mark.startswith('runtime('):
                                try:
                                    case_runtime = float(mark.split('(')[1].split(')')[0])
                                    break
                                except (IndexError, ValueError):
                                    pass
                    elif isinstance(case_mark, dict):
                        # 处理字典形式的mark
                        runtime_value = case_mark.get('runtime')
                        if runtime_value is not None:
                            try:
                                case_runtime = float(runtime_value)
                            except ValueError:
                                pass
        log.debug(
            f'{config_runtime=}, {case_runtime=}, {cmd_runtime=}, {ini_runtime=}, actual_runtime={round(report.duration, 6)}')

        # 优先级：用例级别 > config级别 > pytest.ini > 命令行参数
        runtime_threshold = case_runtime or config_runtime or ini_runtime or cmd_runtime

        if runtime_threshold and report.duration > runtime_threshold:
            log.debug(f'\n{item} cost {round(report.duration, 3)}s more than expected {round(runtime_threshold, 3)}s\n')
            report.outcome = "failed"


def pytest_cmdline_main(config):
    if config.option.start_project:
        create_start_project(config)
        return 0
