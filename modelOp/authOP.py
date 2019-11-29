import datetime
from flask import request, Blueprint, jsonify, session
from conf.conf import login_required
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

    # email = request.form['email']
    data = request.json
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user is not None:
        if user.verify_password(password):
            # login_user(user)
            # 设置session, 为登录时间戳
            session.permanent = True
            session['user'] = user.username
            session['type'] = user.role_id
            user.last_login = datetime.datetime.now()
            userType = db.session.query(Role.type).filter_by(id=user.role_id).first()
            return jsonify({
                'code': 1,
                'result': '登录成功',
                'type': userType[0]
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

    session.pop('user')
    # logout_user()
    return jsonify({
        'code': 1,
        'message': '注销成功'
    })


@auth.route('/')
@login_required
def index():
    return 'yes,you have log'


@auth.route('/register', methods=['POST'])
@login_required
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
    if session['type'] != 1:
        return {'code': -1, 'result': '需superAdmin用户才能添加用户'}
    username = request.json['username']
    #    email = request.json['email']
    password = request.json['newPass']
    password2 = request.json['newPass2']
    type = request.json['type']
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return {'code': -1, 'result': '此用户名已被注册'}
    role = Role.query.filter_by(type=type).first()
    if role is None:
        return {'code': -1, 'result': '此用户类型未找到'}
    db.session.add(User(username=username, password=password, role_id=role.id))
    db.session.commit()
    return jsonify({
        'code': 1,
        'result': '注册成功'
    })


@auth.route('/updatePassword', methods=['POST'])
@login_required
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
    if session['role_id'] != 1:
        return {'code': -1, 'result': '权限不足，仅superAdmin能修改密码'}
    username = request.json['username']
    password = request.json['newPass']
    password2 = request.json['newPass2']
    if password != password2:
        return {'code': -1, 'result': '两次密码不一致'}
    user = User.query.filter_by(username=username).first()
    user.password = password
    db.session.commit()
    return {'code': 1, 'result': '修改成功'}


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


@auth.route('/user', methods=['DELETE'])
@login_required
def deleteUser():
    username = request.json['username']
    if session['type'] != 1:
        return {'code': -1, 'result': '需superAdmin才能删除用户'}
    if session['user'] == username:
        return {'code': -1, 'result': '自己不能删除自己T_T'}
    user = User.query.filter_by(username=username).first()
    if user is None:
        return {'code': -1, 'result': '该用户不存在，请刷新重试'}
    db.session.delete(user)
    db.session.commit()
    return {'code': 1, 'result': '用户已删除'}


@auth.route('/getUser', methods=['GET'])
@login_required
def getUser():
    users = db.session.query(User.username, Role.type, User.last_login).filter(User.role_id == Role.id).all()
    result = [dict(zip(user.keys(), user)) for user in users]
    result = jsonify(result)
    return result
