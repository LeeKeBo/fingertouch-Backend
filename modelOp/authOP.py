from flask import request, flash, url_for, Blueprint, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from model.model import User, db, Role

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    """
    用户登录
    ---
    tags:
      - 用户相关接口
    description:
        用户登录接口，json格式
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: 用户登录
          required:
            - username
            - password
            - email
          properties:
            username:
              type: string
              description: 用户名.
            password:
              type: string
              description: 密码.
            email:
              type: string
              description: 邮箱.
            

    responses:
      201:
          description: 登录成功
          example: {'code':1,'message':登录成功}
      401,402,403,404,405,406:
          description: 登录失败
          example: {'code':1,'message':该用户未注册}

    """

    #email = request.form['email']
    data = request.json
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user is not None:
        if user.verify_password(password):
            login_user(user)
            return jsonify({
                'code': 1,
                'result': '登录成功'
            })
        else:
            return jsonify({
                'code': -1,
                'result': '密码错误'
            })
    else:
        return jsonify({
            'code': -1,
            'result': '该用户未注册'
        })


@auth.route('/logout')
@login_required
def logout():
    """
    用户注销
    ---
    tags:
      - 用户相关接口
    description:
        用户注销接口

    responses:
      200:
          description: 注销成功
          example: {'code':1,'message':注销成功}
      401,402,403,404,405,406:
        description: 注销失败

    """

    logout_user()
    return jsonify({
        'code': 1,
        'message': '注销成功'
    })


@auth.route('/')
@login_required
def index():
    return 'yes,you have log'


@auth.route('/register', methods=['POST'])
def register():
    """
    用户注册
    ---
    tags:
      - 用户相关接口
    description:
        用户注册接口，json格式
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: 用户注册
          required:
            - username
            - password
            - email
            - type
          properties:
            username:
              type: string
              description: 用户名.
            password:
              type: string
              description: 密码.
            email:
              type: string
              description: 邮箱.
            type:
              type: string
              enum: ['admin', 'normal',]
              description: 用户类型.

    responses:
      201:
          description: 注册成功
          example: {'code':1,'message':注册成功}
      406:
        description: 注册有误，参数有误等

    """

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    type = request.form['type']
    user = User.query.filter_by(email=email).first()
    if user is not None:
        return 'this email has been register'
    role = Role.query.filter_by(type=type).first()
    if role is None:
        return 'can not find the role'
    db.session.add(User(username=username, email=email, password=password, role_id=role.id))
    db.session.commit()
    return jsonify({
        'code': 1,
        'message': '注册成功'
    })


@auth.route('/updatePassword', methods=['POST'])
def updateAuth():
    """
    修改密码
    ---
    tags:
      - 用户相关接口
    description:
        修改密码
    parameters:
      - name: form
        in: body
        required: true
        schema:
          id: 修改密码
          required:
            - username
            - oldPassword
            - email
            - newPassword
          properties:
            username:
              type: string
              description: 用户名.
            oldPassword:
              type: string
              description: 旧密码
            email:
              type: string
              description: 邮箱
            newPassword:
              type: string
              description: 新密码
    responses:
      200:
          description: 修改成功
          example: {'code':1,'message':修改成功}
      406:
        description: 修改失败

    """
    return 'yes'


@auth.route('/updateName', methods=['POST'])
def updateName():
    """
    修改用户名
    ---
    tags:
      - 用户相关接口
    description:
        修改用户名
    parameters:
      - name: form
        in: body
        required: true
        schema:
          id: 修改用户名
          required:
            - email
            - newName
          properties:
            email:
              type: string
              description: 邮箱
            newName:
              type: string
              description: 新用户名
    responses:
      200:
          description: 修改成功
          example: {'code':1,'message':修改成功}
      406:
        description: 修改失败

    """
    return 'yes'
