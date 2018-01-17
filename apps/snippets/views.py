# -*- coding:utf-8 -*-
# snippets.views.py

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework import generics
from rest_framework import permissions

from .models import Snippet
from .serializers import SnippetSerializer, UserSerializer, GroupSerializer
from .permissions import IsOwnerOrReadOnly


# Create your views here.
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('snippets:user-list', request=request, format=format),
        'snippets': reverse('snippets:snippet-list', request=request, format=format)
    })


class JSONResponse(HttpResponse):
    """
    用于返回JSON数据
    """
    def __init__(self, data,**kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class SnippetView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


@csrf_exempt
def snippet_list(request, format=None):
    """
    List all code snippets, or create a new snippet. 获取所有的用户列表
    """
    if request.method == 'GET':
        all_snippets = Snippet.objects.all()  # 抓取所有的Snippet
        serializer = SnippetSerializer(all_snippets, many=True)  # 对QuerySet进行序列化
        content = JSONRenderer().render(serializer.data)
        #return JsonResponse(serializer.data, safe=False)  # 返回一个JsonResponse
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            #return JsonResponse(serializer.data, status=201)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        #return JsonResponse(serializer.errors, status=400)
        return Response(serializer.errors,status=400)

@csrf_exempt
def snippet_detail(request, pk, format=None):
    """
    Retrieve ,update or delete a code snippet. 
    """
    try:
        snippet = Snippet.objects.get(id=int(pk))
    except Snippet.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SnippetSerializer(snippet)
        return JsonResponse(serializer.data, status=200)

    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)


@csrf_exempt
def user_list(request):
    """
    Retrieve ,update,or delete a code user
    """
    if request.method == "GET":
        all_user = User.objects.all()
        serializer = UserSerializer(all_user, many=True)
        return JsonResponse(serializer.data, status=200)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=200)
        return JsonResponse(serializer.errors, status=400)

"""
下面都是使用rest_framework的使用APIView方法
"""
class SnippetList(APIView):
    """
    List all snippets. or create a new snippet
    """
    def get(self, request, format=None):
        all_snippets = Snippet.objects.all()
        serializer = SnippetSerializer(all_snippets, many=True)
        #content = JSONRenderer().render(serializer.data)
        #return HttpResponse(content, status=200)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class SnippetDetail(APIView):
    """
    Retrieve,update or delete a snippet instance
    """
    def get_object(self, pk):
        try:
            snippet = Snippet.objects.get(pk =pk)
            return snippet
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request,pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format =None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, reqeust, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

"""
下面都是使用rest_framework的使用Mixin方法
"""


""" 
使用通用视图重构上面功能  generics.ListAPIView, generics.RetrieveUpdateDestroyAPIView
"""
class GenericsSnippetList(generics.ListAPIView):
    """
    List all snippets. or create a new snippet
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)  # 添加权限认证，只有创建者可以删除、修改


class GenericeSnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve,update or delete a snippet instance
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class GenericsUserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)  # 添加权限认证，只有创建者可以删除、修改


class GenericsUserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

"""
使用viewset重构上面的代码
我们使用UserViewSet 取代 UserList和UserDetail
"""
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited. 
    这个viewset自动提供list和detail事件支持
    class UserViewSet(viewsets.ReadOnlyModelViewSet),使用ReadOnlyModelViewSet自动提供只读方法，并且依然像使用常规视图那样设置了
    queryset和serializer_classs属性，但我们不用写两个类了。
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited. 
    
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class SnippetViewSet(viewsets.ModelViewSet):
    """
    这个viewsets会自动提供list、create、retrieve、update、destory事件支持，附加的我们加入了一个叫做highlight的事件
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)


