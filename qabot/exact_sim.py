"""
encode sentence to vector with multi-language model (include Chinese)
"""

import os
from functools import lru_cache

import requests
import numpy as np

ROBERTA_STS_URL = os.environ.get('ROBERTA_STS', 'http://localhost:13920/api/sim')


@lru_cache(maxsize=2000)
def exact_sim(a, b):
    ret = requests.post(ROBERTA_STS_URL, json={
        'a': a,
        'b': b
    }, timeout=30).json()
    return ret['prob']


if __name__ == '__main__':
    """
    python3 -m qabot.exact_sim
    """
    # for test and download model in Dockerfile
    import time
    start = time.time()
    a, b = '企业微信 如何修改我的欢迎语？', '如何修改我的欢迎语？'
    s = exact_sim(a, b)
    print(a)
    print(b)
    print('sim:', s)
    print('time', time.time() - start)
