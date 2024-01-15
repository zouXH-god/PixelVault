from pathlib import Path
from typing import Union, List
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
        self.img_type = self.image.format.lower()
        self.quality = 100

    # 图片裁剪/缩放
    def crop(self, size):
        """
        裁剪/缩放 图片
        :param size: 裁剪/缩放 的尺寸
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


    # 图片添加水印
    def add_watermark(self, watermark: Union[str, Path, Image.Image], position: tuple = (0, 0)):
        """
        添加水印
        :param watermark: 水印图片
        :param position: 水印位置
        :return:
        """
        img = self.image
        watermark = IM(watermark)
        watermark.crop(img.size)
        img.paste(watermark.image, position, watermark.image)
        self.image = img

    # 图片旋转
    def rotate(self, angle: int):
        """
        图片旋转
        :param angle: 旋转角度
        :return:
        """
        img = self.image
        self.image = img.rotate(angle)

    # 图片压缩
    def compress(self, quality: int):
        """
        压缩图片
        :param quality: 图片质量（1-100），值越小压缩率越高
        :return:
        """
        # 验证图片质量值的有效性
        if not 1 <= quality <= 100:
            raise ValueError("图片质量必须在1到100之间")

        self.quality=quality

    # 图片拼接
    def concatenate(self, imgs: List[Image.Image], direction: str = "horizontal"):
        """
        图片拼接
        :param imgs: 图片列表
        :param direction: 拼接方向["horizontal", "vertical"]
        :return:
        """
        # 获取图片列表中最大的宽度和高度
        max_width = 0
        max_height = 0
        for img in imgs:
            if img.width > max_width:
                max_width = img.width
            if img.height > max_height:
                max_height = img.height

        # 创建一个空白图片
        if direction == "horizontal":
            new_img = Image.new("RGB", (max_width * len(imgs), max_height))
        elif direction == "vertical":
            new_img = Image.new("RGB", (max_width, max_height * len(imgs)))
        else:
            raise ValueError("direction must be horizontal or vertical")

        # 拼接图片
        for i, img in enumerate(imgs):
            if direction == "horizontal":
                new_img.paste(img, (i * max_width, 0))
            elif direction == "vertical":
                new_img.paste(img, (0, i * max_height))

        self.image = new_img

    # 获取图片
    def get_image(self, get_type = None):
        """
        获取图片
        :return:
        """
        if get_type == "bytes":
            img = self.image
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format=self.img_type, quality=self.quality)
            return img_byte_arr.getvalue()
        else:
            return self.image

    # 保存图片
    def save(self, path):
        """
        保存图片
        :param path: 保存路径
        :return:
        """
        self.image.save(path, format=self.img_type, quality=self.quality)