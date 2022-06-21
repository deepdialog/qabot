
import os
import re
import traceback
from datetime import datetime
from uuid import uuid4

from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from .app import app
from .items import Item_jzmh
from .open_search import client, index_name
from .encode import encode


def get_answer(question):
    hits = client.search(index=index_name, body={
        "_source": [
            "question",
            "answer",
            "parent",
            "url",
        ],
        "query": {
            "bool": {
                "filter": [ # 这里用filter，避免计入分数
                    {
                        "term": {
                            "token": token
                        }
                    }
                ],
                "should": [
                    {
                        "knn": {
                            "question_vec": {
                                "vector": encode(question),
                                "k": 10,
                            }
                        }
                    }
                ]
            }
        }
    })
    rets = []
    for obj in hits['hits']['hits']:
        obj['_source']['id'] = obj['_id']
        obj['_source']['score'] = obj['_score']
        rets.append(obj['_source'])
    return rets


@app.post('/api/qabot/ask/{token}')
async def api_qabot_ask(token: str, request: Request):
    """提问

    curl localhost:8000/api/qabot/ask/test_token \
        -H 'Content-Type: application/json' \
        -d '{"question": "吃了"}'
    """
    body = await request.json()
    question = body.get('question')
    rets = get_answer(question)
    
    return {
        'ok': True,
        'data': rets,
    }


@app.get('/api/qabot/pair/{token}')
@app.get('/api/qabot/pair/{token}/{page}/{page_size}')
async def api_qabot_post(token: str='', page: int=0, page_size: int=10):
    """获取
    
    curl localhost:8000/api/qabot/pair/test_token
    """
    hits = client.search(index=index_name, body={
        "_source": [
            "question",
            "answer",
            "parent",
            "url",
        ],
        "query": {
            "term": {
                "token": token
            }
        },
        "from": page * page_size,
        "size": page_size
    })
    rets = []
    for obj in hits['hits']['hits']:
        obj['_source']['id'] = obj['_id']
        rets.append(obj['_source'])
    return {
        'ok': True,
        'data': rets,
    }


@app.post('/api/qabot/pair/{token}')
async def api_qabot_post(token: str, request: Request):
    """添加
    
    curl -XPOST localhost:8000/api/qabot/pair/test_token \
        -H 'Content-Type: application/json' \
        -d '{"question": "吃了吗", "answer": "没吃呢", "url": ""}'
    """
    if not isinstance(token, str) or len(token) <= 0:
        return {
            'ok': False,
            'error': 'Invalid token'
        }
    body = await request.json()
    question = body.get('question')
    answer = body.get('answer')
    parent = body.get('parent')
    url = body.get('url')
    if not isinstance(question, str):
        return {
            'ok': False,
            'error': 'Invalid question'
        }
    if not isinstance(answer, str):
        return {
            'ok': False,
            'error': 'Invalid answer'
        }
    _id = str(uuid4())
    ret = client.index(index=index_name, id=_id, body={
        'token': token,
        'question': question,
        'answer': answer,
        'parent': parent,
        'url': url,
        'question_vec': encode(question),
    })
    print(ret)
    return {
        'ok': True,
    }
    

@app.put('/api/qabot/pair/{token}')
async def api_qabot_put(token: str, request: Request):
    """修改
    
    curl -XPUT localhost:8000/api/qabot/pair/test_token \
        -H 'Content-Type: application/json' \
        -d '{"id": "930ab216-706e-4e64-a08c-16703f5ad3ee", "question": "吃了吗", "answer": "没吃呢啊", "url": ""}'
    """
    if not isinstance(token, str) or len(token) <= 0:
        return {
            'ok': False,
            'error': 'Invalid token'
        }
    body = await request.json()
    _id = body.get('id')
    question = body.get('question')
    answer = body.get('answer')
    parent = body.get('parent')
    url = body.get('url')
    if not isinstance(_id, str):
        return {
            'ok': False,
            'error': 'Invalid id'
        }
    if not isinstance(question, str):
        return {
            'ok': False,
            'error': 'Invalid question'
        }
    if not isinstance(answer, str):
        return {
            'ok': False,
            'error': 'Invalid answer'
        }
    ret = client.index(index=index_name, id=_id, body={
        'token': token,
        'question': question,
        'answer': answer,
        'parent': parent,
        'url': url,
        'question_vec': encode(question),
    })
    print(ret)
    return {
        'ok': True,
    }
    

@app.delete('/api/qabot/pair/{token}/{_id}')
async def api_qabot_delete(token: str='', _id: str=''):
    """删除
    curl -XDELETE localhost:8000/api/qabot/pair/test_token/930ab216-706e-4e64-a08c-16703f5ad3ee
    """
    # 删除问题
    ret = client.delete(index=index_name, id=_id)
    print(ret)
    # 删除子问题
    ret = client.delete_by_query(index=index_name, body={
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "token": token
                        }
                    },
                    {
                        "term": {
                            "parent": _id
                        }
                    }
                ]
            }
        }
    })
    print(ret)
    return {
        'ok': True,
    }

@app.post("/api/qabot/message")
async def receive_message(item: Item_jzmh, request: Request):
    """对接句子互动的api
    curl -XPOST localhost:1333/api/qabot/message -H 'Content-Type: application/json' \
        -d '{
            "data": { "payload": { "text": "hello" }, "chatId": "fake" }
        }'
    """
    print('receive message', datetime.now())
    token = item.data.token
    ...

@app.get('/')
async def hello_world():
    return {'hello': 'world'}
