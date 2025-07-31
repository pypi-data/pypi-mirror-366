from Crypto.Cipher import AES
from gmssl import sm4
from lbTool.Common import base64_encode, base64_decode, hex_encode, hex_decode


class AesUtil:
    """
    AES加解密
    """

    @staticmethod
    def encrypt_cbc(key, iv, plaintext):
        """
        加密
        :param key: 密钥
        :param iv: 偏移向量
        :param plaintext: 待加密字符串
        :return: 加密后二进制数据
        """
        # 字符串补位
        data = AesUtil.__pad(plaintext)
        # 初始化加密器
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, iv.encode('utf8'))
        # 加密后得到的是bytes类型的数据
        encrypt_bytes = cipher.encrypt(data.encode('utf8'))
        return encrypt_bytes
        # # 使用Base64进行编码,返回byte字符串
        # encode_strs = base64.b64encode(encrypt_bytes)
        # # 对byte字符串按utf-8进行解码
        # ciphertext = encode_strs.decode('utf8')
        # return ciphertext

    @staticmethod
    def decrypt_cbc(key, iv, cipher_bytes):
        """
        解密
        :param key: 密钥
        :param iv: 偏移向量
        :param cipher_bytes: 加密串二进制数据
        :return: 解密后字符串
        """
        # # 对字符串按utf-8进行编码
        # data = ciphertext.encode('utf8')
        # # 将加密数据转换位bytes类型数据
        # decode_bytes = base64.decodebytes(data)
        # 初始化加密器
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, iv.encode('utf8'))
        # 解密
        text_decrypted = cipher.decrypt(cipher_bytes)
        # 去补位
        text_decrypted = AesUtil.__un_pad(text_decrypted)
        # 对byte字符串按utf-8进行解码
        plaintext = text_decrypted.decode('utf8')
        return plaintext

    @staticmethod
    def __pad(s):
        """
        字符串补位
        :param s: 待处理字符串
        :return:
        """
        return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

    @staticmethod
    def __un_pad(s):
        """
        去掉字符串最后一个字符
        :param s: 待处理字符串
        :return:
        """
        return s[0:-s[-1]]


class Sm4Util:
    """
    SM4加解密
    """

    @staticmethod
    def encrypt_ecb(key, plaintext):
        """
        加密
        :param key: 密钥
        :param plaintext: 待加密字符串
        :return: 二进制加密数据
        """
        sm4_alg = sm4.CryptSM4()  # 实例化sm4
        sm4_alg.set_key(key.encode(), sm4.SM4_ENCRYPT)  # 设置密钥
        datastr = str(plaintext)
        res = sm4_alg.crypt_ecb(datastr.encode('utf8'))  # 开始加密,bytes类型，ecb模式
        return res
        # # 加密后得到的是bytes类型的数据
        # encode_strs = base64.b64encode(res)
        # # 使用Base64进行编码,返回byte字符串
        # ciphertext = encode_strs.decode('utf8')
        # return ciphertext  # 返回加密串

    @staticmethod
    def decrypt_ecb(key, cipher_bytes):
        """
        解密
        :param key: 密钥
        :param cipher_bytes: 加密串二进制
        :return: 解密后字符串
        """
        # ciphertext = ciphertext.encode('utf8')
        # encode_bytes = base64.decodebytes(ciphertext)
        sm4_alg = sm4.CryptSM4()  # 实例化sm4
        sm4_alg.set_key(key.encode(), sm4.SM4_DECRYPT)  # 设置密钥
        res = sm4_alg.crypt_ecb(cipher_bytes)  # 开始解密。十六进制类型,ecb模式
        plaintext = res.decode('utf8')
        return plaintext


if __name__ == '__main__':
    text = "123"
    print()
    aes_key = "91a055ac42b41132"
    aes_iv = "b5a836c453b982a2"
    aes_cipher_bytes = AesUtil.encrypt_cbc(aes_key, aes_iv, text)
    aes_ciphertext = base64_encode(aes_cipher_bytes)
    print("AES加密后===", aes_ciphertext)
    aes_plaintext = AesUtil.decrypt_cbc(aes_key, aes_iv, base64_decode(aes_ciphertext, True))
    print("AES解密后===", aes_plaintext)

    sm4_key = "86C63180C2806ED1"
    sm4_cipher_bytes = Sm4Util.encrypt_ecb(sm4_key, text)
    sm4_ciphertext = base64_encode(sm4_cipher_bytes)
    # sm4_ciphertext = hex_encode(sm4_cipher_bytes)
    print("SM4加密后===", sm4_ciphertext)
    sm4_plaintext = Sm4Util.decrypt_ecb(sm4_key, base64_decode(sm4_ciphertext, True))
    # sm4_plaintext = Sm4Util.decrypt_ecb(sm4_key, hex_decode(sm4_ciphertext, True))
    print("SM4解密后===", sm4_plaintext)
