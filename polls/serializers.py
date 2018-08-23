# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.timezone import localtime, now
from rest_framework import serializers
from .models import Answer, Question, Vote


class UserSerialization(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True, source='id')
    token = serializers.CharField(read_only=True, source='auth_token.key')

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
        fields = ('username', 'password', 'user_id', 'token')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AnswerSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Answer
    """
    class Meta:
        model = Answer
        fields = ('id',
                  'answer_text')


class VoteSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Vote
    """
    def validate(self, attrs):
        validated = super(VoteSerializer, self).validate(attrs)
        answer = validated['answer']
        question = self.context['question']
        # проверяем принадлежит ли ответ опросу
        if answer not in question.answer_set.all():
            raise serializers.ValidationError('Answer is not valid')

        # проверяем акивен ли опрос по датам начала и конца
        current_time = localtime(now())
        if answer.question.date_start > current_time or \
                        answer.question.date_end < current_time:
            raise serializers.ValidationError('Question is not active')

        user = self.context['request'].user
        queryset = Vote.objects.filter(user=user,
                                       answer__question=answer.question)

        # в случае если пользователь уже голосовал вызываем исключение
        if queryset.exists():
            raise serializers.ValidationError('Already voted')

        return validated

    class Meta:
        model = Vote
        fields = ('question', 'answer')
        extra_kwargs = {
            'question': {'required': False}
        }


class QuestionListSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка вопросов
    """
    class Meta:
        model = Question
        fields = ('id', 'title', 'pub_date')


class QuestionSerializer(serializers.ModelSerializer):
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


class StatisticSerializer(serializers.Serializer):
    """
    Сериализатор статистических данных
    """
    question = serializers.IntegerField()
    question__title = serializers.CharField()
    answer__answer_text = serializers.CharField()
    total = serializers.IntegerField()
    answer = serializers.IntegerField()
    frequency = serializers.DecimalField(max_digits=5, decimal_places=2)