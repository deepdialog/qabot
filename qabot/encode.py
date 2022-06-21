"""
encode sentence to vector with multi-language model (include Chinese)
"""

import os
from functools import lru_cache

import requests
import numpy as np

STS_URL = os.environ.get('STS', 'http://localhost:13910/api/encode')
# 一个magic number，用来调整相似度的值域
adjust = [-0.31587389264421867, 1.461716485701409]


@lru_cache(maxsize=2000)
def encode(x):
    # import time
    # start = time.time()
    ret = requests.post(STS_URL, json={
        'text': x
    }, timeout=30).json()['data']
    # print('encode', x, time.time() - start)
    return ret


@lru_cache(maxsize=2000)
def sim(a, b):
    va = encode(a)
    vb = encode(b)
    va, vb = np.array(va), np.array(vb)
    s = np.dot(va, vb) / (np.sqrt(np.sum(va ** 2)) * np.sqrt(np.sum(vb ** 2)))
    s = np.clip(s + adjust[0], 0, 10) * adjust[1]
    s = float(s)
    return s


def detail_sim(a, b):
    maxs = [sim(a, b)]
    for x in a.split(' '):
        if len(x) >= 2:
            s = sim(x, b)
            maxs.append(s)
    # for x in jieba.lcut(a):
    #     if len(x) >= 2:
    #         s = sim(x, b)
    #         maxs.append(s)
    return max(maxs)


if __name__ == '__main__':
    """
    python3 -m qabot.encode
    """
    # for test and download model in Dockerfile
    ret = encode('test')
    print(len(ret))
    import time
    start = time.time()
    a, b = '企业微信 如何修改我的欢迎语？', '如何修改我的欢迎语？'
    s = detail_sim(a, b)
    print(a)
    print(b)
    print('sim:', s)
    print('time', time.time() - start)
