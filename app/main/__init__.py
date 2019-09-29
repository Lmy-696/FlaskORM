from flask import Blueprint
main=Blueprint('main',__name__)#创建蓝图
from . import views#执行此导入后，会执行整个views里的视图

