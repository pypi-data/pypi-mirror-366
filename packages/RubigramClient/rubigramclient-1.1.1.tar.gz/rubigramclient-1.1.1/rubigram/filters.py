from rubigram.types import Message
from typing import Union


class filter:
    @staticmethod
    def text():
        def inner(update: Message):
            return update.new_message.text
        return inner

    @staticmethod
    def private():
        def inner(update: Message):
            return update.new_message.sender_type == "User"
        return inner
    
    @staticmethod
    def command(cmd: Union[str, list[str]]):
        def inner(update: Message):
            if not update.new_message.text:
                return False
            if not update.new_message.text.startswith("/"):
                return False
            return update.new_message.text.lstrip("/").split()[0] == cmd
        return inner
    
    @staticmethod
    def text_filter(text: str):
        def inner(update: Message):
            return update.new_message.text == text if update.new_message.text else False
        return inner
    
    @staticmethod
    def chat(chat_id: str):
        def inner(update: Message):
            return update.chat_id == chat_id
        return inner
    
    @staticmethod
    def file():
        def inner(update: Message):
            return update.new_message.file
        return inner
    
    @staticmethod
    def button(id: str):
        def inner(update: Message):
            return update.new_message.aux_data.button_id == id if update.new_message.aux_data else False
        return inner