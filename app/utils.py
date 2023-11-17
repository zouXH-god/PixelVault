import os
import re
import time

from PIL import Image
from config import Config

def save_image(image):
    """
    保存图片
    :param image:
    :return:
    """
    save_data = {}
    filetype = image.filename.split('.')[-1]
    filename = time.time().__str__().replace('.', '') + '.' + filetype
    save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    cut_dir(save_path)
    save_data['original'] = {
        'path': save_path,
        "filename": filename,
        "url": f"{Config.HTTP_ROOT_PATH}?filename={filename}"
    }
    image.save(save_path)
    # 生成缩略图并保存
    thumbnail_list = create_thumbnail_list(save_path)
    save_data['thumbnail'] = thumbnail_list
    # 添加水印
    if Config.ADD_WATERMARK:
        add_watermark(save_path)
    return save_data

def create_thumbnail(image_path, save_path, size=(100, 100)):
    """
    创建等比例缩略图，然后裁剪到指定大小。
    :param image_path: 原始图片路径。
    :param size: 缩略图大小，格式为 (width, height)。
    """
    with Image.open(image_path) as img:
        # 获取图片的尺寸
        img_width, img_height = img.size

        # 等比例缩放
        aspect_ratio = max(size[0] / img_width, size[1] / img_height)
        new_width, new_height = int(img_width * aspect_ratio), int(img_height * aspect_ratio)
        img.thumbnail((new_width, new_height))  # 放大尺寸，确保宽或高至少有一个达到所需大小

        # 获取缩放后图片的尺寸
        img_width, img_height = img.size

        # 计算裁剪的位置
        left = (img_width - size[0]) // 2
        top = (img_height - size[1]) // 2
        right = (img_width + size[0]) // 2
        bottom = (img_height + size[1]) // 2

        # 裁剪图片
        img_cropped = img.crop((left, top, right, bottom))

        # 保存缩略图
        cut_dir(save_path)
        if img_cropped.mode in ['P', 'RGBA']:
            img_cropped = img_cropped.convert('RGB')
        img_cropped.save(save_path)
        if Config.ADD_WATERMARK:
            add_watermark(save_path)

def create_thumbnail_list(image_path):
    """
    生成缩略图列表
    :param image_path:
    :return:
    """
    thumbnail_list = []
    for thumbnail in Config.THUMBNAIL_SIZE:
        create_thumbnail(image_path, thumbnail.SAVE_PATH + os.path.basename(image_path), thumbnail.SIZE)
        thumbnail_list.append({
            'size': f"{thumbnail.SIZE[0]}x{thumbnail.SIZE[1]}",
            'path': thumbnail.SAVE_PATH + os.path.basename(image_path),
            "url": f"{Config.HTTP_ROOT_PATH}?filename={os.path.basename(image_path)}&size={thumbnail.SIZE[0]}x{thumbnail.SIZE[1]}"
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


