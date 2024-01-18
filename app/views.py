from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file

from config import Config
from db import ProcessedImage, Image, User
from db.tools import update_db
from tools import Image_tools
from tools.recode import json_recode
from .utils import save_image, get_image_list, cut_dir, get_token, verify_token
import os

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    token = request.cookies.get('token')
    uid = request.cookies.get('uid')
    # 校验cookie
    if not verify_token(uid, token):
        return redirect(url_for('main.login_page'))
    img_list = get_image_list(uid)
    if request.method == 'POST':

        image_files = request.files.getlist('image')

        for image_file in image_files:
            if image_file and allowed_file(image_file.filename):
                save_image(image_file, uid)
        return redirect(url_for('main.index'))
    return render_template('index.html', img_list=img_list)


# 登录页面
@main.route('/login', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')


# 添加用户
@main.route('/api/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        if username and password:
            user = User(username=username, password=password)
            if email:
                user.email = email
            if phone:
                user.phone = phone
            return json_recode(200)
        else:
            return json_recode(401)


# 登录
@main.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')

        if username and password:
            # 查询用户，可以使用用户名或邮箱或手机号码登录
            user = User.query.filter(
                (User.username == username) |
                (User.email == username) |
                (User.phone == username)
            ).first()
            if user:
                if user.password == password:
                    token = get_token(user.id)
                    return json_recode(200, {
                        "token": token,
                        "uid": user.id
                    })
                else:
                    return json_recode(400)
            else:
                return json_recode(400)
        else:
            return json_recode(400)


# 获取用户信息
@main.route('/api/user_info', methods=['GET', 'POST'])
def user_info():
    if request.method == 'POST':
        user_id = request.form.get('uid')
        token = request.form.get('token')
    else:
        token = request.cookies.get('token')
        user_id = request.cookies.get('uid')
        if not verify_token(user_id, token):
            return json_recode(402)

    if user_id and token:
        user = User.query.filter_by(id=user_id).first()
        if user:
            _user_info = verify_token(user_id, token)
            print(_user_info)
            if _user_info:
                return json_recode(200, _user_info)
            else:
                return json_recode(402)
        else:
            return json_recode(403)



# 获取图片列表
@main.route('/api/list', methods=['GET', 'POST'])
def get_list():
    # 校验cookie
    token = request.cookies.get('token')
    uid = request.cookies.get('uid')
    if not verify_token(uid, token):
        return json_recode(402)

    img_list = get_image_list(uid)
    return json_recode(200, img_list)


# 上传图片
@main.route('/api/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            save_data = save_image(image_file)
            return json_recode(200, save_data)
        else:
            return json_recode(405)


# 读取图片
@main.route('/api/img', methods=['GET', 'POST'])
def img():
    image_id = request.args.get('id')
    # 判断图片是否存在
    if image_id:
        image_id = int(image_id)
        img_data = Image.query.filter_by(id=image_id).first()
        if not img_data:
            return json_recode(404)
    else:
        return json_recode(401)

    # 如果有指定缩略图大小，则返回缩略图
    size = request.args.get('size')
    width = request.args.get("width")
    height = request.args.get("height")
    if image_id and size:
        processing_method = "thumbnail"
        width = int(size.split("x")[0])
        height = int(size.split("x")[1])
        img_data = ProcessedImage.query.filter_by(
            image_id=image_id,
            width=width,
            height=height,
            processing_method=processing_method
        ).first()
        if img_data:
            file_path = img_data.url
        # 如果缩略图不存在，则创建缩略图
        else:
            img_data = Image.query.filter_by(id=image_id).first()
            _img = Image_tools.IM(img_data.original_url)
            _img.crop((width, height))
            # 保存缩略图
            save_path, img_id = update_db(
                _img.get_image(),
                file_type=_img.img_type,
                image_id=image_id,
                processing_method=processing_method
            )
            cut_dir(save_path)
            _img.save(save_path)
            file_path = save_path
    # 如果指定宽高，则根据宽高缩放图片
    elif image_id and (width or height):
        processing_method = "resize"
        if width:
            width = int(width)
            img_data = ProcessedImage.query.filter_by(
                image_id=image_id,
                width=width,
                processing_method=processing_method
            ).first()
        if height:
            height = int(height)
            img_data = ProcessedImage.query.filter_by(
                image_id=image_id,
                height=height,
                processing_method=processing_method
            ).first()
        if img_data:
            file_path = img_data.url
        # 如果缩略图不存在，则创建缩略图
        else:
            img_data = Image.query.filter_by(id=image_id).first()
            _img = Image_tools.IM(img_data.original_url)
            if width:
                _img.resize(width=width)
            else:
                _img.resize(height=height)
            # 保存缩略图
            save_path, img_id = update_db(
                _img.get_image(),
                file_type=_img.img_type,
                image_id=image_id,
                processing_method=processing_method
            )
            _img.save(save_path)
            file_path = save_path
    else:
        file_path = img_data.original_url
    if os.path.isfile(file_path):
        return send_file(file_path.replace(file_path.split("/")[0] + "/", ""), mimetype=f'image/{img_data.saved_name.split(".")[-1]}')
    else:
        return json_recode(404)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
