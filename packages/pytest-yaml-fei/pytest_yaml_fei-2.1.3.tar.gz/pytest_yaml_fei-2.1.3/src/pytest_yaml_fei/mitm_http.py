import json
import os
from mitmproxy import ctx
from pathlib import Path
import yaml
from urllib.parse import urlparse
import re
from .log import log


class RecoderHTTP:
    """HTTP 录制器，将请求转换为 YAML 测试用例"""

    def __init__(self, filter_host=None, ignore_cookies=False, save_base_url=False, save_case_dir='cases'):
        """
        初始化录制器
        :param filter_host: 需要过滤的域名列表，如 ['http://example.com']
        :param ignore_cookies: 是否忽略 cookies
        :param save_base_url: 是否保存 base_url 到 pytest.ini
        :param save_case_dir: 保存用例的目录
        """
        self.filter_host = filter_host or []
        self.ignore_cookies = ignore_cookies
        self.save_base_url = save_base_url
        self.save_case_dir = save_case_dir
        self._ensure_case_dir()

    def _ensure_case_dir(self):
        """确保用例保存目录存在"""
        if not os.path.exists(self.save_case_dir):
            os.makedirs(self.save_case_dir)

    def _should_record(self, flow):
        """判断是否需要记录该请求"""
        if not self.filter_host:
            return True

        url = flow.request.pretty_url
        return any(host in url for host in self.filter_host)

    def _get_base_url(self, url):
        """获取 base_url"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _clean_url(self, url, base_url):
        """清理 URL，移除 base_url 部分"""
        return url.replace(base_url, "")

    def _get_test_name(self, flow):
        """生成测试用例名称"""
        path = urlparse(flow.request.pretty_url).path
        method = flow.request.method.lower()
        name = re.sub(r'[^a-zA-Z0-9]', '_', path.strip('/'))
        return f"test_{method}_{name}"

    def _extract_request_data(self, flow):
        """提取请求数据"""
        request = {
            "method": flow.request.method,
            "headers": dict(flow.request.headers)
        }

        # 处理请求体
        if flow.request.content:
            content_type = flow.request.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    request["json"] = json.loads(flow.request.content.decode('utf-8'))
                except:
                    request["data"] = flow.request.content.decode('utf-8')
            else:
                request["data"] = flow.request.content.decode('utf-8')

        return request

    def _create_validate(self, flow):
        """创建验证规则"""
        validate = [
            {"eq": ["status_code", flow.response.status_code]}
        ]

        content_type = flow.response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            validate.append({
                "eq": ['headers."Content-Type"', "application/json"]
            })

        return validate

    def request(self, flow):
        """请求事件处理"""
        if not self._should_record(flow):
            return

    def response(self, flow):
        """响应事件处理"""
        if not self._should_record(flow):
            return

        base_url = self._get_base_url(flow.request.pretty_url)
        test_name = self._get_test_name(flow)

        # 构建测试用例
        request_data = self._extract_request_data(flow)
        request_data["url"] = self._clean_url(flow.request.pretty_url, base_url)

        test_case = {
            "config": {
                "base_url": base_url
            },
            test_name: {
                "request": request_data,
                "validate": self._create_validate(flow)
            }
        }

        # 保存测试用例
        case_path = os.path.join(self.save_case_dir, f"{test_name}.yml")
        with open(case_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_case, f, allow_unicode=True, default_flow_style=False)

        log.info(f"Generated test case: {case_path}")

        # 保存 base_url 到 pytest.ini
        if self.save_base_url:
            self._save_base_url(base_url)

    def _save_base_url(self, base_url):
        """保存 base_url 到 pytest.ini"""
        ini_content = "[pytest]\nlog_client =  = true\nbase_url = " + base_url + "\n"
        with open("pytest.ini", "w", encoding='utf-8') as f:
            f.write(ini_content)
