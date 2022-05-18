# ---------------------------------------
#   程序：timezone.py
#   版本：0.1
#   作者：lds
#   日期：2022-05-18
#   语言：Python 3.X
#   说明：常用的函数集合
# ---------------------------------------

from django.utils.timezone import localtime, now


def get_local_now(format_string='%Y-%m-%d %H:%M:%S'):
    """
    获取本地的当前时间
    """
    return localtime(now()).strftime(format_string)
