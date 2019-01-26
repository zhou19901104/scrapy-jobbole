# -*- coding:utf-8 -*-

import hashlib

def get_md5(url):
    # 如果是unicode编码，先进行转码
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    pass