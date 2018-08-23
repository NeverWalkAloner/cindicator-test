# -*- coding: utf-8 -*-
from django.db.models import F, Count
from django.db.models.expressions import Window
from django.utils.timezone import localtime, now
from rest_framework.generics import (ListAPIView,
                                     RetrieveAPIView,
                                     CreateAPIView)
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Question, Vote
from .permissions import ClientPermission
from .serializers import (QuestionSerializer,
                          QuestionListSerializer,
                          StatisticSerializer,
                          VoteSerializer,
                          UserSerialization)


def current_time():
    """
    Вычисляет текущее локальное время
    """
    return localtime(now())


class QuestionList(ListAPIView):
    """
    Представление возвращающее список всех активных на текущее время опросов
    """
    queryset = Question.objects.filter(date_start__lt=current_time(), date_end__gt=current_time())
    serializer_class = QuestionListSerializer


class QuestionDetails(RetrieveAPIView):
    """
    Представление возвращающее детализациою опроса
    """
    queryset = Question.objects.filter(date_start__lt=current_time(), date_end__gt=current_time())
    serializer_class = QuestionSerializer


class VoteView(CreateAPIView):
    """
    Представление реализующее голосование пользователей
    """
    serializer_class = VoteSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        if self.kwargs:
            self.object = Question.objects.get(pk=self.kwargs['pk'])
            return self.object

    def get_serializer_context(self):
        context = super(VoteView, self).get_serializer_context()
        context['question'] = self.get_object()
        return context

    def perform_create(self, serializer):
        serializer.save(question=self.object, user=self.request.user)


class RegisterUser(CreateAPIView):
    """
    Представление реализующее регистрацию пользователей через API
    """
    serializer_class = UserSerialization
    permission_classes = (AllowAny,)


class StatisticView(ListAPIView):
    """
    Представление реализующее сбор статистики по всем опросам,
    доступно только клиентам
    """
    queryset = Vote.objects.all()
    serializer_class = StatisticSerializer
    permission_classes = [ClientPermission, ]

    def get_queryset(self):
        vote_qs = Vote.objects.annotate(
            total=Window(
                expression=Count('answer'),
                partition_by=[F('question')])).annotate(
            per_answer=Window(
                expression=Count('answer'),
                partition_by=[F('question'), F('answer')])
        )

        vote_qs = vote_qs.values(
            'question', 'question__title',
            'answer__answer_text', 'answer',
            'total','per_answer'
        ).distinct().order_by('question')

        return vote_qs
