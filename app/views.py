from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file

from config import Config
from db import ProcessedImage, Image
from db.tools import update_db
from tools import Image_tools
from .utils import save_image, get_image_list
import os

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    img_list = get_image_list()
    if request.method == 'POST':
        image_files = request.files.getlist('image')

        for image_file in image_files:
            if image_file and allowed_file(image_file.filename):
                save_image(image_file)
        return redirect(url_for('main.index'))
    return render_template('index.html', img_list=img_list)


# 获取图片列表
@main.route('/api/list', methods=['GET', 'POST'])
def get_list():
    img_list = get_image_list()
    return jsonify(img_list)


# 上传图片
@main.route('/api/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            save_data = save_image(image_file)
            return jsonify(save_data)


# 读取图片
@main.route('/api/img', methods=['GET', 'POST'])
def img():
    image_id = request.args.get('id')
    size = request.args.get('size')
    # 如果有指定缩略图大小，则返回缩略图
    if image_id and size:
        width = int(size.split("x")[0])
        height = int(size.split("x")[1])
        img_data = ProcessedImage.query.filter_by(image_id=image_id, width=width, height=height).first()
        if img_data:
            file_path = img_data.url
        # 如果缩略图不存在，则创建缩略图
        else:
            img_data = Image.query.filter_by(id=image_id).first()
            img = Image_tools.IM(img_data.original_url)
            img.crop((width, height))
            # 保存缩略图
            save_path, img_id = update_db(img.get_image(), image_id=image_id, processing_method=f"thumbnail")
            img.save(save_path)
            file_path = save_path
    else:
        img_data = Image.query.filter_by(id=image_id).first()
        file_path = img_data.original_url
    if os.path.isfile(file_path):
        return send_file(file_path.replace(file_path.split("/")[0] + "/", ""), mimetype=f'image/{img_data.saved_name.split(".")[-1]}')
    else:
        return jsonify({'code': 404, 'msg': '图片不存在'})


def allowed_file(filename):
    ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
