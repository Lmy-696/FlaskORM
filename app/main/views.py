import os
import json
import hashlib
import random
import datetime
import functools

from flask import jsonify
from flask import session
from flask import request, render_template, redirect

# from main import csrf
from app.models import *
from . import main
from .forms import TaskForm
from app import api
from flask_restful import Resource


class Calendar:
    def __init__(self, year=datetime.datetime.now().year, month=datetime.datetime.now().month):
        assert int(month) <= 12
        date = datetime.datetime(year, month, 1, 0, 0)
        self.month_days = list(self.back_days(year, month))#当月天数
        self.first_day = date.weekday()  # 0 周一 6 周日
        self.work=['python','php','mysql','html']

    def first_line(self, first_day, month_days):  # 每月第一行
        fl = [{month_days.pop(0):random.choice(self.work)} for i in range(7 - first_day)]
        [fl.insert(0, 'null') for i in range(7 - len(fl))]
        return fl

    def back_days(self, year, month):
        big_month = [1, 3, 5, 7, 8, 10, 12]
        small_month = [4, 6, 9, 11]
        two_month = 28
        if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
            two_month = 29
        if month in big_month:
            return range(1, 32)
        elif month in small_month:
            return range(1, 31)
        else:
            return range(1, two_month + 1)

    def return_calendar(self):
        fl = self.first_line(self.first_day, self.month_days)
        lines = [fl]
        while self.month_days:
            line = []
            for i in range(7):
                if self.month_days:
                    line.append({self.month_days.pop(0):random.choice(self.work)})
                else:
                    line.append('null')
            lines.append(line)
        return lines


class Paging:
    '''
    通过sqlalachemy查询进行分页
    offset偏移，开始查询的位置
    limit 单页条数
    分页需要：页码、分页数据、是否第一页、是否最后一页
    '''

    def __init__(self, data, page_size):
        '''

        :param data: 分页的数据
        :param page_size: 每页的条数
        '''
        self.data = data
        self.page_size = page_size
        self.is_start = False
        self.is_end = False
        self.page_count = len(data)
        self.previous_page = 0  # 上一页
        self.next_page = 0  # 下一页
        self.page_number = self.page_count / page_size
        if self.page_number == int(self.page_number):
            self.page_number = int(self.page_number)
        else:
            self.page_number = int(self.page_number) + 1
        self.page_range = range(1, self.page_number + 1)  # 页码范围

    def page_data(self, page):
        '''
        返回分页数据
        :param page:页码
        :return:
        '''
        self.next_page = int(page) + 1
        self.previous_page = int(page) - 1
        if page <= self.page_range[-1]:
            page_start = (page - 1) * self.page_size
            page_end = page * self.page_size
            data = self.data[page_start:page_end]
            if page == 1:
                self.is_start = True
            else:
                self.is_start = False
            if page == self.page_range[-1]:
                self.is_end = True
            else:
                self.is_end = False
        else:
            data = ['没有数据']
        return data


import functools


def loginVaild(fun):
    @functools.wraps(fun)
    def inner(*args, **kwargs):
        username = request.cookies.get('username')
        id = request.cookies.get('id', '0')
        user = User.query.get(str(id))
        session_username = session.get('username')
        if user:
            if user.user_name == username and username == session_username:
                return fun(*args, **kwargs)
            else:
                return redirect('/login/')
        else:
            return redirect('/login/')

    return inner


@main.route('/')  # 路由
def index():  # 视图
    return 'hello world'


@main.route('/base/')
def base():
    return render_template('base.html', **locals())



def setPassword(password):
    # md5 = hashlib.md5()
    # md5.update(password.encode())
    # result = md5.hexdigest()
    result = hashlib.md5(password.encode()).hexdigest()
    return result




@main.route('/register/', methods=['GET', 'POST'])
# @csrf.exempt
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        user = User()
        user.user_name = username
        user.password = setPassword(password)
        user.email = email
        user.save()
    return render_template('register.html')


@main.route('/index/')
@loginVaild
# @csrf.exempt
def index_base():
    # c=Curriculum()
    # c.c_name='fff'
    # c.c_id='1'
    # c.c_time=datetime.datetime.now()
    # c.save()
    li = Curriculum.query.all()
    return render_template('index.html', **locals())


@main.route('/login/', methods=['GET', 'POST'])
# @csrf.exempt
def login():
    error = ''
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            db_password = user.password
            password = setPassword(password)
            if password == db_password:
                response = redirect('/index/')
                response.set_cookie('username', user.user_name)
                response.set_cookie('email', user.email)
                response.set_cookie('id', str(user.id))
                session['username'] = user.user_name
                return response
            else:
                error = '密码错误，请重新输入'
        else:
            error = '该用户不存在'

    return render_template('login.html', error=error)


@main.route('/logout/')
# @csrf.exempt
def logout():
    response = redirect('/login/')
    response.delete_cookie('username')
    response.delete_cookie('email')
    response.delete_cookie('id')
    session.pop('username')
    return response


@main.route('/userinfo/')
def userinfo():
    calendar = Calendar().return_calendar()
    today = datetime.datetime.now().day
    return render_template('userinfo.html', **locals())


@main.route('/leave/', methods=['GET', 'POST'])
# @csrf.exempt
def leave():
    if request.method == 'POST':
        data = request.form
        leave_name = data.get('leave_name')
        leave_type = data.get('leave_type')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        phone = data.get('phone')
        leave_description = data.get('leave_description')
        lea = Leave()
        lea.leave_id = request.cookies.get('id')  # 请假人id
        lea.leave_name = leave_name  # 请假人姓名
        lea.leave_type = leave_type  # 请假类型
        lea.leave_start_time = start_time  # 请假开始时间
        lea.leave_end_time = end_time  # 请假结束时间
        lea.leave_phone = phone  # 请假人电话
        lea.leave_status = '0'  # 请假状态
        lea.leave_description = leave_description  # 请假事由
        lea.save()
        return redirect('/leave_list/1/')
    return render_template('leave.html', **locals())


@main.route('/leave_list/<int:page>/')
# @csrf.exempt
def leave_list(page):
    # leaves = Leave.query.offset(0).limit(5)
    leaves = Leave.query.all()
    paging = Paging(leaves, 4)
    page_data = paging.page_data(page)
    return render_template('leave_list.html', **locals())


from flask import jsonify


@main.route('/cancel/', methods=['GET', 'POST'])
# @csrf.exempt
def cancel():
    id = request.form.get('id')  # 通过args接受get请求
    leave = Leave.query.get(int(id))
    leave.delete()
    return jsonify({'data': '删除成功'})  # 返回json值




@main.route('/add_task/', methods=['GET', 'POST'])
# @csrf.exempt
def add_task():
    '''
    print(task.errors)表单校验错误
    print(task.validate_on_submit())判断是否是一个有效的post请求
    print(task.validate())判断是否是一个合法的post请求
    print(task.data)提交的数据
    '''
    errors = ''
    task = TaskForm()
    if request.method == 'POST':
        if task.validate_on_submit():  # 判断是否是一个有效的post请求
            formData = task.data
        else:
            errors_list = list(task.errors.keys())
            errors = task.errors
            print(errors)
    return render_template('add_task.html', **locals())


from settings import STATICFILES_DIR


@main.route('/picture/', methods=['GET', 'POST'])
def picture():
    p = {'picture': 'img/photo.png'}
    if request.method == 'POST':
        file = request.files.get('photo')
        file_name = file.filename
        file_path = 'img/%s' % file_name
        save_path = os.path.join(STATICFILES_DIR, file_path)
        file.save(save_path)
        p = Picture()
        p.picture = file_path
        p.save()
    return render_template('picture.html', p=p)




@api.resource('/Api/leave/')
class LeaveApi(Resource):
    def __init__(self):
        '''定义返回的格式'''
        super(LeaveApi, self).__init__()
        self.result = {
            'version': '1.0',
            'data': ''
        }

    def set_data(self, leave):
        '''定义返回的数据'''
        result_data = {
            'leave_name': leave.leave_name,
            'leave_type': leave.leave_type,
            'leave_start_time': leave.leave_start_time,
            'leave_end_time': leave.leave_end_time,
            'leave_phone': leave.leave_phone,
            'leave_description': leave.leave_description,
        }
        return result_data

    def get(self):
        data = request.args  # 获取请求的数据
        id = data.get('id')  # 获取id
        if id:  # 如果id存在，返回当前id数据
            leave = Leave.query.get(int(id))
            result_data = self.set_data(leave)
        else:  # 如果不存在，返回所有数据
            leaves = Leave.query.all()
            result_data = []
            for leave in leaves:
                result_data.append(self.set_data(leave))
        self.result['data'] = result_data
        return self.result

    def post(self):
        '''post请求，负责保存数据'''
        data = request.form
        leave_id = data.get('leave_id')
        leave_name = data.get('leave_name')
        leave_type = data.get('leave_type')
        leave_start_time = data.get('leave_start_time')
        leave_end_time = data.get('leave_end_time')
        leave_phone = data.get('leave_phone')
        leave_description = data.get('leave_description')

        leave = Leave()
        leave.leave_id = leave_id
        leave.leave_name = leave_name
        leave.leave_type = leave_type
        leave.leave_start_time = leave_start_time
        leave.leave_end_time = leave_end_time
        leave.leave_phone = leave_phone
        leave.leave_description = leave_description
        leave.leave_status = '0'
        leave.save()
        self.result['data'] = self.set_data(leave)
        return self.result

    def put(self):
        data = request.form  # 请求的数据是类字典对象
        id = data.get('id')
        leave = Leave.query.get(int(id))  # 在数据库里找到
        for key, value in data.items():
            if key != 'id':
                setattr(leave, key, value)
        leave.save()
        self.result['data'] = self.set_data((leave))
        return self.result

    def delete(self):
        data = request.form
        id = data.get('id')
        leave = Leave.query.get(int(id))
        leave.delete()
        self.result['data'] = 'id为%s的数据删除成功' % id
        return self.result
