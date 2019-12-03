import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, DateField, IntegerField
from wtforms.validators import DataRequired, ValidationError


def phone_required(self, field):
    """ 自定义的验证 """
    username = field.data
    # 强制用户名为手机号码
    pattern = r'^1[0-9]{10}$'
    if not re.search(pattern, username):
        raise ValidationError('请输入手机号码')
    return field


class LoginForm(FlaskForm):
    """ 用户登录 """
    username = StringField(label='用户名')
    password = PasswordField(label='密码')

    submit = SubmitField('登陆')


class UserForm(FlaskForm):
    """ 新增用户 """

    def __init__(self, csrf_enabled, *args, **kwargs):
        super().__init__(csrf_enabled=csrf_enabled, *args, **kwargs)


    username = StringField(label='用户名', validators=[phone_required])
    password = PasswordField(label='密码')

    birth_date = DateField(label='生日', validators=[DataRequired('请输入生日')])
    age = IntegerField(label='年龄')

    submit = SubmitField('新增')


class UserAvatarForm(FlaskForm):
    """ 用户头像 """
    avatar = FileField(label='上传头像', validators=[
        FileRequired('请选择图片文件'),
        FileAllowed(['jpg', 'png'], '仅支持jpg和png格式'),
    ])