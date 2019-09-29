from app import models


class BaseModel(models.Model):
    __abstract__ = True  # 声明当前类是抽象类，被继承调用不被创建
    id = models.Column(models.Integer, primary_key=True, autoincrement=True)

    def save(self):
        db = models.session()
        db.add(self)
        db.commit()

    def delete(self):
        db = models.session()
        db.delete(self)
        db.commit()


# 课程
class Curriculum(BaseModel):
    __tablename__ = 'curriculum'  # 表名
    # id = models.Column(models.Integer, primary_key=True)
    c_id = models.Column(models.String(32))
    c_name = models.Column(models.String(32))
    c_time = models.Column(models.Date)


class User(BaseModel):
    __tablename__ = 'user'
    user_name = models.Column(models.String(32))
    password = models.Column(models.String(32))
    email = models.Column(models.String(32))


# 请假条
class Leave(BaseModel):
    __tablename__ = 'leave'
    leave_id = models.Column(models.Integer)  # 请假人id
    leave_name = models.Column(models.String(32))  # 请假人姓名
    leave_type = models.Column(models.String(32))  # 请假类型
    leave_start_time = models.Column(models.String(32))  # 请假开始时间
    leave_end_time = models.Column(models.String(32))  # 请假结束时间
    leave_phone = models.Column(models.String(32))  # 请假人电话
    leave_status = models.Column(models.String(32))  # 请假状态  0请假、1批准、2驳回、3销假
    leave_description = models.Column(models.Text)  # 请假事由

class Picture(BaseModel):
    __tablename__ = 'picture'
    picture=models.Column(models.String(64))
    type=models.Column(models.String(32))

# models.create_all()  # 创表（同步）
