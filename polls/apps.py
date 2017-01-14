# -*- coding: utf-8 -*-
from django.apps import AppConfig


class PollsConfig(AppConfig):
    name = 'polls'

    # зарегистрируем сигнал post_create для модели User
    def ready(self):
        import polls.signals
