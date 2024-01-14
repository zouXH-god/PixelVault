from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """
    用户模型，存储用户信息
    - id: 用户的唯一标识符
    - username: 用户名
    - password: 用户密码
    - creation_time: 账户创建时间
    - email: 用户的电子邮件地址
    - phone: 用户的手机号码（可选）
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)

    images = db.relationship('Image', backref='uploader', lazy=True)

class Image(db.Model):
    """
    图片模型，存储图片信息
    - id: 图片的唯一标识符
    - original_name: 图片的原始文件名
    - saved_name: 图片保存在服务器上的文件名
    - size: 图片文件的大小（字节）
    - space_used: 图片在服务器上占用的空间（字节）
    - original_url: 图片的原始URL
    - upload_time: 图片上传的时间
    - uploader_id: 上传用户的ID（外键）
    """
    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(120), nullable=False)
    saved_name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    space_used = db.Column(db.Integer, nullable=False)
    original_url = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    processed_images = db.relationship('ProcessedImage', backref='original', lazy=True)

class ProcessedImage(db.Model):
    """
    处理后的图片模型，存储处理后的图片信息
    - id: 处理后图片的唯一标识符
    - image_id: 原始图片的ID（外键）
    - processing_method: 图片处理方法
    - url: 处理后图片的URL
    - space_used: 处理后图片在服务器上占用的空间（字节）
    - size: 处理后图片文件的大小（字节）
    - save_time: 处理后图片保存的时间
    """
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    processing_method = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    space_used = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    save_time = db.Column(db.DateTime, default=datetime.utcnow)
