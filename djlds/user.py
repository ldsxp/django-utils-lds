# ---------------------------------------
#   程序：user.py
#   版本：0.2
#   作者：lds
#   日期：2022-01-21
#   语言：Python 3.X
#   说明：django 用户相关的函数集合
# ---------------------------------------

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password  # , check_password

User = get_user_model()


def create_user(username, email, password, is_superuser=False, is_staff=True, is_active=True):
    """
    创建用户

    例子：
    from ilds.django.user import create_user
    create_user(username='admin', email='admin@qq.com', password='123456', is_superuser=False, is_staff=True)

    :param username: 用户名
    :param email: 邮箱
    :param password: 密码，支持直接设置秘钥，秘钥前缀是 pbkdf2_
    :param is_superuser: 是否是超级用户
    :param is_staff: 用户是否可以登录到管理站点
    :param is_active: 用户是否被认为是活跃的。可以用来代替删除帐号
    :return: 创建成功的用户
    """
    if not password.startswith('pbkdf2_'):
        password = make_password(password)

    # 添加一个超级用户数据
    add_user = User.objects.create(**{
        'password': password,
        'last_login': None,
        'is_superuser': is_superuser,
        'username': username,
        'email': email,
        'is_staff': is_staff,
        'is_active': is_active
    })

    try:
        from allauth.account.models import EmailAddress  # django-allauth
        EmailAddress.objects.create(**{
            'user': add_user,
            'email': email,
            'verified': True,
            'primary': True})
    except Exception as e:
        print(e)

    return add_user


def add_superuser(username, email, password):
    """
    添加超级管理员用户

    例子：
    from ilds.django.user import add_superuser
    add_superuser(username='admin', email='admin@qq.com', password='123456')

    :param username: 用户名
    :param email: 邮箱
    :param password: 密码，支持直接设置秘钥，秘钥前缀是 pbkdf2_
    :return: 创建成功的用户
    """
    return create_user(username, email, password, is_superuser=True, is_staff=True, is_active=True)
