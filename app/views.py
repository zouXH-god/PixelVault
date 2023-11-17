from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file

from config import Config
from .utils import save_image, create_thumbnail
import os

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            save_image(image_file)
            return redirect(url_for('main.index'))
    return render_template('index.html')


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
    filename = request.args.get('filename')
    size = request.args.get('size')
    file_orange_path = f'{Config.UPLOAD_FOLDER}/{filename}'
    # 如果有指定缩略图大小，则返回缩略图
    if filename and size:
        file_path = f'{Config.STATIC_FOLDER}images/thumbnails/{"x".join(size.split("x"))}{filename}'
        # 如果缩略图不存在，则创建缩略图
        if os.path.exists(file_orange_path) and not os.path.exists(file_path):
            create_thumbnail(file_orange_path, file_path, size=(int(size.split("x")[0]), int(size.split("x")[1])))
    else:
        file_path = file_orange_path
    if os.path.isfile(file_path):
        return send_file(file_path.replace(file_path.split("/")[0] + "/", ""), mimetype=f'image/{filename.split(".")[-1]}')
    else:
        return jsonify({'code': 404, 'msg': '图片不存在'})


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
