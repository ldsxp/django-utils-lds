__package_name__ = 'django-admin-generator'
__version__ = '2.2.0'
__author__ = 'Rick van Hattem'
__author_email__ = 'Wolph@Wol.ph'
__description__ = ' '.join(('''
Django Admin Generator 是一个管理命令，用于为给定的应用程序/模型自动生成 Django `admin.py` 文件。
Usage
为给定应用程序生成 admin.py：
./manage.py admin_generator APP_NAME >> APP_NAME/admin.py

要使用给定的应用程序（以用户开头）为所有模型生成管理员，请执行以下操作：
./manage.py admin_generator APP_NAME ‘^user’ >> APP_NAME/admin.py
'''.strip().split()))
__url__ = 'https://github.com/WoLpH/django-admin-generator/'

