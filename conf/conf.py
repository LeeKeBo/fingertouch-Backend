import datetime
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import time
from functools import wraps


#app = Flask(__name__)
#app = Flask(__name__,root_path='D:\code/backEnd/fingertouch-Backend2')
# root-path 填项目在服务器上的路径
app = Flask(__name__, root_path='/home/fingertouch/fingertouch-Backend2/')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://wen:123456@127.0.0.1:3306/fingertouch'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://finger:Finger@123@127.0.0.1:3306/fingertouch'
#app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://wen:123456@127.0.0.1:3306/fingertouch'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SECRET_KEY'] = 'fingertouchsecretkey'

#app.config['DEBUG'] = True
app.permanent_session_lifetime = datetime.timedelta(seconds=60*20)
db = SQLAlchemy(app)

# 自定义登录拦截器
def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user = session.get('user', "notFound")
        if user == "notFound":
            return {'code': 0, 'result': '登录过期或未登录，请重新登录'}
        else:
            return func(*args, **kwargs)

    return decorator

# 每次用户发起请求，重置其登录计时
@app.before_request
def func():
    session.modified = True

