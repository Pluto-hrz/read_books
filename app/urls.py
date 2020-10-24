from django.urls import path, include
from app.views import *

urlpatterns = [

    path('login', login, name="login"),
    path('logout', logout, name="logout"),
    path('register', register, name="register"),
    path('check_code', check_code, name="check_code"),
    path('forget_password', forget_password, name="forget_password"),
    path('change_password', change_password, name="change_password"),
    path('change_name', change_name, name="change_name"),
    path('change_image', change_image, name="change_image"),
    path('index', index, name="index"),
    path('comment_request', comment_request, name="comment_request"),
    path('delete_comment', delete_comment, name="delete_comment"),
    # path('state_add', state_add, name="state_add"),
    path('image_upload', image_upload, name='image_upload'),
]

