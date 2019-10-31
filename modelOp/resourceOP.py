import json
import os
import random

from flask import Blueprint, request, jsonify
from model.model import MarkArea, db

# 模型调用，此时并初始化了
from tool import tool_model
from config import IMG_DIR

resource = Blueprint('resource', __name__)


@resource.route('/')
def index():
    return "hello world"


@resource.route('/Res', methods=['POST'])
def makeRes():
    """
    划分区域
    ---
    tags:
      - 资源相关接口
    description:
        划分区域接口，json格式
    parameters:
      - name: markAreas
        in: body
        required: true
        schema:
          id: 书籍区域划分
          required:
            - index
            - firstX
            - firstY
            - secondX
            - secondY
            - thirdX
            - thirdY
            - forthX
            - forthY
            - page
          properties:
            index:
              type: int
              description: 区域编号.
            firstX:
              type: float
              description: 第一个点横坐标.
            firstY:
              type: float
              description: 第一个点纵坐标.
            secondX:
              type: float
              description: 第二个点横坐标.
            secondY:
              type: float
              description: 第二个点纵坐标.
            thirdX:
              type: float
              description: 第三个点横坐标.
            thirdY:
              type: float
              description: 第三个点纵坐标.
            forthX:
              type: float
              description: 第四个点横坐标.
            forthY:
              type: float
              description: 第四个点纵坐标.
            page:
              type: int
              description: 所在页数

      - name: isbn
        in: string
        description: 书籍isbn号

    responses:
      201:
          description: 添加成功
          example: {'code':1,'message':添加成功}
      401,402,403,404,405,406:
        description: 添加失败，参数有误等

    """

    # markAreas = request.form['markAreas']  # 标记坐标数组
    # isbn = request.form['isbn']  # 书本ISBN号

    data = request.get_data()
    data = json.loads(data)

    markAreas = data['markAreas']
    isbn = data['isbn']

    for area in markAreas:
        newArea = MarkArea(isbn=isbn, index=area['index'], firstX=area['firstX'], firstY=area['firstY'],
                           secondX=area['secondX'], secondY=area['secondY'], thirdX=area['thirdX'],
                           thirdY=area['thirdY'], forthX=area['forthX'], forthY=area['forthY'], page=area['page'])
        db.session.add(newArea)
    db.session.commit()
    return 'successful'


@resource.route('/Res', methods=['GET'])
def getRes():
    """
    获取区域语音
    ---
    tags:
      - 资源相关接口
    description:
        获取区域语音口，json格式
    parameters:
      - name: clickArea
        in: body
        required: true
        schema:
          id: 点击区域
          required:
            - x
            - y
            -
          properties:
            x:
              type: float
              description: 点击位置横坐标
            y:
              type: float
              description: 点击位置纵坐标
            page:
              type: int
              description: 所在页数

      - name: isbn
        in: string
        description: 书籍isbn号

    responses:
      201:
          description: 获取成功
          example: {'code':1,'message':获取成功,'audio':audio}
      401,402,403,404,405,406:
        description: 未找到该区域或此区域尚未绑定资源

    """

    # 获取json数据，并解析
    data = request.get_data()
    data = json.loads(data)

    clickArea = data['clickArea']
    isbn = data['isbn']

    x = clickArea['x']
    y = clickArea['y']
    page = clickArea['page']
    audio = db.session.query(MarkArea.audio).filter(MarkArea.isbn == isbn, MarkArea.firstX >= x, MarkArea.firstY <= y,
                                                    MarkArea.secondX >= x,
                                                    MarkArea.secondY <= y, MarkArea.thirdX <= x, MarkArea.thirdY >= y,
                                                    MarkArea.forthX >= x,
                                                    MarkArea.forthY >= y, MarkArea.page == page).first()
    # print(audio)
    if audio is None:
        return "have no this audio"
    return audio
    # return "jiumi"
    # return audio


@resource.route('/testPhoto', methods=['POST'])
def testPhoto():
    print(request.json)

    filename = request.json.get('filename')
    file_path = os.path.join(IMG_DIR, filename)
    # 暂时没用上book，只有一本书的模型
    book = request.json.get("book")

    # 调用图像处理函数，得到结果，假设存放在result中
    # out_put: {'Finger':[手指坐标,...], 'corner':[], }
    pre_finger, pre_page = tool_model.run(file_path)
    result = {
        'finger': pre_finger,
        'page': pre_page,
    }
    return jsonify(result)


@resource.route('/getPhoto', methods=['POST'])
def getPhoto():
    print(request)
    img = request.files.get('file')
    path = "./static/photo/"
    salt = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ext = img.filename.rsplit('.', 1)[1]
    filename = ''
    for i in range(6):
        filename += random.choice(salt)
    filename += "."+ext
    path += filename
    print(filename)
    img.save(path)
    return filename
