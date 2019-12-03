import os

from flask import Flask, current_app, g, request, session, make_response, render_template, redirect, abort, \
    render_template_string, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import constants
from forms import LoginForm, UserForm, UserAvatarForm

app = Flask(__name__)
# 配置数据库的连接参数
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:abc123456@127.0.0.1/test_flask'
# WTF 表单
# app.config['WTF_SCRF_SECRET_KEY'] = '1234567890poiuytrewqasdfghjklmnbvcxz'
app.config['SECRET_KEY'] = '1234567890poiuytrewqasdfghjklmnbvcxz'
# 文件上传的目录
app.config['UPLOAD_PATH'] = os.path.join(os.path.dirname(__file__), 'medias')
db = SQLAlchemy(app)


class User(db.Model):
    """ 用户信息 """
    __tablename__ = 'weibo_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    age = db.Column(db.Integer, default=0)


class UseeAdress(db.Model):
    """ 用户地址 """
    __tablename__ = 'weibo_user_addr'

    id = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.String(64), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('weibo_user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('address', lazy=True))


@app.before_first_request
def first_request():
    # 第一个请求到来前执行
    print('first_request')


@app.before_request
def before_request():
    # 每次请求到来前执行
    g.user = 'zhangsan'
    print('before_request')


@app.after_request
def after_request(resp):
    print('after_request')
    return resp


@app.route('/helloworld')
def hello_world():
    # 获取 get 请求中的参数
    page = request.args.get('page', None)
    # print(page)
    # get、post 请求中的数据集合
    name = request.values.get('name', None)
    # print(name)

    # 获取请求头
    headers = request.headers
    host = headers.get('host', None)
    # print(host)
    user_agent = headers.get('user-agent')
    # print(user_agent)
    # print(headers)

    # 获取用户请求的 IP 地址
    ip = request.remote_addr
    ru = request.remote_user
    print(ip, ru)

    return 'Hello Worldddddd!'


def index():
    return '欢迎您'


@app.route('/hello/<username>')
def hello(username):
    return f'你好，{username}'


@app.route('/user/')
@app.route('/user/<int:page>')
def page_user(page=None):
    """ 分页操作 """
    # return f'当前页：{page}'
    page_size = 10  # 每页10条数据
    page_data = User.query.paginate(page=page, per_page=page_size)
    return render_template('page_user.html', page_data=page_data)


@app.route('/test')
def test():
    # rest = '页面丢失', 404, {
    #     'user_id': 'abc123',
    # }
    # rest['token'] = 'my token'
    # return rest

    # 构造一个响应对象
    resp = make_response(
        '一个测试页面',
        404,
    )
    resp.headers['token'] = 'my token'
    return resp


@app.route('/html')
def html():
    """ 显示 html 内容 """
    return render_template('test.html')


@app.errorhandler(404)
def not_found(err):
    print(err)
    return '页面不存在'


@app.route('/testing')
def testing():
    # 使用重定向
    # return redirect('/html')

    print('业务逻辑...')
    # 用户 IP 地址黑名单
    ip_list = ['127.0.0.1']
    ip = '127.0.0.1'
    if ip in ip_list:
        abort(403)
    return 'hello，，'


@app.route('/')
def welcome():
    print(url_for('index', _external=True), url_for('mine'))
    return render_template('index.html')


#     html = """
#     <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>index</title>
# </head>
# <body>
#     <h3>欢迎html</h3>
# </body>
# </html>
#     """
#     return render_template_string(html)


@app.route('/m')
def mine():
    return render_template('mine.html')


@app.context_processor
def inject_const():
    return dict({
        'constants': constants,
    })


@app.route('/form')
def page_form():
    """ form表单渲染 """
    form = LoginForm()
    return render_template('form.html', form=form)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    """ 手动添加用户信息 """
    form = UserForm(csrf_enabled=False)
    if form.validate_on_submit():
        # 获取表单数据
        username = form.username.data
        password = form.password.data
        birth_date = form.birth_date.data
        age = form.age.data
        # 保存到数据库
        user = User(username=username,
                    password=password,
                    birth_date=birth_date,
                    age=age)
        db.session.add(user)
        db.session.commit()
        # 提示/跳转
        print('添加成功')
        return redirect(url_for('index'))
    else:
        print('表单验证未通过')
        print(form.errors)
    return render_template('add_user.html', form=form)


@app.route('/img/upload', methods=['GET', 'POST'])
def img_upload():
    """ 图片上传 """
    base_dir = app.config['UPLOAD_PATH']
    if request.method == 'POST':
        # 取文件
        files = request.files
        file1 = files['file1']
        file2 = files['file2']
        # 保存文件
        if file1:
            filename = secure_filename(file1.filename)
            file_name = os.path.join(base_dir, filename)
            file1.save(file_name)
    return render_template('img_upload.html')


@app.route('/avatar/upload', methods=['GET', 'POST'])
def avatar_upload():
    """ 头像上传 """
    form = UserAvatarForm()
    if form.validate_on_submit():
        f = form.avatar.data
        filename = secure_filename(f.filename)
        file_name = os.path.join(app.config['UPLOAD_PATH'], filename)
        f.save(file_name)
        print('上传头像成功')
    else:
        print(form.errors)
    return render_template('avatar_upload.html', form=form)


app.add_url_rule('/index', 'index', index)

print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True)
