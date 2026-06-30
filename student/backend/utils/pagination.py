# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.core import paginator
from django.core.paginator import Paginator as DjangoPaginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import InvalidPage


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "pageSize"  # 前端传的每页数量
    page_query_param = "pageNum"
    max_page_size = 999
    django_paginator_class = DjangoPaginator

    def paginate_queryset(self, queryset, request, view=None):
        """
        重写paginate_queryset让分页超过正常分页:有原来的 400 错误无效页面。改写为返回 200 成功，data=[]提示
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            self.page = []

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        code = 200
        msg = 'success'
        count = self.page.paginator.count if self.page else 0
        if not data:
            code = 200
            msg = "暂无数据"
            data = []

        return Response(OrderedDict([
            ('code', code),
            ('msg', msg),
            ('data', data),
            ('count', count)
        ]))
