from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pytest-yaml-fei",
    version="2.1.2",
    author="Fei Wu",
    url='https://gitee.com/fei/pytest-yaml-fei.git',
    author_email="504294190@qq.com",
    description="a pytest yaml allure package",
    license='MIT License',  # 许可协议
    install_requires=['Jinja2', 'jmespath', 'jsonpath', 'pytest<=8.3.5', 'PyYAML', 'requests', 'allure-pytest', 'pymysql',
                      'DingtalkChatbot', 'faker', 'requests-toolbelt', 'redis', 'mitmproxy'],
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    entry_points={
        "pytest11": ['pytest = pytest_yaml_fei.plugin']
    },
    classifiers=[
        "Framework :: Pytest",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',  # 对python的最低版本要求
)
