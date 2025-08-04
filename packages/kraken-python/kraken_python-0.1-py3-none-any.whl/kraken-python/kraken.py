import telebot
from telebot import types
import threading
import time
from .utils import Anonymizer

class Kraken:
    def __init__(self, token, anon=False):
        self.token = token
        self.anon = anon
        self.bot = telebot.TeleBot(token)
        self.message_handlers = []
        self.anonymizer = Anonymizer() if anon else None
        self._stop_polling = threading.Event()

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
        if self.anon:
            message = self.anonymizer.anonymize_message(message)
        
        for handler in self.message_handlers:
            if handler['commands']:
                if message.text and message.text.startswith('/'):
                    cmd = message.text.split()[0][1:]
                    if cmd in handler['commands']:
                        handler['function'](message)
                        return
        
        # Default handler if no commands match
        for handler in self.message_handlers:
            if not handler['commands']:
                handler['function'](message)

    def send_message(self, chat_id, text, **kwargs):
        self.bot.send_message(chat_id, text, **kwargs)

    def polling(self, non_stop=False, interval=0, timeout=20):
        self._stop_polling.clear()
        
        def poll():
            while not self._stop_polling.is_set():
                try:
                    self.bot.polling(none_stop=True, timeout=timeout)
                except Exception as e:
                    if non_stop:
                        time.sleep(interval)
                    else:
                        raise e
        
        poll_thread = threading.Thread(target=poll)
        poll_thread.daemon = True
        poll_thread.start()

    def stop_polling(self):
        self._stop_polling.set()
        self.bot.stop_polling()
