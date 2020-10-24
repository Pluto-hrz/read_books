from django.db import models
from django.contrib.auth.models import AbstractUser
from read_books.settings import MEDIA_ROOT


# Create your models here.

def upload_to(instance, username):
    return r'F:\Order\200419项目(0)\itstudio\media\User_'.join([instance.username, username])


class User(AbstractUser):
    # 用户名/密码/邮箱 为默认
    name = models.CharField(max_length=30, verbose_name='用户昵称')
    image = models.ImageField(upload_to=upload_to, verbose_name='用户头像', default="Image/default.jpg")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    code = models.CharField(max_length=30, verbose_name='验证码')

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = '用户信息管理'
        verbose_name_plural = verbose_name


class Type(models.Model):
    # 图书类型做主键,便于筛选
    type = models.TextField(verbose_name='图书类型')

    def __str__(self):
        return str(self.type)

    class Meta:
        verbose_name = '图书分类管理'
        verbose_name_plural = verbose_name


class Books(models.Model):  #
    # 图书封面存为URL
    num = models.TextField(verbose_name='书籍ID')
    title = models.TextField(verbose_name='标题')
    info = models.TextField(verbose_name='相关信息')
    introduce = models.TextField(verbose_name='简介')
    score = models.TextField(verbose_name='评分')
    img_l = models.TextField(verbose_name='img_l')
    img_s = models.TextField(verbose_name='img_s')
    people = models.TextField(verbose_name='评论人数', default='0')
    done = models.TextField(verbose_name="已读人数", default='0')  # 2
    progress = models.TextField(verbose_name='在读人数', default='0')  # 1
    want = models.TextField(verbose_name="想读人数", default='0')  # 0
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return str(self.num)

    class Meta:
        verbose_name = '图书详情管理'
        verbose_name_plural = verbose_name


class State(models.Model):
    # 用户状态：0为想读,1为在读,2为读过,默认为3
    user = models.TextField(verbose_name='用户名', blank=True, default='root')
    num = models.TextField(verbose_name='书籍ID')
    state = models.TextField(verbose_name='用户状态', default='3')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '用户状态管理'
        verbose_name_plural = verbose_name


class Long(models.Model):
    user = models.ForeignKey("User", null=True, blank=True, on_delete=models.SET_NULL)
    num = models.IntegerField(verbose_name='图书编号')
    content = models.TextField(verbose_name='评论内容')
    title = models.TextField(verbose_name='评论的标题')
    word = models.TextField(verbose_name='书评内容的文字')
    score = models.TextField(verbose_name='评分')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '图书短评管理'
        verbose_name_plural = verbose_name


class Short(models.Model):
    user = models.ForeignKey("User", null=True, blank=True, on_delete=models.SET_NULL)
    num = models.IntegerField(verbose_name='图书编号')
    content = models.TextField(verbose_name='评论内容')
    score = models.TextField(verbose_name='评分')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = '图书长评管理'
        verbose_name_plural = verbose_name


def photo_upload_to(instance, title):
    return '/Photo_'.join([instance.title, title])


class Photo(models.Model):
    title = models.CharField(max_length=30, verbose_name='图片名称')
    photo = models.ImageField(upload_to=photo_upload_to, verbose_name='图片上传')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = '图片管理中心'
        verbose_name_plural = verbose_name


class Book_list(models.Model):
    list_class = models.TextField(verbose_name='书单类型')
    name = models.TextField(verbose_name='书单名')
    image = models.TextField(verbose_name='图片')
    number = models.TextField(verbose_name='书单里书本的数量')
    content = models.TextField(verbose_name='内容')
    info = models.TextField(verbose_name='相关信息')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = '图书列表管理'
        verbose_name_plural = verbose_name


