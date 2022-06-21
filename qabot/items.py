from typing import Optional
from pydantic import BaseModel

# 暂时仅仅处理文字 
class Payload_Struct(BaseModel):
    # text:Optional[str] = ""
    text:str

class Item_jzmh_data(BaseModel):
    messageId: Optional[str] = ""
    chatId: Optional[str] = "" # juzi system chatId
    avatar: Optional[str] = ""
    roomTopic: Optional[str] = ""
    roomId: Optional[str] = "" # room wxid nullable
    contactName: Optional[str] = "" # message conact name
    contactId: Optional[str] = ""
    payload: Optional[Payload_Struct] = ""
    # payload: Optional[Payload_Struct] = None
    type: Optional[str] = ""
    timestamp: Optional[int] = "" # message timestamp
    token: Optional[str] = "" # token
    botId: Optional[str] = "" # botId
    contactType: Optional[int] = ""
    coworker: Optional[bool] = "" # is coworker or not
    botId: Optional[str] = ""
    botWxid: Optional[str] = ""
    botWeixin: Optional[str] = ""

class Item_jzmh(BaseModel):
    data:Optional[Item_jzmh_data]= ""
