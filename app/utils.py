import os
import re
import time

from PIL import Image
from config import Config
from db.tools import update_db
from tools import Image_tools
from db import Image as Image_db
from db import ProcessedImage


def save_image(image):
    """
    保存图片
    :param image:
    :return:
    """
    save_data = {}
    filetype = image.filename.split('.')[-1]
    filename = image.filename
    image = Image.open(image)
    # 将图片信息上传到数据库
    save_path, img_id = update_db(
        image,
        filetype,
        original_name=filename
    )

    cut_dir(save_path)
    save_data['original'] = {
        'path': save_path,
        "url": f"{Config.HTTP_ROOT_PATH}?id={img_id}"
    }
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
        img.crop(thumbnail.SIZE)
        save_path, img_id = update_db(img.get_image(), image_id=image_id, processing_method=f"thumbnail")
        img.save(save_path)
        thumbnail_list.append({
            'size': f"{thumbnail.SIZE[0]}x{thumbnail.SIZE[1]}",
            'path': save_path,
            "url": f"{Config.HTTP_ROOT_PATH}?id={image_id}&size={thumbnail.SIZE[0]}x{thumbnail.SIZE[1]}"
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
def get_image_list():
    image_list = []
    # 读取数据库
    img_data_list = Image_db.query.all()
    for img_data in img_data_list:
        file_name = img_data.saved_name
        if file_name.split('.')[-1].lower() in Config.ALLOWED_EXTENSIONS:
            # 如果有指定缩略图大小，则返回缩略图
            thumbnail_list = []
            if Config.THUMBNAIL_SIZE:
                for thumbnail in Config.THUMBNAIL_SIZE:
                    # 查询数据库中是否有缩略图
                    img = ProcessedImage.query.filter_by(
                        image_id=img_data.id,
                        processing_method=f"thumbnail",
                        width=int(thumbnail.SIZE[0]),
                        height=int(thumbnail.SIZE[1]),
                    ).first()
                    if img:
                        thumbnail_list.append({
                            'size': f"{thumbnail.SIZE[0]}x{thumbnail.SIZE[1]}",
                            'url': f"{Config.HTTP_ROOT_PATH}?id={img_data.id}&size={thumbnail.SIZE[0]}x{thumbnail.SIZE[1]}"
                        })
                print(thumbnail_list)
            image_list.append({
                'path': img_data.original_url,
                'filename': img_data.saved_name,
                'url': f"{Config.HTTP_ROOT_PATH}?id={img_data.id}",
                "thumbnails": thumbnail_list,
            })
    return image_list
