import telebot
from telebot import types
import threading
import time
import logging
from .utils import Anonymizer

class Kraken:
    def __init__(self, token, anon=False):
        self.token = token
        self.anon = anon
        self.bot = telebot.TeleBot(token)
        self.message_handlers = []
        self.anonymizer = Anonymizer() if anon else None
        self._stop_polling = threading.Event()
        
        # Регистрируем обработчик всех сообщений
        @self.bot.message_handler(func=lambda m: True)
        def handle_all_messages(message):
            self._process_message(message)

    def message_handler(self, commands=None, **kwargs):
        def decorator(func):
            handler = {
                'function': func,
                'filters': kwargs,
                'commands': commands
            }
            self.message_handlers.append(handler)
            return func
        return decorator

    def _process_message(self, message):
        try:
            if self.anon and self.anonymizer:
                message = self.anonymizer.anonymize_message(message)
            
            for handler in self.message_handlers:
                if handler['commands']:
                    if message.text and message.text.startswith('/'):
                        cmd = message.text.split()[0][1:].split('@')[0]
                        if cmd in handler['commands']:
                            handler['function'](message)
                            return
                
                # Обработчик для всех сообщений
                if not handler['commands']:
                    handler['function'](message)
                    return
        except Exception as e:
            logging.error(f"Ошибка обработки сообщения: {e}")

    def send_message(self, chat_id, text, **kwargs):
        self.bot.send_message(chat_id, text, **kwargs)

    def polling(self, non_stop=True, interval=5, timeout=30):
        self._stop_polling.clear()
        print("🦑 Kraken Bot запущен в анонимном режиме" if self.anon else "🦑 Kraken Bot запущен")
        
        def poll():
            while not self._stop_polling.is_set():
                try:
                    self.bot.polling(none_stop=non_stop, interval=interval, timeout=timeout)
                except Exception as e:
                    logging.error(f"Ошибка polling: {e}")
                    if non_stop:
                        time.sleep(interval)
                    else:
                        raise
                finally:
                    if not non_stop:
                        self._stop_polling.set()
        
        poll_thread = threading.Thread(target=poll)
        poll_thread.daemon = True
        poll_thread.start()
        return poll_thread

    def stop_polling(self):
        self._stop_polling.set()
        self.bot.stop_polling()
        print("🛑 Kraken Bot остановлен")

    # Дополнительные методы для совместимости
    def reply_to(self, message, text, **kwargs):
        self.send_message(message.chat.id, text, **kwargs)
