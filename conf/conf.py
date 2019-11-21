from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from auth import auth

app = Flask(__name__,root_path='D:\code/backEnd/fingertouch-Backend2')
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://wen:123456@127.0.0.1:3306/fingertouch'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SECRET_KEY'] = '123456'
app.config['DEBUG'] = True
# app.register_blueprint(auth)
db = SQLAlchemy(app)
