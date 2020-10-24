from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
# 内置user的登录注销以及判断登录
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
# 用于密码加密解密
from django.contrib.auth.hashers import make_password, check_password
# 使用model类
from app.models import User, Books, Short, Long, Type, State, Photo
# 用于发送邮件
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
# 用于正则表达式
import re
# 用于生成随机函数
import random
import time

# Create your views here.


# 登录表单提交函数
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            exist_user = User.objects.filter(username=username).first()
            if exist_user:
                exist_password = check_password(password, exist_user.password)
                if exist_password:
                    if exist_user.is_active == 1:
                        request.session['user'] = exist_user.username
                        log_in(request, exist_user)
                        result = '登陆成功'
                        code = 1000
                    else:
                        result = '该用户已经被冻结'
                        code = 1005
                else:
                    result = '用户名或者密码错误'
                    code = 1004
            else:
                result = '用户名不存在'
                code = 1003
        else:
            result = '未提交全部参数'
            code = 1002
    else:
        result = '未提交POST请求'
        code = 1001
    json = {
        "result": result,
        "code": code,
    }
    return JsonResponse(json)


# 随机code生成函数
def get_code():
    code = random.randint(100000, 999999)
    return code


# 发送邮件的函数
def send_mail(email, code):
    # 发件人邮箱账号
    my_sender = '1559492576@qq.com'
    # 发件人邮箱密码
    my_pass = "fetvpbfssteiibdj"
    # 收件人邮箱账号
    my_user = email
    content = '''
    亲爱的用户：
        您好！
        欢迎您加入我们爱特读书大家庭!
        一定保存好验证码,打死也不要告诉别人哦！
    '''
    content = content + "    您的注册验证码为:" + str(code)
    # 括号里包括邮件主要内容、编码方式
    msg = MIMEText(content, 'plain', 'utf-8')
    # 括号里的对应发件人邮箱昵称、发件人邮箱账号
    msg['From'] = formataddr(["【爱特读书APP】", my_sender])
    # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    msg['To'] = formataddr(["爱特读书用户", my_user])
    # 邮件的主题，也可以说是标题
    msg['Subject'] = "【爱特读书验证码发送】"
    # 发件人邮箱中的SMTP服务器，端口是465
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    # 括号中对应的是发件人邮箱账号、邮箱密码
    server.login(my_sender, my_pass)
    # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
    server.sendmail(my_sender, [my_user, ], msg.as_string())
    server.quit()


# 判断是否登录-Python装饰器
def login_required(func):
    def wrapper(request, *args, **kwargs):
        username = request.session.get('user')
        user = User.objects.filter(username=username).first()
        if user:
            setattr(request, 'user', user)
            result = func(request, *args, **kwargs)
            return result
        else:
            json = {
                "result": '用户未登录',
                "code": 0000,
            }
            return JsonResponse(json)
    return wrapper


# 注册表单提交函数
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')if request.POST.get('name') else username
        if username and email and password:
            un = re.findall(r"^[a-z0-9_]{6,16}$", username)
            pd = re.findall(r"^[a-z0-9_.]{6,16}$", password)
            em = re.findall(r"^[a-z0-9]+[@][a-z0-9]+\.com|cn$", email)
            exist_user = User.objects.filter(username=username).first()
            if exist_user:
                result = '用户名已经存在'
                code = 1007
            elif not(un and un[0] == username):
                result = '用户名格式不正确'
                code = 1008
            elif not(pd and pd[0] == password):
                result = '密码格式不正确'
                code = 1008
            elif not(em and em[0] == email):
                result = '邮箱格式不正确'
                code = 1008
            elif len(name) > 16:
                result = '昵称格式不正确'
                code = 1008
            else:
                code = get_code()
                request.session['m_username'] = username
                request.session['m_password'] = make_password(password)
                request.session['m_email'] = email
                request.session['m_name'] = name
                request.session['m_code'] = code + 123456
                try:
                    send_mail(email, code)
                    result = '验证码发送成功'
                    code = 1000
                except Exception:
                    result = '验证码发送失败'
                    code = 1013
        else:
            result = '未提交全部参数'
            code = 1002
    else:
        result = '未提交POST请求'
        code = 1001
    json = {
        "result": result,
        "code": code,
    }
    return JsonResponse(json)


# 验证码验证页
def check_code(request):
    if request.method == "POST":
        m_username = request.session.get('m_username')
        m_password = request.session.get('m_password')
        m_code = request.session.get('m_code') - 123456
        m_email = request.session.get('m_email')
        m_name = request.session.get('m_name')
        code = request.POST.get('code')
        if m_username and m_password and m_code and code:
            exist_user = User.objects.filter(username=m_username).first()
            if exist_user:
                if str(code) == str(m_code):
                    exist_user.code = "000000"
                    exist_user.is_active = 1
                    exist_user.password = m_password
                    exist_user.save()
                    result = '验证码验证成功'
                    code = 1000
                else:
                    result = '验证码错误'
                    code = 1009
            elif m_email and m_name:
                if str(code) == str(m_code):
                    u = User()
                    u.username = m_username
                    u.password = m_password
                    u.email = m_email
                    u.name = m_name
                    u.is_active = 1
                    u.code = "000000"
                    u.save()
                    result = '验证码验证成功'
                    code = 1000
                else:
                    result = '验证码错误'
                    code = 1009
            else:
                result = '用户名不存在'
                code = 1004
        else:
            result = '未提交全部参数'
            code = 1002
    else:
        result = '未提交POST请求'
        code = 1001
    json = {
        "result": result,
        "code": code,
    }
    return JsonResponse(json)


@login_required
def logout(request):
    del request.session['user']
    result = '退出登录成功'
    json = {
        "result": result,
        "code": 1000,
    }
    return JsonResponse(json)


def forget_password(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        if username and email and new_password:
            exist_user = User.objects.filter(username=username).first()
            if exist_user:
                if email == exist_user.email:
                    pd = re.findall(r"^[a-z0-9_.]{6,16}$", new_password)
                    if pd and pd[0] == new_password:
                        if exist_user.is_active == 1:
                            code = get_code()
                            request.session['m_password'] = make_password(new_password)
                            request.session['m_code'] = code + 123456
                            request.session['m_username'] = username
                            try:
                                send_mail(email, code)
                                result = '验证码发送成功'
                                code = 1000
                            except Exception:
                                result = '验证码发送失败'
                                code = 1013
                        else:
                            result = '该用户已经被冻结'
                            code = 1005
                    else:
                        result = '新密码格式不正确'
                        code = 1008
                else:
                    result = '用户名与邮箱不匹配'
                    code = 1010
            else:
                result = '用户名不存在'
                code = 1003
        else:
            result = '未提交全部参数'
            code = 1002
    else:
        result = '未提交POST请求'
        code = 1001
    json = {
        "result": result,
        "code": code,
    }
    return JsonResponse(json)


@login_required
def change_password(request):
    user = User.objects.filter(username=request.session.get('user')).first()
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        if old_password and new_password:
            exist_password = check_password(old_password, user.password)
            if exist_password:
                pd = re.findall(r"^[a-z0-9_.]{6,16}$", new_password)
                if pd and pd[0] == new_password:
                    user.password = make_password(new_password)
                    user.save()
                    result = '密码修改成功'
                    code = 1000
                else:
                    result = '新密码格式不正确'
                    code = 1008
            else:
                result = '原密码不正确'
                code = 1004
        else:
            result = '未提交全部参数'
            code = 1002
    else:
        result = '未提交POST请求'
        code = 1001
    json = {
        "result": result,
        "code": code,
    }
    return JsonResponse(json)


@login_required
def change_name(request):
    user = User.objects.filter(username=request.session.get('user')).first()
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            if len(name) <= 16:
                user.name = name
                user.save()
                result = '昵称修改成功'
                code = 1000
            else:
                result = '昵称格式不正确'
                code = 1008
        else:
            result = '未提交全部参数'
            code = 1002
    else:
        result = '未提交POST请求'
        code = 1001
    json = {
        "result": result,
        "code": code,
    }
    return JsonResponse(json)


@login_required
def change_image(request):
    user = User.objects.filter(username=request.session.get('user')).first()
    image = request.FILES.get('image')
    image_size = request.FILES.get('image').size
    if image_size < 1024 * 1024 * 25:
        if image:
            if image.content_type in ('image/jpeg', 'image/jpg', 'image/png', 'application/x-png'):
                user.image = image
                user.save()
                result = '头像修改成功'
                code = 1000
            else:
                result = '图片格式不正确'
                code = 1008
        else:
            result = '未上传图片'
            code = 1002
    else:
        result = '文件大于25M'
        code = 1012
    json = {
        "result": result,
        "code": code,
    }
    return JsonResponse(json)


@login_required
def index(request):
    user = User.objects.filter(username=request.session.get('user')).first()
    user_index = {
        "username": user.username,
        "nickname": user.name,
        "icon": "http://47.102.46.161/media/" + str(user.image.name),
        "email": user.email,
    }
    want_read = []
    reading = []
    have_read = []
    books = State.objects.filter(user=user.username).all()
    if books:
        for book in books:
            if book.state == "0":
                book_index = Books.objects.filter(num=book.num).first()
                if book_index:
                    temp = {
                        "num": book.num,
                        "bookname": book_index.title,
                        "bookphoto": book_index.img_s,
                        "info": book_index.info,
                        "score": book_index.score,
                    }
                    want_read.append(temp)
            elif book.state == "1":
                book_index = Books.objects.filter(num=book.num).first()
                if book_index:
                    temp = {
                        "num": book.num,
                        "bookname": book_index.title,
                        "bookphoto": book_index.img_s,
                        "info": book_index.info,
                        "score": book_index.score,
                    }
                    reading.append(temp)
            elif book.state == "2":
                book_index = Books.objects.filter(num=book.num).first()
                if book_index:
                    temp = {
                        "num": book.num,
                        "bookname": book_index.title,
                        "bookphoto": book_index.img_s,
                        "info": book_index.info,
                        "score": book_index.score,
                    }
                    have_read.append(temp)
    json = {
        "user": user_index,
        "want_read": want_read,
        "reading": reading,
        "have_read": have_read,
        "result": '用户已登录',
        "code": 1000,
    }
    return JsonResponse(json)


def image_upload(request):
    image = request.FILES.get('image')
    image_size = request.FILES.get('image').size
    if image_size < 1024 * 1024 * 25:
        if image:
            if image.content_type in ('image/jpeg', 'image/jpg', 'image/png', 'application/x-png'):
                photo_name = str(time.time())[:10] + str(get_code())
                p = Photo()
                p.title = photo_name
                p.photo = image
                p.save()
                photo = Photo.objects.filter(title=photo_name).first()
                result = "http://47.102.46.161/media/" + str(photo.photo.name)
                code = 1000
            else:
                result = '图片格式不正确'
                code = 1008
        else:
            result = '未上传图片'
            code = 1002
    else:
        result = '文件大于25M'
        code = 1012
    json = {
        "result": result,
        "code": code,
    }
    return JsonResponse(json)


@login_required
def comment_request(request):
    user = User.objects.filter(username=request.session.get('user')).first()
    short_comment = []
    long_comment = []
    shorts = Short.objects.filter(user_id=user.id).all()
    longs = Long.objects.filter(user_id=user.id).all()
    if shorts:
        for short in shorts:
            book = Books.objects.filter(num=short.num).first()
            temp = {
                "id": short.id,
                "content": short.content,
                "score": short.score,
                "create_time": short.create_time,
                "num": short.num,
                "title": book.title,
                "image": book.img_s,
            }
            short_comment.append(temp)
    if longs:
        for long in longs:
            book = Books.objects.filter(num=long.num).first()
            temp = {
                "id": long.id,
                "long_title": long.title,
                "content": long.word,
                "score": long.score,
                "create_time": long.create_time,
                "num": long.num,
                "title": book.title,
                "image": book.img_s,
            }
            long_comment.append(temp)
    json = {
        "short": short_comment,
        "long": long_comment,
        "result": "用户已登录",
        "code": 1000,
    }
    return JsonResponse(json)


@login_required
def delete_comment(request):
    if request.method == 'GET':
        user = User.objects.filter(username=request.session.get('user')).first()
        comment_id = request.GET.get("comment_id")
        type = request.GET.get("type")
        if type == 'short' and comment_id:
            short = Short.objects.filter(id=comment_id).first()
            if short and str(short.user_id) == str(user.id):
                short.delete()
                result = '评论删除成功'
                code = 1000
            else:
                result = '该用户未发表此评论'
                code = 1011
        elif type == 'long' and comment_id:
            long = Long.objects.filter(id=comment_id).first()
            if long and str(long.user_id) == str(user.id):
                long.delete()
                result = '评论删除成功'
                code = 1000
            else:
                result = '该用户未发表此评论'
                code = 1011
        elif type not in ['short', 'long'] and comment_id:
            result = 'type参数不正确'
            code = 1008
        else:
            result = '未提交全部参数'
            code = 1002
    else:
        result = '未提交GET请求'
        code = 1001
    json = {
        'result': result,
        'code': code,
    }
    return JsonResponse(json)


# @login_required
# def state_add(request):
#     if request.method == 'GET':
#         user = User.objects.filter(username=request.user).first()
#         book_num = request.GET.get("book_num")
#         state = str(request.GET.get("state"))
#         if book_num and state:
#             book_exit = Books.objects.filter(num=book_num)
#             if book_exit and book_num:
#                 if state == '0':
#                     s = State()
#                     s.state = state
#                     s.num = book_num
#                     s.user_id = user.id
#                     s.save()
#                     result = '状态添加成功'
#                     code = 1000
#                 elif state == '1':
#                     s = State()
#                     s.state = state
#                     s.num = book_num
#                     s.user_id = user.id
#                     s.save()
#                     result = '状态添加成功'
#                     code = 1000
#                 elif state == '2':
#                     s = State()
#                     s.state = state
#                     s.num = book_num
#                     s.user_id = user.id
#                     s.save()
#                     result = '状态添加成功'
#                     code = 1000
#                 else:
#                     result = 'state参数不正确'
#                     code = 1011
#             else:
#                 result = '书籍不存在'
#                 code = 1003
#         else:
#             result = '未提交全部参数'
#             code = 1002
#     else:
#         result = '未提交GET请求'
#         code = 1001
#     json = {
#         'result': result,
#         'code': code,
#     }
#     return JsonResponse(json)

