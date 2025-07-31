import base64
import binascii
import codecs
import hashlib
import os
import sys
import xml.etree.ElementTree as et


def str_to_md5(text):
    """
    字符串MD5加密
    :param text: 明文
    :return:
    """
    # 创建一个 MD5 对象
    md5 = hashlib.md5()
    # 将文本转换为二进制，并进行加密
    md5.update(text.encode('utf-8'))
    # 获取加密后的结果，以十六进制表示
    encrypted_text = md5.hexdigest()

    return encrypted_text


def byte_to_md5(binary):
    """
    字节MD5加密
    :param binary: 字节数组
    :return:
    """
    # 创建一个 MD5 对象
    md5 = hashlib.md5()
    # 填充文本二进制
    md5.update(binary)
    # 获取加密后的结果，以十六进制表示
    encrypted_text = md5.hexdigest()

    return encrypted_text


def parse_xml_config(xml_file_path, element_name):
    """
    解析XML
    :param xml_file_path: xml文件路径
    :param element_name: 节点名称
    :return:
    """
    # 解析 XML 文件
    tree = et.parse(xml_file_path)
    root = tree.getroot()

    # 获取数据库连接串参数
    params_obj = {}
    for elem in root.findall(f".//{element_name}/*"):
        params_obj[elem.tag] = elem.text

    return params_obj


def get_file_path(relative_path):
    """
    获取资源绝对路径(可用于打包后资源路径获取)
    :param relative_path: 资源根目录路径
    :return:
    """
    try:
        # pyinstaller打包后的路径 如果是打包成单一exe文件，便用此路径
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")  # 当前工作目录的路径
    return os.path.normpath(os.path.join(base_path, relative_path))  # 返回实际路径


def base64_encode(raw_data, ret_bytes=False, charset="utf-8"):
    # type: (str|bytes|bytearray, bool, str) -> str|bytes
    """
    Base64加密
    :param raw_data: 待加密数据
    :param ret_bytes: 是否返回byte数据
    :param charset:  字符编码：utf-8,gbk
    :return:
    """
    if isinstance(raw_data, str):
        raw_data = raw_data.encode(charset)
    elif isinstance(raw_data, (bytes, bytearray)):
        raw_data = raw_data
    else:
        raise ValueError("暂不支持的转换类型。")
    base64_str = base64.b64encode(raw_data)
    if ret_bytes is False:
        base64_str = base64_str.decode(charset)
    return base64_str


def base64_decode(raw_data, ret_bytes=False, charset="utf-8"):
    # type: (str|bytes|bytearray, bool, str) -> str|bytes
    """
    Base64解密
    :param raw_data: 待解密数据
    :param ret_bytes: 是否返回byte数据
    :param charset:  字符编码：utf-8,gbk
    :return:
    """
    raw_str = base64.b64decode(raw_data)
    if ret_bytes is False:
        raw_str = raw_str.decode(charset)
    return raw_str


def unicode_encode(raw_data, charset="utf-8"):
    # type: (str, str) -> str
    """
    unicode编码
    :param raw_data: 原始数据
    :param charset: 字符编码
    :return:
    """
    return codecs.encode(raw_data, 'unicode_escape').decode(charset)


def unicode_decode(raw_data, charset="utf-8"):
    # type: (str|bytes|bytearray, str) -> str
    """
    unicode解码
    :param raw_data: 原始数据
    :param charset: 字符编码
    :return:
    """
    if isinstance(raw_data, str):
        raw_data = raw_data.encode(charset)
    elif isinstance(raw_data, (bytes, bytearray)):
        raw_data = raw_data
    else:
        raise ValueError("暂不支持的转换类型。")
    return codecs.decode(raw_data, 'unicode_escape')


def hex_encode(raw_data, ret_bytes=False, charset="utf8"):
    # type: (str|bytes|bytearray, bool, str) -> str|bytes
    """
    16进制编码
    :param raw_data: 原始数据
    :param ret_bytes: 是否返回字节数组
    :param charset: 返回字符串编码
    :return:
    """
    if isinstance(raw_data, str):
        raw_data = raw_data.encode(charset)
    elif isinstance(raw_data, (bytes, bytearray)):
        raw_data = raw_data
    else:
        raise ValueError("暂不支持的转换类型。")
    hex_bytes = binascii.hexlify(raw_data)
    if ret_bytes is True:
        return hex_bytes
    return hex_bytes.decode(charset)


def hex_decode(hex_str, ret_bytes=False, charset="utf8"):
    # type: (str, bool, str) -> str|bytes
    """
    16进制解码
    :param hex_str: 16进制字符串
    :param ret_bytes: 是否返回字节数组
    :param charset: 返回字符串编码
    :return:
    """
    hex_bytes = binascii.unhexlify(hex_str)
    if ret_bytes is True:
        return hex_bytes
    return hex_bytes.decode(charset)
