import json
from typing import Literal

from pydantic import BaseModel, model_validator

from .base import EndPointKit, api

ReceiveIdType = Literal["open_id", "user_id", "union_id", "email", "chat_id"]

# text: 文本
# post: 富文本
# image: 图片
# file: 文件
# audio: 语音
# media: 视频
# sticker: 表情包
# interactive: 卡片
# share_chat: 分享群名片
# share_user: 分享个人名片
# system: 系统消息
MessageType = Literal[
    "text", "post", "image", "file", "audio", "media", "sticker", "interactive", "share_chat", "share_user", "system"
]


class MessageBody(BaseModel):
    content: str


class Sender(BaseModel):
    id: str
    id_type: str
    sender_type: str
    tenant_key: str


class Mention(BaseModel):
    key: str
    id: str
    id_type: str
    name: str
    tenant_key: str


class Message(BaseModel):
    message_id: str
    root_id: str = ""
    parent_id: str = ""
    thread_id: str = ""
    msg_type: str
    create_time: str
    update_time: str
    deleted: bool
    updated: bool
    chat_id: str
    sender: Sender
    body: MessageBody
    mentions: list[Mention] = None
    upper_message_id: str = ""


class SendReq(BaseModel):
    receive_id: str
    msg_type: MessageType
    content: str
    uuid: str = ""

    @model_validator(mode="after")
    def check(self):
        try:
            json.loads(self.content)
        except json.JSONDecodeError as exc:
            raise ValueError("content must be json string") from exc


class Messages(EndPointKit):
    @api("/im/v1/messages")
    def send(self, receive_id_type: ReceiveIdType, body: SendReq) -> Message:
        """
        https://open.larkoffice.com/document/server-docs/im-v1/message/create

        :param receive_id_type:
        :param body:
        :return:
        """


if __name__ == "__main__":
    data = {
        "body": {"content": '{"text":"hello"}'},
        "chat_id": "oc_0eda4802cbc508bc39c3d912a677163a",
        "create_time": "1753091888390",
        "deleted": False,
        "message_id": "om_x100b48d4bdc9a8ac0f1349b6ad8d477",
        "msg_type": "text",
        "sender": {
            "id": "cli_a65f8ab154f6d00e",
            "id_type": "app_id",
            "sender_type": "app",
            "tenant_key": "736588c9260f175d",
        },
        "update_time": "1753091888390",
        "updated": False,
    }
    Message.model_validate(data)
