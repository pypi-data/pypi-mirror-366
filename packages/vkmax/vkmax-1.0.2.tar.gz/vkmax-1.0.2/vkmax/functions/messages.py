from random import randint
from vkmax.client import MaxClient


async def send_message(
    client: MaxClient,
    chat_id: int,
    text: str,
    notify: bool = True
):
    """Sends message to specified chat"""

    return await client.invoke_method(
        opcode=64,
        payload={
            "chatId": chat_id,
            "message": {
                "text": text,
                "cid": randint(1750000000000, 2000000000000),
                "elements": [],
                "attaches": []
            },
            "notify": notify
        }
    )


async def edit_message(
    client: MaxClient,
    chat_id: int,
    message_id: int,
    text: str
):
    """Edits the specified message"""

    return await client.invoke_method(
        opcode=67,
        payload={
            "chatId": chat_id,
            "messageId": str(message_id),
            "text": text,
            "elements": [],
            "attachments": []
        }
    )

async def delete_message(
    client: MaxClient,
    chat_id: int,
    message_ids: list,
    delete_for_me: bool = False
):
    """ Deletes the specified message """

    return await client.invoke_method(
        opcode=66,
        payload={
            "chatId": chat_id,
            "messageIds": message_ids,
            "forMe": delete_for_me
        }
    )

async def pin_message(
    client: MaxClient,
    chat_id: int,
    message_id: int,
    notify = False
):
    """Pins message in the chat"""

    return await client.invoke_method(
        opcode=55,
        payload={
            "chatId": chat_id,
            "notifyPin": notify,
            "pinMessageId": str(message_id)
        }
    )


async def reply_message(
    client: MaxClient,
    chat_id: int,
    text: str,
    reply_to_message_id: int,
    notify = True
):
    """Replies to message in the chat"""
    
    return await client.invoke_method(
        opcode=64,
        payload={
            "chatId": chat_id,
            "message": {
                "text": text,
                "cid": randint(1750000000000, 2000000000000),
                "elements": [],
                "link": {
                    "type": "REPLY",
                    "messageId": str(reply_to_message_id)
                },
                "attaches": []
            },
            "notify": notify
        }
    )
