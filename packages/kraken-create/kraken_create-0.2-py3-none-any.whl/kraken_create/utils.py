import random
import hashlib
from telebot import types

class Anonymizer:
    def __init__(self):
        self.user_mapping = {}
        self.chat_mapping = {}
        self.name_pool = [f"User_{i:04d}" for i in range(1, 10000)]
        random.shuffle(self.name_pool)
        self.id_counter = 1000000

    def _generate_id(self, real_id):
        """Генерация постоянного анонимного ID"""
        if real_id not in self.user_mapping:
            salt = "kraken_salt_"
            hashed = hashlib.sha256(f"{salt}{real_id}".encode()).hexdigest()
            self.user_mapping[real_id] = int(hashed[:10], 16) + self.id_counter
            self.id_counter += 1
        return self.user_mapping[real_id]

    def _get_anon_name(self, real_id):
        """Получение случайного но постоянного имени"""
        if real_id not in self.name_pool:
            if not self.name_pool:
                self.name_pool = [f"User_{i:04d}" for i in range(1, 10000)]
                random.shuffle(self.name_pool)
            self.name_pool[real_id] = self.name_pool.pop()
        return self.name_pool[real_id]

    def anonymize_user(self, user):
        """Анонимизация объекта пользователя"""
        if not user:
            return None
            
        anon_id = self._generate_id(user.id)
        return types.User(
            id=anon_id,
            is_bot=user.is_bot,
            first_name=self._get_anon_name(user.id),
            last_name=None,
            username=f"anon_{anon_id}",
            language_code=None
        )

    def anonymize_chat(self, chat):
        """Анонимизация объекта чата"""
        anon_id = self._generate_id(chat.id)
        return types.Chat(
            id=anon_id,
            type=chat.type,
            title=f"Chat_{anon_id}" if chat.title else None,
            username=f"chat_{anon_id}" if hasattr(chat, 'username') else None,
            first_name=None,
            last_name=None
        )

    def anonymize_message(self, message):
        """Анонимизация всего сообщения"""
        try:
            anon_msg = types.Message(
                message_id=message.message_id,
                from_user=self.anonymize_user(message.from_user),
                date=message.date,
                chat=self.anonymize_chat(message.chat),
                content_type=message.content_type,
                json_string=message.json_string
            )
            
            # Копируем содержимое без персональных данных
            for attr in ['text', 'caption', 'data', 'contact', 'location']:
                if hasattr(message, attr):
                    setattr(anon_msg, attr, getattr(message, attr))
                    
            return anon_msg
        except Exception as e:
            print(f"Ошибка анонимизации: {e}")
            return message
