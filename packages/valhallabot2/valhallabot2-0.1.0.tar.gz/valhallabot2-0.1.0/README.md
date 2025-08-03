# myfile_sender

مكتبة بايثون لإرسال ملفات من مجلد معين عبر بوت تليجرام مع إرسال الأخطاء كرسائل.

## الاستخدام

```python
from myfile_sender import FileSenderBot

API_TOKEN = 'ضع_توكن_البوت_هنا'
CHAT_ID = 'ضع_معرف_المستخدم_أو_القناة_هنا'

bot = FileSenderBot(API_TOKEN)
bot.send_files_from_folder(CHAT_ID)
```

---

## تثبيت المتطلبات

```
pip install pyTelegramBotAPI
```
