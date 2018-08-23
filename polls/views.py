# -*- coding: utf-8 -*-
from django.db.models import Count
from django.utils.timezone import localtime, now
from rest_framework.generics import (ListAPIView,
                                     RetrieveAPIView,
                                     CreateAPIView)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
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
        question_qs = Question.objects.all().values_list('id').annotate(total=Count('vote')).order_by('id')
        vote_qs = Vote.objects.all().values('question',
                                            'answer',
                                            'question__title',
                                            'answer__answer_text').annotate(total=Count('answer'))
        for vote in vote_qs:
            vote['frequency'] = vote['total'] / question_qs.get(pk=vote['question'])[1]
        return vote_qs

    def list(self, request, *args, **kwargs):
        serializer = StatisticSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)
