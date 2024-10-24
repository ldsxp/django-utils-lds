import os
import sys
import subprocess
from importlib import import_module

VERSION = '3.1'

CONFIG = {
    'USERNAME': os.getenv('USERNAME', 'lds'),
    'EMAIL': os.getenv('EMAIL', '85176878@qq.com'),
    'SCRIPTS_PATH': os.getenv('SCRIPTS_PATH', r'D:\Envs\lds_mysite_310\Scripts'),
    'BACKUP_DIR': 'backup',
    'DJANGO_SETTINGS_MODULE': os.getenv('DJANGO_SETTINGS_MODULE', 'mysite.settings'),
    'SERVER_ADDRESS': '127.0.0.1',
    'SERVER_PORT': '8100'
}


def run_command(command, capture_output=False, show_command=True):
    if show_command:
        print(f'运行命令：{command}')
    result = subprocess.run(command, shell=True, text=True, capture_output=capture_output)
    if capture_output:
        return result.stdout.strip() if result.returncode == 0 else None
    return result.returncode == 0


class DjangoTool:

    def __init__(self, config):
        self.config = config
        self.working_dir = os.getcwd()
        self.python = os.path.join(self.config['SCRIPTS_PATH'], 'python.exe')
        self.actions = {
            'r': self.runserver,
            's': self.create_app,
            '1': self.create_user,
            '2': self.check_db,
            '3': self.create_db,
            'b': self.dbbackup,
            'x': self.dbrestore,
            'm': self.mediabackup,
            'a': self.mediarestore,
            'e': self.export_requirements,
            'i': lambda: self.import_requirements("requirements.txt"),
            'd': lambda: self.import_requirements("requirements_dev.txt"),
        }

    def set_cmd_title(self, title):
        if os.name == 'nt':
            os.system(f'title {title}')
        else:
            sys.stdout.write(f'\33]0;{title}\a')
            sys.stdout.flush()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def pause(self, message="按回车返回菜单..."):
        input(message)

    def list_backup_files(self):
        if not os.path.exists(self.config['BACKUP_DIR']):
            print(f"备份目录 '{self.config['BACKUP_DIR']}' 不存在！")
            return []
        return [f for f in os.listdir(self.config['BACKUP_DIR']) if os.path.isfile(os.path.join(self.config['BACKUP_DIR'], f))]

    def get_databases_from_settings(self):
        sys.path.append(self.working_dir)
        try:
            settings = import_module(self.config['DJANGO_SETTINGS_MODULE'])
            return list(settings.DATABASES.keys()), settings.DATABASES
        except Exception as e:
            print(f"加载Django设置时出错: {e}")
            return [], {}

    def ensure_virtual_env(self):
        if not os.path.exists(self.config['SCRIPTS_PATH']):
            print(f"Django Tool {VERSION} 版")
            print(f"虚拟环境的路径不存在，请修正文件路径（{self.config['SCRIPTS_PATH']}）或新建虚拟环境。")
            input("将退出命令行工具，按回车退出...")
            exit()

    def ensure_manage_py(self):
        if not os.path.exists(os.path.join(self.working_dir, 'manage.py')):
            print("错误: manage.py 没找到。请在Django项目根目录中运行此脚本。")
            sys.exit(1)

    def get_version_info(self):
        python_version = run_command(f"{self.python} --version", capture_output=True, show_command=False)
        django_version = run_command(f"{self.python} -m django --version", capture_output=True, show_command=False)
        return python_version, django_version

    def print_menu(self):
        self.clear_screen()
        print('')
        print(f"  Django Tool {VERSION}")
        print(f"  使用环境：{self.config['SCRIPTS_PATH']}\\activate.bat")
        print(f"  工作目录：{self.working_dir}")
        print("\n   选项   菜单\n")
        print("   [r]    启动服务器")
        print("   [s]    创建应用程序")
        print("   [1]    创建管理员")
        print("   [2]    检查迁移")
        print("   [3]    迁移数据")
        print("   [b]    备份数据库 (dbbackup)")
        print("   [x]    恢复数据库 (dbrestore)")
        print("   [m]    备份媒体文件 (mediabackup)")
        print("   [a]    还原媒体文件 (mediarestore)")
        print("   [e]    导出 requirements.txt")
        print("   [i]    安装 requirements.txt")
        print("   [d]    安装 requirements_dev.txt")
        print("\n   输入其他任意内容退出...\n")

    def select_choice(self):
        return input("请输入 [] 内的选项，按回车：").strip().lower()

    def execute_action(self, action):
        if action:
            action()
        else:
            print("选择无效，将退出...")

    def runserver(self):
        print(f"\n启动服务器，管理地址：{self.config['SERVER_ADDRESS']}:{self.config['SERVER_PORT']}/admin\n")
        run_command(f"{self.python} manage.py runserver {self.config['SERVER_ADDRESS']}:{self.config['SERVER_PORT']}")

    def create_app(self):
        app_name = input("输入应用程序的名称：").strip()
        if app_name:
            run_command(f"{self.python} manage.py startapp {app_name}")

    def create_user(self):
        run_command(f"{self.python} manage.py migrate")

        input_username = input(f"输入用户名（默认值：{self.config['USERNAME']}）：").strip() or self.config['USERNAME']
        input_email = input(f"输入邮箱（默认值：{self.config['EMAIL']}）：").strip() or self.config['EMAIL']

        print(f"\n将使用用户名：{input_username} 和邮箱：{input_email}\n")
        run_command(f"{self.python} manage.py createsuperuser --username={input_username} --email={input_email}")

    def check_db(self):
        run_command(f"{self.python} manage.py check")

    def create_db(self):
        app_name = input("为应用程序迁移：").strip()
        if app_name:
            run_command(f"{self.python} manage.py makemigrations {app_name}")
        else:
            run_command(f"{self.python} manage.py makemigrations")
        run_command(f"{self.python} manage.py migrate")
        print("\n迁移数据完成\n")

    def dbbackup(self):
        print("\n备份数据库\n")
        if run_command(f"{self.python} manage.py dbbackup"):
            print("\n数据库备份完成\n")
        else:
            print("\n数据库备份失败\n")

    def dbrestore(self):
        print("\n恢复数据库\n")

        databases, db_settings = self.get_databases_from_settings()
        if not databases:
            print("没有找到数据库！")
            return

        print("可用的数据库：")
        for i, db in enumerate(databases):
            print(f"  [{i}] {db}")

        db_choice = input("请输入要恢复的数据库编号（默认选择[0]）：").strip()
        db_choice = int(db_choice) if db_choice.isdigit() and 0 <= int(db_choice) < len(databases) else 0
        database = databases[db_choice]

        backup_files = self.list_backup_files()
        if not backup_files:
            print("没有找到备份文件！")
            return

        print("可用的备份文件：")
        for i, filename in enumerate(backup_files):
            print(f"  [{i}] {filename}")

        file_choice = input("请输入备份文件的编号进行恢复（默认选择[0]）：").strip()
        file_choice = int(file_choice) if file_choice.isdigit() and 0 <= int(file_choice) < len(backup_files) else 0

        if input("是否需要清空数据库？(y/n，默认n)：").strip().lower() == 'y':
            self.clear_and_migrate_database(database, db_settings)

        if run_command(f"{self.python} manage.py dbrestore -i \"{backup_files[file_choice]}\" --database={database}"):
            print(f"\n已从文件 '{backup_files[file_choice]}' 恢复数据库 '{database}'\n")
        else:
            print(f"\n数据库 {backup_files[file_choice]} 恢复失败\n")

    def clear_and_migrate_database(self, database, db_settings):
        print("清空数据库中...")
        db_setting = db_settings[database]
        if db_setting['ENGINE'] == 'django.db.backends.sqlite3':
            db_path = db_setting['NAME']
            if os.path.exists(db_path):
                os.remove(db_path)
            print("已删除SQLite数据库文件。")
        else:
            if not run_command(f"{self.python} manage.py flush --no-input --database={database}"):
                print("\n清空数据库失败，请手动处理。\n")

        print("重新迁移数据库中...")
        if not run_command(f"{self.python} manage.py migrate --database={database}"):
            print("\n数据库迁移失败，请手动处理。\n")

    def mediabackup(self):
        print("\n备份媒体文件\n")
        if run_command(f"{self.python} manage.py mediabackup"):
            print("\n媒体文件备份完成\n")
        else:
            print("\n媒体文件备份失败\n")

    def mediarestore(self):
        print("\n恢复媒体文件\n")
        backup_files = self.list_backup_files()
        if not backup_files:
            print("没有找到备份文件！")
            return

        print("可用的备份文件：")
        for i, filename in enumerate(backup_files):
            print(f"  [{i}] {filename}")

        file_choice = input("请输入备份文件的编号进行恢复（默认选择[0]）：").strip()
        file_choice = int(file_choice) if file_choice.isdigit() and 0 <= int(file_choice) < len(backup_files) else 0

        if run_command(f"{self.python} manage.py mediarestore -i \"{backup_files[file_choice]}\""):
            print(f"\n已从文件 '{backup_files[file_choice]}' 恢复媒体文件\n")
        else:
            print(f"\n媒体文件 {backup_files[file_choice]} 恢复失败\n")

    def export_requirements(self):
        run_command(f"{os.path.join(self.config['SCRIPTS_PATH'], 'pip.exe')} freeze > requirements.txt")
        print("\n导出 requirements.txt 完成\n")

    def import_requirements(self, requirements_file):
        use_custom_mirror = input("是否使用 https://pypi.douban.com/simple/ 进行安装？(y/n, 默认n)：").strip().lower() == 'y'
        command = f"{os.path.join(self.config['SCRIPTS_PATH'], 'pip.exe')} install -r {requirements_file}"
        if use_custom_mirror:
            command += " -i https://pypi.douban.com/simple/"
        run_command(command)
        print(f"\n安装 {requirements_file} 完成\n")

    def menu(self):
        while True:
            self.print_menu()
            choice = self.select_choice()
            action = self.actions.get(choice)
            self.execute_action(action)

            if not action:
                break
            self.pause()

    def run(self):
        python_version, django_version = self.get_version_info()
        self.set_cmd_title(f"Django 管理工具 {VERSION} [{python_version}] [Django {django_version}]")
        self.ensure_virtual_env()
        self.ensure_manage_py()
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', self.config['DJANGO_SETTINGS_MODULE'])
        self.menu()


def main(config):
    check_config = [key for key in CONFIG.keys() if key not in config]
    if check_config:
        raise ValueError(f'config 中缺少设置内容:{check_config}')
    dt = DjangoTool(config)

    dt.run()


if __name__ == "__main__":
    main(CONFIG)

# 下面是 djt.py 示例：
"""
import os
import sys
import subprocess

CONFIG = {
    'USERNAME': os.getenv('USERNAME', 'lds'),
    'EMAIL': os.getenv('EMAIL', '85176878@qq.com'),
    'SCRIPTS_PATH': os.getenv('SCRIPTS_PATH', r'D:\Envs\lds_mysite_310\Scripts'),
    'BACKUP_DIR': 'backup',
    'DJANGO_SETTINGS_MODULE': os.getenv('DJANGO_SETTINGS_MODULE', 'mysite.settings'),
    'SERVER_ADDRESS': '127.0.0.1',
    'SERVER_PORT': '8100'
}


def execute_script_with_alternative_python(required_python_path):
    required_python_executable = os.path.join(required_python_path, 'python.exe')
    if os.path.normcase(os.path.normpath(required_python_executable)) != os.path.normcase(os.path.normpath(sys.executable)):
        print(f"当前 Python 路径“{sys.executable}”与所需路径“{required_python_executable}”不同")
        print(f"切换到 Python: {required_python_executable}")
        subprocess.run([required_python_executable, sys.argv[0]], check=True)
        sys.exit()


def main():
    # 确保使用正确的 Python 路径
    execute_script_with_alternative_python(CONFIG['SCRIPTS_PATH'])
    from djlds.tool import main as djlds_main
    djlds_main(CONFIG)


if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(f"运行错误: {e}")
        input('输入任意字符退出...')
"""
