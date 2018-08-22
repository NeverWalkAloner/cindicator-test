from django.conf.urls import url
from rest_framework.authtoken.views import obtain_auth_token
from .views import (QuestionDetails,
                    VoteView,
                    QuestionList,
                    RegisterUser,
                    StatisticView)


app_name = 'polls'
urlpatterns = [
    url(r'^get-auth-token/', obtain_auth_token, name='login'),
    url(r'^sign-on/', RegisterUser.as_view(), name='sign-on'),
    url(r'^questions/$', QuestionList.as_view(), name='questions'),
    url(r'^questions/(?P<pk>\d+)/$', QuestionDetails.as_view(), name='question_details'),
    url(r'^questions/(?P<pk>\d+)/vote/$', VoteView.as_view(), name='vote'),
    url(r'^questions/statistics/$', StatisticView.as_view(), name='statistics'),
]
