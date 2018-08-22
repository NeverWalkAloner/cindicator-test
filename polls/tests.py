# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils.timezone import localtime, now, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Question, Answer


def create_account(superuser=False):
    """
    создает нового пользователя
    """
    user = User.objects.create(
            username='test_account',
            is_superuser=superuser
        )
    user.set_password('pass12345')
    user.save()
    return user.auth_token.key


def create_question(future_days):
    """
    создает новый вопрос и вариант ответа
    future_days: если положительное дата активации опроса еще еще не наступила,
    если отрицательное уже наступила
    """
    start_date = localtime(now()) + timedelta(future_days)
    q = Question.objects.create(title='test',
                                text='test',
                                date_start=start_date,
                                date_end=start_date + timedelta(5),
                                owner=User.objects.get())
    a = Answer.objects.create(question=q,
                          answer_text='text')
    return q.id, a.id


class QuestionListTest(APITestCase):
    def test_not_authenticated_list(self):
        """
        проверяет доступность списка опросов для неаутентифицированных запросов
        """
        url = reverse('polls:questions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_list(self):
        """
        проверяет доступность списка опросов для аутентифицированных запросов
        """
        token = create_account()
        url = reverse('polls:questions')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'test_account')


class RegisterUserTest(APITestCase):
    def test_register_user(self):
        """
        проверяет регистрацию пользователей
        """
        url = reverse('polls:sign-on')
        data = {'username': 'test_account',
                'password': 'pass12345'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'test_account')


class GetTokenTest(APITestCase):
    def test_get_token(self):
        """
        проверяет доступность получения токена для зарегистрированных пользователей
        """
        token = create_account()
        url = reverse('polls:login')
        data = {'username': 'test_account',
                'password': 'pass12345'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'{"token":"' + bytes(token, encoding='utf-8') + b'"}')


class QuestionDetailsTest(APITestCase):
    def test_not_authenticated_question_details(self):
        """
        проверяет доступность деталей опроса для неаутентифицированных запросов
        """
        create_account()
        create_question(0)
        url = reverse('polls:question_details', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_question_details(self):
        """
        проверяет доступность деталей опроса для аутентифицированных запросов
        """
        token = create_account()
        q_id, _ = create_question(-1)
        url = reverse('polls:question_details', kwargs={'pk': q_id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_not_active_question_details(self):
        """
        проверяет доступность деталей неактивного опроса для аутентифицированных запросов
        """
        token = create_account()
        q_id, _ = create_question(1)
        url = reverse('polls:question_details', kwargs={'pk': q_id})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.content, b'{"detail":"Not found."}')


class VoteTest(APITestCase):
    def test_not_authenticated_question_vote(self):
        """
        проверяет доступность голосования для неаутентифицированных запросов
        """
        create_account()
        create_question(0)
        url = reverse('polls:vote', kwargs={'pk': 1})
        data = {"answer": 1}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_question_vote(self):
        """
        проверяет доступность голосования для аутентифицированных запросов
        """
        token = create_account()
        question_id, answer_id = create_question(0)
        url = reverse('polls:vote', kwargs={'pk': question_id})
        data = {"answer": answer_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['answer'], answer_id)

    def test_authenticated_not_active_question_vote(self):
        """
        проверяет доступность голосования по неактивным опросам для аутентифицированных запросов
        """
        token = create_account()
        question_id, answer_id = create_question(1)
        url = reverse('polls:vote', kwargs={'pk': question_id})
        data = {"answer": answer_id}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, b'["Question is not active"]')


class StatisticTest(APITestCase):
    def test_not_authenticated_statistic(self):
        """
        проверяет доступность статистики для неаутентифицированных запросов
        """
        url = reverse('polls:statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_superuser_statistic(self):
        """
        проверяет доступность статистики для обычных пользователей
        """
        token = create_account()
        url = reverse('polls:statistics')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_statistic(self):
        """
        проверяет доступность статистики для суперпользователей
        """
        token = create_account(True)
        url = reverse('polls:statistics')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
