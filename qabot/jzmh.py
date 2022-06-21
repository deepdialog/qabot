import requests # only for JZMH


def send_message(chatid, text, url = "https://ex-api.botorange.com/message/send", token=None, mention=None):
    """
    send message to jzmh
    """
    assert isinstance(token, str), 'Invalid token'
    jzmh_data = {
        "chatId":  chatid, # "6214b19ea66c67d78d0f133d",
        "token": token if token is not None else default_token,
        "messageType": 0, # MessageType, check below
        "payload": {
            "text": text, # str(return_data).replace('{',"").replace('}',"") ,
            "mention": [] if mention is None else mention # mention list, you can only set it when you send text message to room,
        },
        "externalRequestId": "",
    }
    if chatid == 'fake':
        return jzmh_data
    res = requests.post(url=url, json=jzmh_data, timeout=30)
    return res.json()
