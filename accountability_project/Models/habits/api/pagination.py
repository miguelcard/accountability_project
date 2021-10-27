from rest_framework.pagination import PageNumberPagination

""" ---------Pagination classes fot habits-------"""

class AllHabitsPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

class HabitTagsPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 200

class CheckmarksPagination(PageNumberPagination):
    page_size = 31
    page_size_query_param = 'page_size'
    max_page_size = 100