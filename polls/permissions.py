# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission


class ClientPermission(BasePermission):
    """
    Проверяет наличие прав суперюзера или членство в группе Clients
    """
    def has_permission(self, request, view):
        is_client = request.user.groups.filter(name='Clients').exists()
        return request.user.is_superuser or is_client
