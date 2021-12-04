from rest_framework.pagination import PageNumberPagination

""" ---------Pagination classes fot Spaces-------"""

class SpacesPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 50
