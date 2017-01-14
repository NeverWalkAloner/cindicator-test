# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings


class Question(models.Model):
    """
    Модель описывающая опросы
    """
    title = models.CharField(verbose_name='наименование', max_length=100)
    text = models.CharField(verbose_name='текст опроса', max_length=250)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.PROTECT,
                              verbose_name='создатель опроса')
    pub_date = models.DateTimeField(verbose_name='время публикации', auto_now_add=True)
    date_start = models.DateTimeField(verbose_name='опрос активен после')
    date_end = models.DateTimeField(verbose_name='опрос активен до')

    def __str__(self):
        return self.title


class Answer(models.Model):
    """
    Модель описывающая варианты ответа
    """
    question = models.ForeignKey(Question,
                                 on_delete=models.PROTECT,
                                 verbose_name='опрос')
    answer_text = models.CharField(verbose_name='текст ответа', max_length=250)

    def __str__(self):
        return self.answer_text


class Vote(models.Model):
    """
    Модель описывающая отвкты пользователей
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.PROTECT,
                             verbose_name='пользователь')
    question = models.ForeignKey(Question,
                                 on_delete=models.PROTECT,
                                 verbose_name='ответ к опросу')
    answer = models.ForeignKey(Answer,
                               on_delete=models.PROTECT,
                               verbose_name='выбранный ответ')
