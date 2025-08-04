Rubigram

```python
from rubigram import Client, filter
from rubigram.types import Message

client = Client("Your_Bot_Token")

@bot.on_message(filter.command("start"))
async def start(client: Client, message: Message):
    chat_id = message.chat_id
    await message.reply("Hi, {}".format(chat_id))

client.run()