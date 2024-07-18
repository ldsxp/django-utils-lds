# ---------------------------------------
#   程序：util.py
#   版本：0.3
#   作者：lds
#   日期：2020-02-27
#   语言：Python 3.X
#   说明：常用的函数集合
# ---------------------------------------

import os
import sys
import random

from colorama import Fore, Back, Style

# 最后修改时间：20190929
CLEAN_STR = "	", " ", "(", ")", "（", "）", " ", "|", "/", "+", "&", "•", "；", " ", "＆", "　", "<", ">" \
    , "、", "\n", "\"", "?", "？", "*", ",", "《", "》", "-", "×", "."


def django_setup(project_name=None, site_path=None):
    """
    设置 Django 运行环境
    
    https://stackoverflow.com/questions/8047204/django-script-to-access-model-objects-without-using-manage-py-shell

    from ilds.django.util import django_setup
    django_setup(r'mysite', site_path=None)
    """

    if site_path is not None:
        sys.path.insert(0, site_path)

    if project_name is None:
        project_name = os.path.split(os.path.dirname(__file__))[-1]
    print('项目：', project_name)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{}.settings".format(project_name))
    try:
        import django
        django.setup()
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            f"\n\n{e}\n\n注：如果提示 ModuleNotFoundError: No module named 'django'，请安装 django: pip install django")


def random_key():
    """
    生成 Django 使用的 SECRET_KEY

    from ilds.django.util import random_key
    print(random_key())
    """

    return ''.join(
        [random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])


def prompt_list(in_list, title='选择内容：', text='输入序号：'):
    """
    命令行选择列表内容的交互提示
    选择列表内容，输入 e 返回 None
    """
    print(Fore.BLUE + title)
    for i, v in enumerate(in_list):
        print(Fore.RED + f'({i}):', Fore.GREEN + str(v))
    ret = None
    while True:
        input_str = input(Fore.YELLOW + text)
        # print(input_str, type(input_str), int(input_str))
        if input_str == 'e':
            break
        try:
            ret = in_list[int(input_str)]
            break
        except:
            continue
    print(Style.RESET_ALL)
    return ret


def confirm_yes_no(title='是否确认继续...', text='输入 y 确认，其他任意字符表示取消'):
    """
    命令行选择列表内容的交互提示
    输入 y 返回 True，其他任意字符 返回 False
    """
    print(Fore.RED + title)
    print(Fore.YELLOW + text)
    input_str = input(Fore.BLUE + '请输入选择：')
    ret = False
    if input_str.lower() == 'y':
        ret = True

    print(Style.RESET_ALL)
    return ret
