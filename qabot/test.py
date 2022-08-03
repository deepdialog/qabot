
from tqdm import tqdm
from open_search import client, index_name

token = '61ef6cf9f576f0d95bae388a'


hits = client.search(index=index_name, body={
    '_source': ['question'],
    'query': {
        'bool': {
            'filter': {
                'term': {
                    'token': token
                }
            }
        }
    },
    'size': 10000
})

hits = hits['hits']['hits']

question_id = {}
for x in hits:
    q = x['_source']['question']
    i = x['_id']
    if q not in question_id:
        question_id[q] = [i]
    else:
        question_id[q].append(i)

dup = {k: v for k, v in question_id.items() if len(v) > 1}

for k, v in tqdm(dup.items()):
    for _id in v[1:]:
        client.delete(index=index_name, id=_id)
