
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
from .exact_sim import exact_sim
from .jzmh import send_message


def get_answer(question, token, size=5):
    hits = client.search(index=index_name, body={
        "_source": [
            "question",
            "answer",
            "parent",
            "url",
            "created_at",
            "updated_at"
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
        },
        "size": size
    })
    rets = []
    for obj in hits['hits']['hits']:
        s = obj['_source']
        s['id'] = obj['_id']
        s['score'] = obj['_score']
        s['exact_score'] = exact_sim(question, s['question'])
        rets.append(obj['_source'])
    return rets


def make_answer(rets):
    if len(rets) <= 0:
        return ''
    if rets[0]['score'] > 0.8 or rets[0]['exact_score'] > 0.5:
        a = rets[0]
        text = f'''{a["question"]}
{a["answer"]}'''
    else:
        text = f'''没有找到精确匹配的回答，你问的是下面几个问题吗？

{rets[0]["question"].strip()}'''
        if len(rets) > 1:
            text += f'\n{rets[1]["question"].strip()}'
        if len(rets) > 2:
            text += f'\n{rets[2]["question"].strip()}'
    return text


@app.post('/api/qabot/ask/{token}')
async def api_qabot_ask(token: str, request: Request):
    """提问

    curl localhost:8000/api/qabot/ask/test_token \
        -H 'Content-Type: application/json' \
        -d '{"question": "吃了"}'
    """
    body = await request.json()
    question = body.get('question')
    rets = get_answer(question, token)
    
    return {
        'ok': True,
        'data': rets,
        'text': make_answer(rets)
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
            "created_at",
            "updated_at"
        ],
        "query": {
            "term": {
                "token": token
            }
        },
        "from": page * page_size,
        "size": page_size,
        "track_total_hits": True,
        "sort" : [
            { "updated_at" : "desc" }
        ]
    })
    total = hits['hits']['total']['value']
    rets = []
    for obj in hits['hits']['hits']:
        obj['_source']['id'] = obj['_id']
        rets.append(obj['_source'])
    return {
        'ok': True,
        'data': rets,
        'total': total,
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
    
    hits = client.search(index=index_name, body={
        '_source': ['question'],
        'query': {
            'bool': {
                'filter': {
                    'term': {
                        'token': token
                    }
                },
                'must': {
                    'term': {
                        'question.keyword': question
                    }
                }
            }
        }
    })

    _id = str(uuid4())
    exists = False
    if hits['hits']['total']['value'] > 0:
        _id = hits['hits']['hits'][0]['_id']
        exists = True

    now = str(datetime.now()).replace(' ', 'T')[:19]
    ret = client.index(index=index_name, id=_id, body={
        'token': token,
        'question': question,
        'answer': answer,
        'parent': parent,
        'url': url,
        'question_vec': encode(question),
        'created_at': now,
        'updated_at': now,
    }, refresh='wait_for')
    client.indices.refresh(index_name)
    print('create', ret)
    if ret.get('result') == 'created':
        return {
            'ok': True,
            'exists': exists,
        }
    else:
        return {
            'ok': False,
            'error': '未知错误',
            'exists': exists,
        }
    

@app.put('/api/qabot/pair/{token}/{_id}')
async def api_qabot_put(token: str, _id: str, request: Request):
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
    now = str(datetime.now()).replace(' ', 'T')[:19]
    ret = client.update(index=index_name, id=_id, body={
        'doc': {
            'question': question,
            'answer': answer,
            'parent': parent,
            'url': url,
            'question_vec': encode(question),
            'updated_at': now,
        }
    }, refresh='wait_for')
    client.indices.refresh(index_name)
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
    client.delete_by_query(index=index_name, body={
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
    client.indices.refresh(index_name)
    # client.cluster.health(wait_for_no_relocating_shards=True, wait_for_active_shards='all')
    print('delete', ret)
    if ret.get('result') == 'deleted':
        return {
            'ok': True,
        }
    else:
        return {
            'ok': False,
            'error': '未知错误',
        }

@app.post("/api/qabot/message")
async def receive_message(item: Item_jzmh, request: Request):
    """对接句子互动的api
    curl -XPOST localhost:1333/api/qabot/message -H 'Content-Type: application/json' \
        -d '{
            "data": { "payload": { "text": "hello" }, "chatId": "fake" }
        }'
    """
    print('receive message', datetime.now(), f'"{item.data.payload.text}"')
    token = item.data.token
    question = item.data.payload.text
    # 去除群聊的at信息
    if question.startswith('@'):
        question = re.sub(r'^@[^\s]+\s', '', question)
    rets = get_answer(question, token)
    text = make_answer(rets)
    mention = []
    is_group = not not item.data.roomId
    if is_group:
        mention = [item.data.contactId]
    ret = send_message(chatid=item.data.chatId, text=text, token=token, mention=mention)
    print('response message', datetime.now())
    return ret


@app.get('/')
async def hello_world():
    return {'hello': 'world'}
