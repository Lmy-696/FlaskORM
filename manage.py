import os
from app import creat, models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = creat()
manage = Manager(app)
migrate = Migrate(app, models)  # 安装数据库管理插件
app.secret_key = '123456'

manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manage.run()
