import random
import string
import hashlib
from telebot import types

class Anonymizer:
    def __init__(self):
        self.user_mapping = {}
        self.chat_mapping = {}
        self.name_pool = [f"User_{i:04d}" for i in range(1, 10000)]
        random.shuffle(self.name_pool)

    def _generate_id(self, real_id):
        """Генерация постоянного анонимного ID"""
        salt = "kraken_salt_"
        return int(hashlib.sha256(f"{salt}{real_id}".encode()).hexdigest()[:10], 16)

    def _get_anon_name(self, real_id):
        """Получение случайного но постоянного имени"""
        if real_id not in self.user_mapping:
            self.user_mapping[real_id] = {
                'name': self.name_pool.pop() if self.name_pool else f"User_{random.randint(1000,9999)}"
            }
        return self.user_mapping[real_id]['name']

    def anonymize_user(self, user):
        """Анонимизация объекта пользователя"""
        if not user:
            return None
            
        anon_id = self._generate_id(user.id)
        return types.User(
            id=anon_id,
            is_bot=user.is_bot,
            first_name=self._get_anon_name(user.id),
            last_name="",
            username=f"anon_{anon_id}",
            language_code=""
        )

    def anonymize_chat(self, chat):
        """Анонимизация объекта чата"""
        anon_id = self._generate_id(chat.id)
        return types.Chat(
            id=anon_id,
            type=chat.type,
            title=f"Chat_{anon_id}" if chat.title else "",
            username=f"chat_{anon_id}",
            first_name="",
            last_name=""
        )

    def anonymize_message(self, message):
        """Анонимизация всего сообщения"""
        anon_msg = types.Message(
            message_id=message.message_id,
            from_user=self.anonymize_user(message.from_user),
            date=message.date,
            chat=self.anonymize_chat(message.chat),
            content_type=message.content_type,
            json_string=message.json_string
        )
        
        # Копируем содержимое без персональных данных
        if message.text:
            anon_msg.text = message.text
        if message.caption:
            anon_msg.caption = message.caption
            
        return anon_msg
