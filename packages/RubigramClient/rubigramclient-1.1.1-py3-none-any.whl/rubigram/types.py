import rubigram
from typing import Literal
from json import dumps



class ForwardFrom:
    def __init__(self, data: dict):
        self.type_from: str = data["type_from"]
        self.message_id: str = data["message_id"]
        self.from_sender_id: str = data.get("from_sender_id")
        self.from_chat_id: str = data.get("from_chat_id")
    
    def _dict(self):
        return {
            "type_from": self.type_from,
            "message_id": self.message_id,
            "from_sender_id": self.from_sender_id,
            "from_chat_id": self.from_chat_id
        }

    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)
        
        
class File:
    def __init__(self, data: dict):
        self.file_id: str = data["file_id"]
        self.file_name: str = data.get("file_name")
        self.size: int = data.get("size")
    
    def _dict(self):
        return {"file_id": self.file_id, "file_name": self.file_name, "size": self.size}
        
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)
    
    
class Location:
    def __init__(self, data: dict):
        self.longitude: int = data["longitude"]
        self.latitude: int = data["latitude"]
    
    def _dict(self):
        return {"longitude": self.longitude, "latitude": self.latitude}
    
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)


class AuxData:
    def __init__(self, data: dict):
        self.start_id = data.get("start_id")
        self.button_id: str = data.get("button_id")
    
    def _dict(self):
        return {"start_id": self.start_id, "button_id": self.button_id}
    
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)
        
        
class MessageId:
    def __init__(self, data: dict):
        self.message_id = data["message_id"]
    
    def _dict(self):
        return {"message_id": self.message_id}
    
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)


class UpdateMessage:
    def __init__(self, data: dict):
        self.message_id: str = data["message_id"]
        self.text: str = data["text"]
        self.time: str = data["time"]
        self.is_edited: bool = data["is_edited"]
        self.sender_type: str = data["sender_type"]
        self.sender_id: str = data["sender_id"]
        
    def _dict(self):
        return {
            "message_id": self.message_id,
            "text": self.text,
            "time": self.time,
            "is_edited": self.is_edited,
            "sender_type": self.sender_type,
            "sender_id": self.sender_id
        }
        
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)


class NewMessage:
    def __init__(self, data: dict):
        self.message_id: str = data["message_id"]
        self.time: str = data["time"]
        self.is_edited: bool = data["is_edited"]
        self.sender_type: str = data["sender_type"]
        self.sender_id: str = data["sender_id"]
        self.text: str = data.get("text")
        self.forwarded_from: ForwardFrom = ForwardFrom(data["forwarded_from"]) if data.get("forwarded_from") else None
        self.file: File = File(data["file"]) if data.get("file") else None
        self.location: Location = Location(data["location"]) if data.get("location") else None
        self.aux_data: AuxData = AuxData(data["aux_data"]) if data.get("aux_data") else None

    def _dict(self):
        return {
            "message_id": self.message_id,
            "time": self.time,
            "is_edited": self.is_edited,
            "sender_type": self.sender_type,
            "sender_id": self.sender_id,
            "text": self.text,
            "forwarded_from": self.forwarded_from._dict() if self.forwarded_from else None,
            "file": self.file._dict() if self.file else None,
            "location": self.location._dict() if self.location else None,
            "aux_data": self.aux_data._dict() if self.aux_data else None
        }
        
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)
    

class InlineMessage:
    def __init__(self, data: dict):
        self.message_id: str = data["message_id"]
        self.chat_id: str = data["chat_id"]
        self.sender_id: str = data["sender_id"]
        self.text: str = data["text"]
        self.aux_data: AuxData = AuxData(data["aux_data"])
        self.location: Location = Location(data["location"]) if data.get("location") else None
    
    def _dict(self):
        return {
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "sender_id": self.sender_id,
            "text": self.text,
            "aux_data": self.aux_data._dict() if self.aux_data else None,
            "location":self.location._dict() if self.location else None
        }
        
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)


class Bot:
    def __init__(self, data: dict):
        self.bot_id: str = data["bot_id"]
        self.bot_title: str = data["bot_title"]
        self.username: str = data["username"]
        self.start_message: str = data["start_message"]
        self.share_url: str = data["share_url"]
        self.description: str = data["description"]
        self.avatar: File = File(data["avatar"]) if data.get("avatar") else None

    def _dict(self):
        return {
            "bot_id": self.bot_id,
            "bot_title": self.bot_title,
            "username": self.username,
            "start_message": self.start_message,
            "share_url": self.share_url,
            "description": self.description,
            "avatar": self.avatar._dict() if self.avatar else None
        }
    
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)


class Chat:
    def __init__(self, data: dict):
        self.chat_id: str = data["chat_id"]
        self.chat_type: str = data["chat_type"]
        self.user_id: str = data.get("user_id")
        self.first_name: str = data.get("first_name")
        self.last_name: str = data.get("last_name")
        self.title: str = data.get("title")
        self.username: str = data.get("username")
    
    def _dict(self):
        return {
            "chat_id": self.chat_id,
            "chat_type": self.chat_type,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "title" : self.title,
            "username": self.username
        }
        
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)
    

class Message:
    def __init__(self, client: "rubigram.Client", data: dict):
        # Message Update Type : ["NewMessage", "UpdatedMessage", "RemovedMessage", "StartedBot", "StoppedBot"و "UpdatedPayment"]
        self.client = client
        self.type: str = data["type"]
        self.chat_id: str = data["chat_id"]
        self.new_message: NewMessage = NewMessage(data.get("new_message")) if data.get("new_message") else None
        self.removed_message_id: int = data.get("removed_message_id")
        self.updated_message: UpdateMessage = UpdateMessage(data.get("updated_message")) if data.get("updated_message") else None
    
    def _dict(self):
        return {
            "type": self.type,
            "chat_id": self.chat_id,
            "new_message": self.new_message._dict() if self.new_message else None,
            "removed_message_id" : self.removed_message_id,
            "updated_message": self.updated_message._dict() if self.updated_message else None
        }
        
    def __str__(self):
        return dumps(self._dict(), indent=4, ensure_ascii=False)

    async def reply_text(self, text: str):
        return await self.client.send_message(self.chat_id, text, reply_to_message_id=self.new_message.message_id)
    
    async def reply_file(
        self,
        path: str,
        file_name: str,
        type: Literal["File", "Image", "Voice", "Music", "Gif", "Video"] = "File"
    ):
        return await self.client.send_file(self.chat_id, path, file_name, type)

    async def download(self, file_name: str):
        return await self.client.download_file(self.new_message.file.file_id, file_name)