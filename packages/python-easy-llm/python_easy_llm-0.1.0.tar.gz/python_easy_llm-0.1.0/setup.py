from setuptools import setup, find_packages

setup(
    name="python-easy-llm",  # 包的名称
    version="0.1.0",  # 包的版本
    packages=find_packages(where="src"),  # 自动找到 src 目录下的包
    package_dir={"": "src"},  # 包的根目录
    install_requires=[
        # 依赖的包，例如：
        "openai",  
        "jinja2",  
    ],
    include_package_data=True,  
    long_description=open('README.md').read(),  # 从 README.md 获取包描述
    long_description_content_type="text/markdown",  # 设置 README 文件的类型
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # 支持的 Python 版本
)
