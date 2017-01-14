# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import (Question,
                     Answer,
                     Vote)


# Регистрируем модели в админке Django
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Vote)
