import wtforms
from flask_wtf import FlaskForm
from wtforms import validators

from wtforms import ValidationError

def keywords_valid(form,field):
    '''
    :param form: 表单
    :param field: 字段   均不主动传参
    '''
    data=field.data#获取input内容（value）
    keywords=['admin','管理员']
    if data in keywords:
        raise ValidationError('不可以用敏感词命名')




class TaskForm(FlaskForm):
    name=wtforms.StringField(
        label='name',
        render_kw={
            'class':'form-control',
            'placeholder':'任务名称'
        },
        validators=[
            validators.DataRequired('名字不可以为空'),
            keywords_valid#关键词拦截
        ]
    )
    description=wtforms.TextField(
        label='description',
        render_kw={
            'class':'form-control',
            'placeholder':'任务描述'
        },
        validators=[
            validators.EqualTo('name')  # 检测与name输入的是否一致
        ]
    )
    time=wtforms.StringField(
        label='time',
        render_kw={
            'class':'form-control',
            'placeholder':'任务时间'
        }
    )
    public=wtforms.StringField(
        label='public',
        render_kw={
            'class':'form-control',
            'placeholder':'任务发布人'
        }
    )