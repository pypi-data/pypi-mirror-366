from rubigram.types import Message, InlineMessage, MessageId, Chat, Bot
from aiohttp import ClientSession, FormData, web
from typing import Literal
import aiofiles


class Client:
    def __init__(self, token: str, webhook_url: str = "0.0.0.0", port: int = 5000):
        self.token = token
        self.webhook = webhook_url
        self.port = port
        self.messages_handler = []
        self.api = "https://botapi.rubika.ir/v3"
    
    async def request(self, method: str, data: dict):
        async with ClientSession() as session:
            async with session.post(f"{self.api}/{self.token}/{method}", json=data) as response:
                return await response.json()
    
    def on_message(self, *filters):
        def decorator(func):
            async def wrapped(client, update):
                if all(f(update) for f in filters):
                    await func(client, update)
            self.messages_handler.append(wrapped)
            return func
        return decorator
    
    async def update(self, data: dict):
        update_object = Message(self, data["update"]) if data.get("update") else InlineMessage(data["inline_message"])
        for handler in self.messages_handler:
            await handler(self, update_object)
            
    
    async def get_me(self) -> "Bot":
        response = await self.request("getMe", {})
        return Bot(response["data"]["bot"])
    
    
    async def get_chat(self, chat_id: str) -> "Chat":
        response = await self.request("getChat", {"chat_id": chat_id})
        return Chat(response["data"])

    
    async def get_updates(self, limit: int = 1, offset_id: str = None):
        response = await self.request("getUpdates", {"limit": limit, "offset_id": offset_id})
        return response
    
    
    async def set_command(self, commands: list):
        response = await self.request("setCommands", {"bot_commands": commands})
        return response
    
    
    async def update_bot_endpoint(
        self,
        url: str,
        type: Literal["ReceiveUpdate", "ReceiveInlineMessage", "ReceiveQuery", "GetSelectionItem", "SearchSelectionItems"]
    ):
        response = await self.request("updateBotEndpoints", {"url": url, "type": type})
        return response
    
    
    async def send_message(
        self,
        chat_id: str,
        text: str,
        chat_keypad = None, # مشخص کردن تایپ
        inline_keypad = None, # مشخص کردن تایپ
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = None,
        reply_to_message_id = None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "text": text,
            "chat_keypad": chat_keypad,
            "inline_keypad": inline_keypad,
            "chat_keypad_type": chat_keypad_type,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id
        }
        response = await self.request("sendMessage", data)
        return MessageId(response["data"])

    
    async def send_poll(
        self,
        chat_id: str,
        question: str,
        options: list[str],
        chat_keypad = None, # مشخص کردن تایپ
        inline_keypad = None, # مشخص کردن تایپ
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal[None, "New", "Remove"] = None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "chat_keypad": chat_keypad,
            "inline_keypad": inline_keypad,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        response = await self.request("sendPoll", data)
        return MessageId(response["data"])
    
    
    async def send_location(
        self,
        chat_id: str,
        latitude: str,
        longitude: str,
        chat_keypad = None, # مشخص کردن تایپ
        inline_keypad = None, # مشخص کردن تایپ
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal[None, "New", "Remove"] = None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "chat_keypad": chat_keypad,
            "inline_keypad": inline_keypad,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        response = await self.request("sendLocation", data)
        return MessageId(response["data"])
    
    
    async def send_contact(
        self,
        chat_id: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        chat_keypad = None, # مشخص کردن تایپ
        inline_keypad  = None, # مشخص کردن تایپ
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal[None, "New", "Remove"] = None
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "chat_keypad": chat_keypad,
            "inline_keypad": inline_keypad,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        response = await self.request("sendContact", data)
        return MessageId(response["data"])
    
    
    async def send_sticker(
        self,
        chat_id: str,
        sticker_id: str,
        chat_keypad = None, # مشخص کردن تایپ
        inline_keypad = None, # مشخص کردن تایپ
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal[None, "New", "Remove"] = None,
    ) -> "MessageId":
        data = {
            "chat_id": chat_id,
            "sticker_id": sticker_id,
            "chat_keypad": chat_keypad,
            "disable_notification": disable_notification,
            "inline_keypad": inline_keypad,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        response = await self.request("sendSticker", data)
        return MessageId(response["data"])
    
    
    async def forward_message(
        self,
        from_chat_id: str,
        message_id: str,
        to_chat_id: str,
        disable_notification: bool = False
    ) -> "MessageId":
        data = {
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "to_chat_id": to_chat_id,
            "disable_notification": disable_notification
        }
        response = await self.request("forwardMessage", data)
        return MessageId(response["data"])
    
    
    async def edit_message_text(
        self,
        chat_id: str,
        message_id: str,
        text: str
    ) -> None:
        data = {"chat_id": chat_id, "message_id": message_id, "text": text}
        await self.request("editMessageText", data)
    
    
    async def edit_message_keypad(
        self,
        chat_id: str,
        message_id: str,
        inline_keypad # مشخص کردن تایپ
        ) -> None:
        data = {"chat_id": chat_id, "message_id": message_id, "inline_keypad": inline_keypad}
        await self.request("editMessageKeypad", data)
        
        
    async def edit_chat_keypad(
        self,
        chat_id: str,
        chat_keypad # مشخص کردن تایپ
    ) -> None:
        data = {"chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad}
        await self.request("editChatKeypad", data)
    
    
    async def remove_chat_keypad(
        self,
        chat_id: str
    ) -> None:
        data = {"chat_id": chat_id, "chat_keypad_type": "Remove"}
        await self.request("editChatKeypad", data)
        
    
    async def delete_message(
        self,
        chat_id: str,
        message_id: str
        ) -> None:
        data = {"chat_id": chat_id, "message_id": message_id}
        await self.request("deleteMessage", data)
    
    
    async def get_file(self, file_id: str) -> str:
        response = await self.request("getFile", {"file_id": file_id})
        return response["data"]["download_url"]

    
    async def request_send_file(self, type: Literal["File", "Image", "Voice", "Music", "Gif", "Video"]) -> str:
        response = await self.request("requestSendFile", {"type": type})
        return response["data"]["upload_url"]

    
    async def upload_file(self, path: str, file_name: str, type: Literal["File", "Image", "Voice", "Music", "Gif", "Video"]) -> str:
        upload_url = await self.request_send_file(type)
        form = FormData()
        form.add_field("file", open(path, "rb"), filename=file_name, content_type="application/octet-stream")
        async with ClientSession() as session:
            async with session.post(upload_url, data=form) as response:
                result = await response.json()
                return result["data"]["file_id"]
    
    
    async def send_file(
        self,
        chat_id: str,
        path: str,
        file_name: str,
        type: Literal["File", "Image", "Voice", "Music", "Gif", "Video"] = "File",
        chat_keypad = None,
        inline_keypad = None,
        disable_notification: bool = False,
        reply_to_message_id: str = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
    ) -> str:
        file_id = await self.upload_file(path, file_name, type)
        data = {
            "chat_id": chat_id,
            "file_id": file_id,
            "chat_keypad": chat_keypad,
            "disable_notification": disable_notification,
            "inline_keypad": inline_keypad,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type,
        }
        response = await self.request("sendFile", data)
        return MessageId(response["data"])

    
    async def download_file(self, file_id: str, file_name: str):
        download_url = await self.get_file(file_id)
        async with ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status == 200:
                    async with aiofiles.open(file_name, "wb") as file:
                        await file.write(await response.read())
                    return {"status": "OK", "file": file_name}
                raise Exception(f"Download Error | status_code : {response.status}")
    
    
    def run(self):
        routes = web.RouteTableDef()
        @routes.post("/receiveUpdate")
        @routes.post("/receiveInlineMessage")
        async def webhook(request):
            data = await request.json()
            await self.update(data)
            return web.json_response({"status": "ok"})
        app = web.Application()
        app.add_routes(routes)
        web.run_app(app, host=self.webhook, port=self.port)