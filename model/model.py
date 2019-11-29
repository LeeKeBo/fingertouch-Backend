from conf.conf import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Book(db.Model):  # 书
    __tablename__ = 'books'
    isbn = db.Column(db.String(20), unique=True, primary_key=True)
    name = db.Column(db.String(60))
    author = db.Column(db.String(30))
    describe = db.Column(db.String(200))
    pages = db.Column(db.Integer)
    publishing = db.Column(db.String(60))

    def serialize(self):
        return {
            'isbn': self.isbn,
            'name': self.name,
            'author': self.author,
            'describe': self.describe,
            'pages': self.pages,
            'publishing': self.publishing
        }

    def __repr__(self):
        return '<Books {}>'.format(self.name)


class Role(db.Model):  # 角色
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), unique=True)  # 角色类型

    def __repr__(self):
        return '<Role {}>'.format(self.type)


class User(UserMixin, db.Model):  # 用户
    __tablename__ = 'users'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(60))
    password = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 引入外键
    last_login = db.Column(db.DateTime)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class MarkArea(db.Model):  # 标定区域
    __tablename__ = "markareas"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    isbn = db.Column(db.String(20), db.ForeignKey('books.isbn'), index=True)
    count = db.Column(db.Integer)
    relativeX = db.Column(db.Float)
    relativeY = db.Column(db.Float)
    relativeW = db.Column(db.Float)
    relativeH = db.Column(db.Float)
    name = db.Column(db.String(40))
    uuid = db.Column(db.String(8))
    page = db.Column(db.Integer)

    audio = db.Column(db.String(50))

    def serialize(self):
        return {
            'isbn': self.isbn,
            'index': self.count,
            'relativeX':self.relativeX,
            'relativeY':self.relativeY,
            'relativeW':self.relativeW,
            'relativeH':self.relativeH,
            'name': self.name,
            'uuid': self.uuid,
        }


    def __repr__(self):
        return '<markArea {}>'.format(self.isbn)


class bookphoto(db.Model):
    __tablename__ = "bookphoto"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    isbn = db.Column(db.String(20), db.ForeignKey('books.isbn'), index=True)
    page = db.Column(db.Integer)
    uuid = db.Column(db.String(8))
    address = db.Column(db.String(150))

    def serialize(self):
        return {
            'isbn': self.isbn,
            'index': self.index,
            'src': self.address,
            'uuid': self.uuid,
        }
