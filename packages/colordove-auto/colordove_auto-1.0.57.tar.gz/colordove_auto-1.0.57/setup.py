# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='colordove_auto',  # 包的名字
    version='1.0.57',  # 包的版本
    packages=find_packages(),  # 自动寻找包中的模块
    install_requires=[  # 依赖的其他包
        'beautifulsoup4==4.13.4',
        'blinker==1.4',
        'chardet==5.2.0',
        'flask==2.0.3',
        'mitmproxy==8.0.0',
        'openpyxl==3.1.5',
        'pandas==2.0.3',
        'pika==1.3.2',
        'psutil==5.8.0',
        'pyotp==2.4.0',
        'pytz==2025.2',
        'selenium==4.27.1',
        'undetected-chromedriver==3.5.5',
        'werkzeug==2.0.3',
        'xlrd==2.0.2',
    ],
    author='Zhongshuizhou',
    author_email='zhongshuizhou@qq.com',
    description='Cross border e-commerce automation program',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://www.colordove.com',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',  # 支持的Python版本
    entry_points = {
        'console_scripts': [
            'colordove_auto = colordove_auto.main:main', # 设置命令行工具的入口
        ],
    }
)
