# -*- coding: utf-8 -*-
from django.db.models import Count
from django.utils.timezone import localtime, now
from rest_framework import status
from rest_framework.generics import (ListAPIView,
                                     RetrieveAPIView,
                                     CreateAPIView)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
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
        return Question.objects.get(pk=self.kwargs['pk'])

    @staticmethod
    def validations(user, question, answer):
        # проверяем принадлежит ли ответ опросу
        if answer not in question.answer_set.all():
            raise ValidationError('Answer is not valid')

        # проверяем акивен ли опрос по датам начала и конца
        if answer.question.date_start > current_time() or answer.question.date_end < current_time():
            raise ValidationError('Question is not active')
        queryset = Vote.objects.filter(user=user,
                                       answer__question=answer.question)

        # в случае если пользователь уже голосовал вызываем исключение
        if queryset.exists():
            raise ValidationError('Already voted')

    def perform_create(self, serializer):
        user = self.request.user
        question = self.get_object()
        serializer.validated_data['user'] = self.request.user
        serializer.validated_data['question'] = question
        answer = serializer.validated_data.get('answer')
        self.validations(user, question, answer)
        super(VoteView, self).perform_create(serializer)


class RegisterUser(CreateAPIView):
    """
    Представление реализующее регистрацию пользователей через API
    """
    serializer_class = UserSerialization
    permission_classes = (AllowAny,)

    # Переопределяем метод чтобы включить в ответ токен
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'user_id': serializer.instance.id,
                         'token': serializer.instance.auth_token.key},
                        status=status.HTTP_201_CREATED,
                        headers=headers)


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
