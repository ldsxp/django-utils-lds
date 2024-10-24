import os
import sys
import random


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
