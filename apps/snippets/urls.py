# -*- coding: utf-8 -*-
# snippets.url.py

from django.conf.urls import url, include

from rest_framework import routers

from rest_framework.urlpatterns import format_suffix_patterns

from .views import SnippetList, api_root, GenericsSnippetList, GenericsUserList, GenericsUserDetail,GenericeSnippetDetail
from .views import SnippetViewSet, UserViewSet,GroupViewSet

snippet_list = SnippetViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

snippet_detail = SnippetViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destory',
})

user_list = UserViewSet.as_view({
    'get': 'list'
})

user_detail = UserViewSet.as_view({
    'get': 'retrieve'
})


# API endpoints
# urlpatterns = [
#     url(r'^$', api_root, name='snippet_index'),
#     url(r'^snippets/$', GenericsSnippetList.as_view(), name='snippet-list'),
#     url(r'^snippets/(?P<pk>[0-9]+)/$', GenericeSnippetDetail.as_view(), name='snippet-detail'),
#     url(r'^users/$', GenericsUserList.as_view(), name='user-list'),
#     url(r'^users/(?P<pk>[0-9]+)/$', GenericsUserDetail.as_view(), name='user-detail'),
# ]
#
# urlpatterns = format_suffix_patterns(urlpatterns)
urlpatterns = format_suffix_patterns([
    url(r'^$', api_root),
    url(r'^snippets/$', SnippetList.as_view(), name='snippet-list'),
    url(r'^snippets/(?P<pk>[0-9]+)/$', snippet_detail, name='snippet-detail'),
    url(r'^users/$', user_list, name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', user_detail, name='user-detail')
])


