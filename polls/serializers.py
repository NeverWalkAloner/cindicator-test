# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, CharField, Serializer, IntegerField, DecimalField
from .models import Answer, Question, Vote


class UserSerialization(ModelSerializer):
    """
    Сериализатор модели User для регистрации пользователей
    """
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'password')


class AnswerSerializer(ModelSerializer):
    """
    Сериализатор модели Answer
    """
    class Meta:
        model = Answer
        fields = ('id',
                  'answer_text')


class VoteSerializer(ModelSerializer):
    """
    Сериализатор модели Vote
    """
    user = CharField(required=False)
    question = CharField(required=False)

    class Meta:
        model = Vote
        fields = ('user', 'question', 'answer')


class QuestionListSerializer(ModelSerializer):
    """
    Сериализатор списка вопросов
    """
    class Meta:
        model = Question
        fields = ('title',
                  'pub_date')


class QuestionSerializer(ModelSerializer):
    """
    Сериализатор модели Question
    """
    answer_set = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('title',
                  'text',
                  'date_start',
                  'date_end',
                  'answer_set')


class StatisticSerializer(Serializer):
    """
    Сериализатор статистических данных
    """
    question = IntegerField()
    question__title = CharField()
    answer__answer_text = CharField()
    total = IntegerField()
    answer = IntegerField()
    frequency = DecimalField(max_digits=5, decimal_places=2)