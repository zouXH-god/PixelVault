import os
import re
import secrets
import time

from PIL import Image
from config import Config
from db.tools import update_db
from tools import Image_tools
from db import Image as Image_db, User, db
from db import ProcessedImage


def save_image(image, uid):
    """
    保存图片
    :param uid:  用户id
    :param image: 图片
    :return:
    """
    save_data = {}
    filetype = image.filename.split('.')[-1]
    filename = image.filename
    image_bytes = image.read()
    image = Image.open(image)
    # 将图片信息上传到数据库
    save_path, img_id = update_db(
        image,
        file_type=filetype,
        uid=uid,
        original_name=filename
    )

    cut_dir(save_path)
    save_data['original'] = {
        'path': save_path,
        "url": f"{Config.HTTP_ROOT_PATH}?id={img_id}"
    }
    if image.format == "GIF":
        with open(save_path, 'wb') as f:
            f.write(image_bytes)
    else:
        image.save(save_path)
    print(save_path)
    # 生成缩略图并保存
    thumbnail_list = create_thumbnail_list(save_path, img_id)
    save_data['thumbnail'] = thumbnail_list
    # 添加水印
    if Config.ADD_WATERMARK:
        add_watermark(save_path)
    return save_data


def create_thumbnail_list(image_path, image_id):
    """
    生成缩略图列表
    :param image_path: 图片路径
    :param image_id: 原图id
    :return:
    """
    thumbnail_list = []
    for thumbnail in Config.THUMBNAIL_SIZE:
        # 生成缩略图并保存
        img = Image_tools.IM(image_path)
        width = thumbnail.SIZE[0]
        height = thumbnail.SIZE[1]
        processing_method = "resize"
        # 如果宽度或高度为auto，则按比例缩放
        if width == "auto":
            height = img.resize(height=height)
        elif height == "auto":
            width = img.resize(width=width)
        else:
            img.crop(thumbnail.SIZE)
            processing_method = "thumbnail"
        # 上传数据库
        save_path, img_id = update_db(
            img.get_image(),
            file_type=img.img_type,
            image_id=image_id,
            processing_method=processing_method
        )
        # 保存缩略图
        img.save(save_path)
        thumbnail_list.append({
            'size': f"{width}x{height}",
            'path': save_path,
            "url": f"{Config.HTTP_ROOT_PATH}?id={image_id}&size={width}x{height}"
        })
    return thumbnail_list

def add_watermark(image_path):
    """
    添加水印
    :param image_path:
    :return:
    """
    watermark_path = Config.WATERMARK_PATH  # 水印图片路径，可以放在配置文件中
    with Image.open(image_path).convert("RGBA") as base:
        with Image.open(watermark_path).convert("RGBA") as watermark:
            # 可以在这里调整水印的位置和大小
            base.paste(watermark, (0, 0), watermark)
        if base.mode in ['P', 'RGBA']:
            base = base.convert('RGB')
        cut_dir(image_path)
        base.save(image_path, "JPEG")


# 切割文件路径，逐层判断文件夹是否存在，存在则继续判断下一层，不存在则创建
def cut_dir(path):
    path = re.split(r'[\\|/]', path)
    for i in range(len(path) - 1):
        dirs = '/'.join(path[:i + 1])
        if not os.path.isdir(dirs):
            os.mkdir(dirs)


# 获取图片列表
def get_image_list(uid):
    image_list = []
    # 读取数据库
    img_data_list = Image_db.query.filter_by(uploader_id=uid).all()
    for img_data in img_data_list:
        file_name = img_data.saved_name
        if file_name.split('.')[-1].lower() in Config.ALLOWED_EXTENSIONS:
            # 如果有指定缩略图大小，则返回缩略图
            thumbnail_list = []
            if Config.THUMBNAIL_SIZE:
                for thumbnail in Config.THUMBNAIL_SIZE:
                    # 查询数据库中是否有缩略图
                    if "auto" not in thumbnail.SIZE:
                        img = ProcessedImage.query.filter_by(
                            image_id=img_data.id,
                            processing_method=f"thumbnail",
                            width=int(thumbnail.SIZE[0]),
                            height=int(thumbnail.SIZE[1]),
                        ).first()
                        if img:
                            url = f"{Config.HTTP_ROOT_PATH}?id={img_data.id}&size={img.width}x{img.height}"
                    # 若没有指定宽高，则查询按比例缩放
                    else:
                        if thumbnail.SIZE[0] == "auto":
                            img = ProcessedImage.query.filter_by(
                                image_id=img_data.id,
                                processing_method=f"resize",
                                height=int(thumbnail.SIZE[1]),
                            ).first()
                        else:
                            img = ProcessedImage.query.filter_by(
                                image_id=img_data.id,
                                processing_method=f"resize",
                                width=int(thumbnail.SIZE[0]),
                            ).first()
                        if img:
                            url = f"{Config.HTTP_ROOT_PATH}?id={img_data.id}&width={img.width}&height={img.height}"
                    if img:
                        thumbnail_list.append({
                            'size': f"{img.height}x{img.width}",
                            'url': url
                        })
            image_list.append({
                'path': img_data.original_url,
                'filename': img_data.saved_name,
                'url': f"{Config.HTTP_ROOT_PATH}?id={img_data.id}",
                "thumbnails": thumbnail_list,
            })
    return image_list


# 获取token
def get_token(user_id):
    """
    获取用户token,如果没有则生成
    :param user_id:  用户id
    :return:
    """
    user = User.query.filter_by(id=user_id).first()
    if user:
        if user.token:
            return user.token
        else:
            token = generate_token()
            user.token = token
            db.session.commit()
            return token
    else:
        return None


# 生成随机token
def generate_token(length=32):
    """
    生成一个安全的随机令牌。
    :param length: 令牌的长度，以字节为单位，默认为32字节。
    :return: 返回一个随机生成的令牌字符串。
    """
    return secrets.token_hex(length)


# 验证用户是否登录，返回用户信息
def verify_token(user_id, token):
    """
    验证用户是否登录，返回用户信息
    :param user_id: 用户id
    :param token: 用户token
    :return:
    """
    user = User.query.filter_by(id=user_id).first()
    if user:
        if user.token == token:
            return get_user_info(user_id)
        else:
            return None
    else:
        return None


# 获取用户信息
def get_user_info(user_id):
    """
    获取用户信息
    :param user_id: 用户id
    :return:
    """
    user = User.query.filter_by(id=user_id).first()
    if user:
        return {
            'userId': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'creation_time': user.creation_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    else:
        return None