import os
import time
from io import BytesIO

from PIL.Image import Image as PILImage

from config import Config
from db import Image, ProcessedImage, db


# 将数据上传数据库，并返回id
def update_db(image: PILImage, file_type: str = "jpeg", original_name: str = None, processing_method: str = None, image_id: int = None):
    file_type = file_type.lower()
    # 拼接文件名
    timestamp = time.time()
    saved_name = f"{timestamp}.{file_type}"
    # 获取当天日期 作为文件夹名
    date = time.strftime("%Y-%m-%d", time.localtime(timestamp))
    # 获取图片大小（字节）
    img_io = BytesIO()
    if file_type == "jpg":
        file_type = "jpeg"
    image.save(img_io, file_type)
    img_size = img_io.tell()
    # 上传数据库
    if original_name:
        save_path = os.path.join(Config.UPLOAD_FOLDER, date, saved_name)
        im = Image(
            original_name=original_name,
            saved_name=saved_name,
            size=img_size,
            space_used=img_size,
            width=image.width,
            height=image.height,
            original_url=save_path,
            uploader_id=1
        )
    elif processing_method and image_id:
        save_path = os.path.join(Config.TREATMENT_SAVE_PATH, date, saved_name)
        im = ProcessedImage(
            image_id=image_id,
            saved_name=saved_name,
            processing_method=processing_method,
            url=save_path,
            space_used=img_size,
            size=img_size,
            width=image.width,
            height=image.height
        )
    else:
        raise ValueError("original_name or processing_method must be specified.")

    # 提交数据库
    db.session.add(im)
    db.session.commit()

    # 返回id
    return save_path, im.id