﻿import os
import sys

from setuptools import setup, find_packages

from djlds.versions import version

"""
pip install -U spider-utils
pip --no-cache-dir install -U spider-utils

# 检查错误
# twine check dist/*

echo 使用 twine 上传到官方的pip服务器:
echo 在系统添加 TWINE_USERNAME 和 TWINE_PASSWORD 变量，不用输入用户名和密码
echo 例如 TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJD...

rmdir /S/Q build
rmdir /S/Q dist
python setup.py sdist bdist_wheel
echo 上传到PyPI:
twine upload dist/*

"""

# twine upload dist/* 使用 twine 上传
# 添加上传到 PyPI 的命令
# 设置 TWINE_USERNAME=lds 和 TWINE_PASSWORD 变量，但不建议设置到系统里面
# 勾选：Emulate terminal in output console(在输出控制台中模拟终端)
if sys.argv[-1] == 'up':
    # os.system('rm -rf dist')
    # os.system('rm -rf build')
    os.system('rmdir /S/Q build')
    os.system('rmdir /S/Q dist')
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine check dist/*')
    os.system('twine upload dist/*')
    sys.exit()
elif sys.argv[-1] == 'dev':
    os.system('pip install wheel')
    os.system('pip install twine')
    sys.exit()

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    # 名称
    name="djlds",
    # 版本
    version=version,
    # version=".".join(map(str, __import__('html2text').__version__)),
    # 关键字列表
    keywords=("django", "utils"),
    # 简单描述
    description="常用 Django 功能集合，为了多平台，多电脑调用方便!",
    # 详细描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 授权信息
    license="GNU GPL 3",

    # 官网地址
    url="https://github.com/ldsxp/django-utils-lds",
    # 程序的下载地址
    download_url="https://pypi.org/project/django-utils-lds",
    # 作者
    author="lds",
    # 作者的邮箱地址
    author_email="85176878@qq.com",

    # 需要处理的包目录（包含__init__.py的文件夹）
    packages=find_packages('.', exclude=['tests', 'tests.*']),
    # 软件平台列表
    platforms="any",
    # 所属分类列表
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    # 需要安装的依赖包
    install_requires=[
        'ilds',
        'colorama',
        'django-admin-generator>=2.6.0',
        'Django',
    ],
    include_package_data=True,
    extras_require={'dev': ['wheel', 'twine', ]},
    python_requires='>=3.6',

    zip_safe=False
)
