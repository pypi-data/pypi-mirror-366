# -*- coding: utf-8 -*-
"""加密相关工具类，从原encrypt.py移植"""

import execjs
import requests
import random
import base64
import codecs
import json
from Crypto.Cipher import AES


def to_16(key):
    """将密钥填充到16的倍数"""
    while len(key) % 16 != 0:
        key += '\0'
    return str.encode(key)


def AES_encrypt(text, key, iv):
    """AES加密"""
    bs = AES.block_size
    def pad2(s): return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
    encryptor = AES.new(to_16(key), AES.MODE_CBC, to_16(iv))
    encrypt_aes = encryptor.encrypt(str.encode(pad2(text)))
    encrypt_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
    return encrypt_text


def RSA_encrypt(text, pubKey, modulus):
    """RSA加密"""
    text = text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'),
             16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def set_user_agent():
    """随机选择User-Agent"""
    USER_AGENTS = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.4705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
    ]
    return random.choice(USER_AGENTS)


# 获取随机字符串的JavaScript函数
get_random_string = execjs.compile(r"""
    function a(a) {
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)
            e = Math.random() * b.length,
            e = Math.floor(e),
            c += b.charAt(e);
        return c
    }
""")


class WanYiYun:
    """网易云音乐加密工具类"""
    
    def __init__(self):
        self.song_url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
        self.g = '0CoJUm6Qyw8W8jud'
        self.b = "010001"
        self.c = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.i = get_random_string.call('a', 16)  # 随机生成长度为16的字符串
        self.iv = "0102030405060708"  # 偏移量

    def get_params(self, music_id):
        """生成请求参数"""
        encText = str({'ids': "[" + str(music_id) + "]",
                      'br': 128000, 'csrf_token': ""})
        return AES_encrypt(AES_encrypt(encText, self.g, self.iv), self.i, self.iv)

    def get_encSecKey(self):
        """生成加密的安全密钥"""
        return RSA_encrypt(self.i, self.b, self.c)

    def getDownloadUrl(self, music_id, cookie):
        """获取歌曲下载链接"""
        headers = {
            'User-Agent': set_user_agent(),
            'Referer': 'https://music.163.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cookie': cookie,
        }
        
        formdata = {
            'params': self.get_params(music_id),
            'encSecKey': self.get_encSecKey()
        }
        
        try:
            response = requests.post(self.song_url, headers=headers, data=formdata)
            result = json.loads(response.content)
            return result["data"][0]["url"]
        except Exception as e:
            print(f'获取下载链接失败: {e}')
            return None
