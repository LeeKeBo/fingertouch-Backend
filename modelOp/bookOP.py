from flask import Blueprint, request, jsonify
from model.model import db, Book
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

    form = request.form

    book = Book.query.filter_by(isbn=form['form'])
    if book is not None:
        return "isbn can't be the same"
    else:
        book = Book(isbn=form['isbn'], name=form['name'], author=form['author'], describe=form['describe'],
                    pages=form['pages'], publishing=form['publishing'])
        db.session.add(book)
        db.session.commit()
        return 'add book successfully'


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

    isbn = request.args.get('isbn')

    book = Book.query.filter_by(isbn=isbn).first()
    if book is None:
        return "can't find this book"
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

    isbn = request.args.get('isbn')
    book = Book.query.filter_by(isbn=isbn).first()
    if book is None:
        return "can't find this book"
    else:
        Book.query.filter_by(isbn=isbn).delete()


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


    form = request.form
    book = Book.query.filter_by(isbn=form['isbn']).first()
    if book is None:
        return "can't find the book"
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
        return "update successfully"


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

