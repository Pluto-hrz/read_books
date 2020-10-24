from django.urls import path, include
from books.views import *

urlpatterns = [
    path('book_list1/', book_list1, name="book_list1"),
    path('book_list2/', book_list2, name="book_list2"),
    path('book_list/', new_book, name='new_book_lists'),
    path('book/', book, name='book'),
    path('book_review/', book_review, name='book_review'),
    path('status/', status, name='status'),
    path('get_init/', get_init, name='get_init'),
    path('delete/', delete_database, name='delete'),
]
