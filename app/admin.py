from . import models as us
from django.contrib import admin


class AdminLogin(admin.ModelAdmin):
    # 要显示的字段
    list_display = ['username', 'name', 'email', 'is_active', 'last_login', 'create_time']
    # 搜索框，按照元组内指定字段搜索
    search_fields = ('username', 'name')
    # 按时间过滤
    date_hierarchy = 'create_time'
    # 定义动作列表
    actions = ["publish_status", "withdraw_status"]
    # 每页显示多少条
    list_per_page = 20

    # 禁止登陆动作函数 参数固定
    def publish_status(self, request, queryset):
        queryset.update(is_active=False)

    publish_status.short_description = '冻结用户'  # 指定动作显示名称

    # 允许登陆动作函数 参数固定
    def withdraw_status(self, request, queryset):
        queryset.update(is_active=True)

    withdraw_status.short_description = '解除冻结'  # 指定动作显示名称


class Photos(admin.ModelAdmin):
    list_display = ['title', 'create_time']
    search_fields = ('title',)
    date_hierarchy = 'create_time'
    list_per_page = 20


class AdminBooks(admin.ModelAdmin):
    # 要显示的字段
    list_display = ['num', 'title', 'info', 'score', 'create_time']
    # 搜索框，按照元组内指定字段搜索
    search_fields = ('num', 'title')


class AdminState(admin.ModelAdmin):
    # 要显示的字段
    list_display = ['user', 'num', 'state', 'create_time']
    # 搜索框，按照元组内指定字段搜索
    search_fields = ('user', 'num')


class AdminLong(admin.ModelAdmin):
    # 要显示的字段
    list_display = ['user', 'num', 'title', 'create_time']
    # 搜索框，按照元组内指定字段搜索
    search_fields = ('user', 'num')


class AdminShort(admin.ModelAdmin):
    # 要显示的字段
    list_display = ['user', 'num', 'create_time']
    # 搜索框，按照元组内指定字段搜索
    search_fields = ('user', 'num')


class AdminBook_List(admin.ModelAdmin):
    # 要显示的字段
    list_display = ['list_class', 'name', 'id']
    # 搜索框，按照元组内指定字段搜索
    search_fields = ('id', 'list_class')


# 注册   第一个参数为数据库模型， 第二为自己写的类
admin.site.register(us.User, AdminLogin)
admin.site.register(us.Photo, Photos)
admin.site.register(us.Long, AdminLong)
admin.site.register(us.State, AdminState)
admin.site.register(us.Short, AdminShort)
admin.site.register(us.Book_list, AdminBook_List)
admin.site.register(us.Books, AdminBooks)


