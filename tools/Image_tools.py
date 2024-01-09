from pathlib import Path
from typing import Union
import requests
from io import BytesIO

from PIL import Image


class IM:
    def __init__(self, image: Union[str, Path, Image.Image]):
        if isinstance(image, Image.Image):
            self.image = image
        elif isinstance(image, str):
            # 判断是否为网络图片
            if image.startswith("http"):
                r = requests.get(image)
                self.image = Image.open(BytesIO(r.content))
            else:
                self.image = Image.open(image)
        elif isinstance(image, Path):
            self.image = Image.open(image)
        else:
            raise TypeError("image must be str, Path or Image.Image")

    # 图片裁剪
    def crop(self, size):
        """
        裁剪图片
        :param size: 裁剪的尺寸
        :return:
        """
        img = self.image
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
        self.image = img_cropped