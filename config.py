from typing import List


class THUMBNAIL:
    def __init__(self, size: tuple, STATIC_FOLDER=None):
        self.SIZE = size
        self.SAVE_PATH = f'{STATIC_FOLDER}images/treatment'


class Config:
    # http服务配置
    HOST = '0.0.0.0'
    PORT = 6501
    DEBUG = True
    # 图片服务配置
    HTTP_ROOT_PATH = '/api/img'
    STATIC_FOLDER = 'app/static/'
    # 允许上传的图片类型
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico'}
    # 原图上传位置
    UPLOAD_FOLDER = STATIC_FOLDER + 'images/original'
    # 处理后图片保存位置
    TREATMENT_SAVE_PATH = f'{STATIC_FOLDER}images/treatment'
    # 缩略图列表，按需填写，不填写则不生成缩略图
    THUMBNAIL_SIZE: List[THUMBNAIL] = [
        THUMBNAIL((100, 100), STATIC_FOLDER),
        THUMBNAIL((300, 300), STATIC_FOLDER),
        THUMBNAIL((400, 400), STATIC_FOLDER),
        THUMBNAIL((300, 200), STATIC_FOLDER),
        THUMBNAIL((600, 400), STATIC_FOLDER),
        THUMBNAIL((300, "auto"), STATIC_FOLDER),
    ]
    # 添加水印
    ADD_WATERMARK = False
    WATERMARK_PATH = STATIC_FOLDER + 'images/watermark/log_w.png'
    # MySQL数据库URI
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://PixelVault:7NGTSXrrweTrXft6@localhost/pixelvault'


