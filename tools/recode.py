"""
返回值状态码
"""
import json

from flask import jsonify, Response

recode = {
    200: '成功',
    400: '用户名或密码错误',
    401: '参数错误',
    402: '信息验证失败，请重新登录',
    403: '未知用户',
    404: '信息不存在',
    405: '文件保存出错',
}

def json_recode(code, data=None):
    resout = {
        "code": code,
        "msg": recode[code],
        "data": data
    }
    response = Response(json.dumps(resout, ensure_ascii=False), content_type="application/json; charset=utf-8")
    return response