import random
from flask import Blueprint, request, jsonify
from model.model import MarkArea, db
<<<<<<< HEAD

# 模型调用，此时并初始化了
# from tool import tool_model
# from config import IMG_DIR

=======
from conf.conf import login_required
>>>>>>> linux
resource = Blueprint('resource', __name__)


@resource.route('/')
def index():
    return "hello world"


@resource.route('/Area', methods=['POST'])
@login_required
def makeArea():
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
            - x
            - y
            - w
            - h
            - page
            - thirdY
            - forthX
            - forthY
          properties:
            index:
              type: int
              description: 区域编号.
            x:
              type: float
              description: 左上角横坐标.
            y:
              type: float
              description: 左上角纵坐标.
            w:
              type: float
              description: 矩形宽度.
            h:
              type: float
              description: 矩形长度.


      - name: isbn
        in: string
        description: 书籍isbn号
      - name: page
        in: int
        description: 页数

    responses:
      201:
          description: 添加成功
          example: {'code':1,'message':添加成功}
      401,402,403,404,405,406:
        description: 添加失败，参数有误等

    """

    # markAreas = request.form['markAreas']  # 标记坐标数组
    # isbn = request.form['isbn']  # 书本ISBN号
    data = request.json

    markAreas = data['markAreas']
    isbn = data['isbn']
    page = data['page']
    uuids = []

    if isbn == None or page == None:
        return {'code': -1, 'result': 'isbn或页数不正确'}

    # 保存或更新客户增加或修改的区域
    for index in range(len(markAreas)):
        area = markAreas[index]
        uuids.append(area['uuid'])
        oldArea = MarkArea.query.filter_by(uuid=area['uuid']).first()
        if oldArea == None:
            newArea = MarkArea(isbn=isbn, count=index, relativeX=area['relativeX'], relativeY=area['relativeY'],
                               relativeW=area['relativeW'], relativeH=area['relativeH'], page=page, name=area['name'], uuid=area['uuid'])
            db.session.add(newArea)
        else:
            oldArea.relativeX = area['relativeX']
            oldArea.relativeY = area['relativeY']
            oldArea.relativeW = area['relativeW']
            oldArea.relativeH = area['relativeH']
            oldArea.name = area['name']
            oldArea.count = index

    # 删除被客户删除的区域
    areas = MarkArea.query.filter_by(page=page, isbn=isbn).all()
    for area in areas:
        if area.uuid not in uuids:
            db.session.delete(area)

    # for index, area in markAreas:
    db.session.commit()
    return {'code': 1, 'result': '已保存分区信息'}


@resource.route('/Area', methods=['GET'])
@login_required
def getArea():
    data = request.args
    isbn = data['isbn']
    page = data['page']

    areas = MarkArea.query.filter_by(page=page, isbn=isbn).all()
    return jsonify(areas=[area.serialize() for area in areas])


@resource.route('/Res', methods=['GET'])
@login_required
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
    data = request.json

    clickArea = data['clickArea']
    isbn = data['isbn']

    # # x = clickArea['x']
    # # y = clickArea['y']
    # # page = clickArea['page']
    # # audio = db.session.query(MarkArea.audio).filter(MarkArea.isbn == isbn, MarkArea.firstX >= x, MarkArea.firstY <= y,
    # #                                                 MarkArea.secondX >= x,
    # #                                                 MarkArea.secondY <= y, MarkArea.thirdX <= x, MarkArea.thirdY >= y,
    # #                                                 MarkArea.forthX >= x,
    # #                                                 MarkArea.forthY >= y, MarkArea.page == page).first()
    # # print(audio)
    # if audio is None:
    #     return "have no this audio"
    # return audio
    return "have not write"
    # return "jiumi"
    # return audio


@resource.route('/testPhoto', methods=['POST'])
@login_required
def testPhoto():
    print(request.json)

    # "./static/photo/"
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
@login_required
def getPhoto():
    print(request)
    img = request.files.get('file')
    path = "./static/photo/"
    salt = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ext = img.filename.rsplit('.', 1)[1]
    filename = ''
    for i in range(6):
        filename += random.choice(salt)
    filename += "." + ext
    path += filename
    print(filename)
    img.save(path)
    return filename
