# -*- coding: utf-8 -*-

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限，只有创建者才能编辑
    """
    def has_object_permission(self, request, view, obj):
        # read permission are allowd to any request
        # so we'll always allow GET,HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # write permission are only allowed to the owner of the snippet
        return obj.owner == request.user