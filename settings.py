import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATICFILES_DIR = os.path.join(BASE_DIR,'static')

'''类对象'''
class Config:
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'ORM.sqlite')
    SQLAlCHEMY_COMMIT_ON_TEARDOWN = True  # 请求结束后自动提交
    SQLAlCHEMY_RTACK_MODIFICATIONS = True  # 跟踪修改

class RunConfig(Config):
    DEBUG = False