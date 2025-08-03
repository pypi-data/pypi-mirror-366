# -*- coding: utf-8 -*-
"""
 @Author: xiaoxuan6
 @Date: 2025/8/3 14:06
 @File: setup.py.py
 @Description: 
"""
from setuptools import setup, find_packages

setup(
    name='captcha_operation',
    version='0.0.2',
    description='数字运算验证码',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='xiaoxuan6',
    url='https://github.com/xiaoxuan6/captcha_operation',
    packages=['captcha_operation'],
    install_requires=[
        'ddddocr',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.12",
        'License :: OSI Approved :: MIT License',
    ],
    keywords=['number operation captcha'],
    python_requires='>=3.12',
    zip_safe=True
)
