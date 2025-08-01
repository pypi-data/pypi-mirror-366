import telebot
import os

class FileSenderBot:
    def __init__(self, api_token):
        self.bot = telebot.TeleBot(api_token)

    def send_files_from_folder(self, chat_id, folder=None):
        target_folder = folder or os.getcwd()
        for filename in os.listdir(target_folder):
            file_path = os.path.join(target_folder, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        self.bot.send_document(chat_id, f)
                except Exception as e:
                    error_message = f"❌ خطأ في إرسال الملف '{filename}': {e}"
                    try:
                        self.bot.send_message(chat_id, error_message)
                    except Exception as send_err:
                        pass
