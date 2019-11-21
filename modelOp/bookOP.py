import random
from flask import Blueprint, request, jsonify
from sqlalchemy import JSON

from model.model import db, Book, bookphoto
import json

book = Blueprint('book', __name__)


@book.route('/book', methods=['POST'])
def addBook():
    """
    添加书籍
    ---
    tags:
      - 书籍相关接口
    description:
        添加书籍接口，json格式
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: 添加书籍
          required:
            - isbn
            - name
            - author
            - pages
            - describe
            - publishing
          properties:
            isbn:
              type: string
              description: 书籍isbn号.
            name:
              type: string
              description: 书籍名.
            author:
              type: string
              description: 作者.
            pages:
              type: int
              description: 书籍页数.
            describe:
              type: string
              description: 书籍简介.
            publishing:
              type: string
              description: 出版社.

    responses:
      201:
          description: 添加成功
          example: {'code':1,'message':添加成功}
      401,402,403,404,405,406:
        description: 添加失败，参数有误等

    """

    form = request.json

    book = Book.query.filter_by(isbn=form['isbn']).first()
    if book is not None:
        return {'code': -1, 'result': "该isbn号已存在，不能重复出现"}
    else:
        book = Book(isbn=form['isbn'], name=form['name'], author=form['author'], describe=form['describe'],
                    pages=form['pages'], publishing=form['publishing'])
        db.session.add(book)
        db.session.commit()
        return {'code': 1, 'result': 'add book successfully'}


@book.route('/book', methods=['GET'])
def getBook():
    """
    获取书籍
    ---
    tags:
      - 书籍相关接口
    description:
        获取书籍接口
    parameters:
      - name: isbn
        in: string
        required: true
        description: 书籍isbn号.

    responses:
      200:
          description: 获取成功
          example: {'code':1,'message':获取成功,'book':book}
      401,402,403,404,405,406:
        description: 获取失败，参数有误等

    """

    isbn = request.json['isbn']

    book = Book.query.filter_by(isbn=isbn).first()
    if book is None:
        return {'code': -1, 'result': "can't find this book"}
    else:
        # book = se
        return jsonify(book.serialize())


@book.route('/book', methods=['DELETE'])
def deleteBook():
    """
    删除书籍
    ---
    tags:
      - 书籍相关接口
    description:
        删除书籍接口
    parameters:
      - name: isbn
        in: string
        required: true
        description: 书籍isbn号.

    responses:
      200:
          description: 删除成功
          example: {'code':1,'message':删除成功}
      401,402,403,404,405,406:
        description: 删除失败，参数有误等

    """

    isbn = request.json['isbn']
    book = Book.query.filter_by(isbn=isbn).first()
    if book is None:
        return {'code': -1, 'result': "can't find this book"}
    else:
        db.session.delete(book)
        db.session.commit()
        return {'code': 1, 'result': 'delete'}


@book.route('/updateBook', methods=['POST'])
def updateBook():
    """
    修改书籍
    ---
    tags:
      - 书籍相关接口
    description:
        修改书籍接口，json格式
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: 修改书籍
          required:
            - isbn
            - name
            - author
            - pages
            - describe
            - publishing
          properties:
            isbn:
              type: string
              description: 书籍isbn号.
            name:
              type: string
              description: 书籍名.
            author:
              type: string
              description: 作者.
            pages:
              type: int
              description: 书籍页数.
            describe:
              type: string
              description: 书籍简介.
            publishing:
              type: string
              description: 出版社.

    responses:
      201:
          description: 修改成功
          example: {'code':1,'message':修改成功}
      401,402,403,404,405,406:
        description: 修改失败，参数有误等

    """

    form = request.json
    book = Book.query.filter_by(isbn=form['isbn']).first()
    if book is None:
        return {'code': -1, 'result': "该书籍不存在"}
    else:
        book.author = form['author']
        book.publishing = form['publishing']
        book.name = form['name']
        book.describe = form['describe']
        book.pages = form['pages']
        db.session.commit()
        # Book.query.filter_by(isbn=form['isbn']).update(
        #     {'name': form['name'], 'author': form['author'], 'describe': form['describe'], 'pages': form['pages'],
        #      'publishing': form['publishing']})
        return {'code': 1, 'result': "update successfully"}


@book.route('/bookList', methods=['GET'])
def bookList():
    """
    获取所有书籍
    ---
    tags:
      - 书籍相关接口
    description:
        获取所有书籍

    responses:
      200:
          description: 获取成功
          example: {'code':1,'message':添加成功,'books':booksArray}
      401,402,403,404,405,406:
        description: 获取失败

    """

    bookList = Book.query.all()
    return jsonify(bookList=[book.serialize() for book in bookList])


@book.route('/uploadPhoto', methods=['post'])
def uploadPhoto():
    img = request.files.get('file')
    isbn = request.values['isbn']
    path = "./static/bookphoto/"
    salt = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ext = img.filename.rsplit('.', 1)[1]
    filename = ''
    for i in range(6):
        filename += random.choice(salt)
    filename += "." + ext
    path += filename
    img.save(path)
    # 为图片增加标识符
    uuid = ''
    for i in range(8):
        uuid += random.choice(salt)
    # 获取index值
    index = bookphoto.query.filter_by(isbn=isbn).count()
    newPhoto = bookphoto(isbn=isbn, address=path, uuid=uuid, page=index)
    db.session.add(newPhoto)
    db.session.commit()

    return {'code': 1, 'result': 'update successfully'}


@book.route('/getPhoto', methods=['get'])
def getPhoto():
    data = request.args
    isbn = data['isbn']
    photos = db.session.query(bookphoto.address.label("src"), bookphoto.uuid).filter_by(isbn=isbn).order_by(
        bookphoto.page).all()
    print(photos)
    result = [dict(zip(photo.keys(), photo)) for photo in photos]
    result = jsonify(result)
    print(result)
    return result
    # jsonify(photos=[photo.serialize() for photo in photos])


# 提交修改顺序后的书籍页
@book.route('/uploadOrder', methods=['post'])
def uploadOrder():
    data = request.json
    for index, value in enumerate(data):
        photo = bookphoto.query.filter_by(uuid=value['uuid']).first()
        if photo is not None:
            photo.page = index
            db.session.commit()
        else:
            return {'code': -1, 'result': '修改出错，图片未找到，请重试'}
    return {'code': 1, 'result': '成功修改图片顺序'}
