# -*- coding:utf-8 -*-
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponse
import re
import json as jss
from datetime import datetime, timedelta
from app.models import *
from bs4 import BeautifulSoup
import requests

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.79 Safari/537.36'
}


def Detail(num, url='https://book.douban.com/subject/', flag='1'):
    url = 'https://book.douban.com/subject/'

    http = requests.get(url + num + "/", headers=header)
    txt = http.content.decode('utf-8')

    introduce = re.findall('<div class="intro">(.*?)</div>', txt, re.S)
    for i in range(len(introduce)):
        introduce[i] = introduce[i].replace('<p>', '').replace('</p>', '\n')
    if len(introduce) >= 2 and introduce[0][:31] == introduce[1][:31]:
        introduce = introduce[1]
    else:
        introduce = introduce[0]

    img_s = 'https:' + re.findall('<img src="https:(.*?)"', txt, re.S)[0]
    img_l = img_s.replace('/s/', '/l/')

    info = re.findall('<div id="info" class="">(.*?)</div>', txt, re.S)[0].replace('  ', '').replace('\n\n', '')[7:]
    del_list = re.findall('<.*?>', info, re.S)
    for i in del_list:
        info = info.replace(i, ' ')

    score = re.findall('<strong class="ll rating_num " property="v:average"> (.*?) </strong>', txt, re.S)[0]

    try:
        score = float(score)
    except:
        score = '5'
    finally:
        score = str(score)

    title = re.findall('<span property="v:itemreviewed">(.*?)</span>', txt, re.S)[0]

    if flag == '1':
        temp = {
            "title": title,
            "info": info,
            "img": {'img_l': img_l, 'img_s': img_s},
            "introduce": introduce,
            'score': score,
        }

        return temp

    else:

        book_file = Books(num=num, title=title, info=info, introduce=introduce,
                          score=score, img_l=img_l, img_s=img_s)
        book_file.save()
        '''
    num = models.TextField(verbose_name='书籍ID')
    title = models.TextField(verbose_name='标题')
    info = models.TextField(verbose_name='相关信息')
    introduce = models.TextField(verbose_name='简介')
    score = models.TextField(verbose_name='评分')
    img_l = models.TextField(verbose_name='img_l')
    img_s = models.TextField(verbose_name='img_s')
        '''


def get_init(request):
    url = 'https://market.douban.com/book/?type=topic'

    for page in range(1, 4):  # 6*17 的书单,page为书单页的页数，一页有17个书单
        response = requests.get(url + '&page=' + str(page), headers=header)
        txt = response.content.decode('utf-8')

        # 一页, 17个
        title_list = re.findall('<h3>(.*?)</h3>', txt, re.S)[1:]
        content_list = re.findall('<p>(.*?)</p>', txt, re.S)[2:]
        card_list = re.findall('<div class="card">(.*?)</div>', txt, re.S)[1:]
        href_list = re.findall('<a href="(.*?)".*?class="special-item">', txt, re.S)[1:]
        front_url = 'https://market.douban.com'

        for count in range(17):

            cover_img = []
            cards = card_list[count].split('\n')
            for i in cards:
                img = re.findall('<img src="(.*?)" alt=".*?"/>', i, re.S)
                if img:
                    cover_img.append(img[0])

            # 进入书单的详情页面

            books = requests.get(front_url + href_list[count], headers=header).content.decode('utf-8')
            books = re.findall("'page': (.*?),\n", books, re.S)[0]

            details = jss.loads(books)['detail']['cards']

            info_list = []
            for detail in details:
                book_id = detail['subject_id']
                title = detail['title']
                desc = detail['desc'].replace('<b>', '').replace('</b>', '')
                img = detail['info']['cover']['url']
                info = detail['info']['meta'].split(' / ')[1:]

                info_list.append({
                    "title": title,
                    "image": img,
                    "author": ' / '.join(info),
                    "content": desc,
                    "num": book_id
                })
                if not Books.objects.filter(num=book_id):
                    Detail(num=book_id, flag='0')
                    print('正在加载书籍信息')

            book_list_file = Book_list(name=title_list[count], image=cover_img[0],
                                       number=str(len(info_list)), content=content_list[count],
                                       info=str(info_list), list_class=str(count % 5 + 1))
            book_list_file.save()
            print('正在加载书单信息')

            # book_list = {
            #     'name': title_list[count],
            #     'image': cover_img[0],
            #     'number': str(len(info_list)),
            #     'content': content_list[count]
            # }
            #
            #
            # js = {
            #     'book_list': book_list,
            #     'info': info_list
            # }

    return HttpResponse('200')


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
            json = {"result": '401', 'detail': '用户未登陆'}
            return JsonResponse(json, charset='utf-8', safe=False, json_dumps_params={'ensure_ascii': False})

    return wrapper


def book_list1(request):  # 每个书单
    if not request.GET.get('list_id'):

        return JsonResponse({'result': '400', 'detail': '参数有误'}, charset='utf-8', safe=False, json_dumps_params={'ensure_ascii': False})

    list_id = request.GET.get('list_id')
    list_file = Book_list.objects.get(id=list_id)
    js = {
        'book_list': {
            'name': list_file.name,
            'image': list_file.image,
            'number': list_file.number,
            'content': list_file.content,
        },

        'info': eval(list_file.info)
    }
    '''
    list_class = models.TextField(verbose_name='书单类型')
    name = models.TextField(verbose_name='书单名')
    image = models.TextField(verbose_name='图片')
    number = models.TextField(verbose_name='书单里书本的数量')
    content = models.TextField(verbose_name='内容')
    info = models.TextField(verbose_name='相关信息')
    '''
    return JsonResponse(js, charset='utf-8', safe=False, json_dumps_params={'ensure_ascii': False})


def book_list2(request):  # 书单的详情
    if not request.GET.get('list_class'):
        return JsonResponse({'result': '400', 'detail': '参数有误'}, charset='utf-8', safe=False,
                            json_dumps_params={'ensure_ascii': False})

    list_class = request.GET.get('list_class')

    book_list_list = Book_list.objects.filter(list_class=list_class)
    book_list = []
    for i in book_list_list:
        book_list.append(
            {
                "name": i.name,
                "image": i.image,
                "number": i.number,
                "num": i.id,
            }
        )

    js = {
        'book': book_list
    }

    return JsonResponse(js,
                        charset='utf-8', safe=False, json_dumps_params={'ensure_ascii': False})


def new_book_spyder():

    def delete_kg(str):
        if type(str) != type('str'):
            return str
        else:
            a = ""
            for i in str:
                if i in [" ", "\n", "\t"]:
                    pass
                else:
                    a = a + i
            return a

    url = "https://book.douban.com/latest?icn=index-latestbook-all"

    session = requests.session()
    page = session.get(url, headers=header)
    html = page.content.decode('utf8')
    soup = BeautifulSoup(html, "html.parser")
    unreal = soup.find("div", {"class": "article"})
    unreal_li = unreal.find_all("li")
    unreal_list = []
    for li in unreal_li:
        image = li.find("img").get("src")
        title_p = li.find("h2").text
        title = delete_kg(title_p)
        score_p = li.find("p", {"class": "rating"}).text
        score = delete_kg(score_p)
        author_p = li.find("p", {"class": "color-gray"}).text
        author = delete_kg(author_p)
        content_p = li.find("p", {"class": "detail"}).text
        content = delete_kg(content_p)
        num_p = li.find("a").get("href")
        num = num_p.split("/")[-2]
        temp = {
            "image": image,
            "title": title,
            "score": score,
            "author": author,
            "content": content,
            "num": num
        }
        unreal_list.append(temp)


    js = []
    for i in unreal_list:  # real_list
        score = i['score']
        try:
            score = float(score)
        except:
            score = '5'
        finally:
            score = str(score)
        js.append({
            "title": i['title'],
            "image": i['image'],
            "author": i['author'],
            "content": i['content'],
            "num": i['num'],
            "score": score
        })
        if not Books.objects.filter(num=i['num']):
            Detail(num=i['num'], flag='0')

    return js

new_book_list = [{'title': '生活与命运', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33562090.jpg', 'author': '[俄罗斯]瓦西里·格罗斯曼/理想国丨四川人民出版社/2020-2', 'content': '全面描写斯大林苏联社会生活的真实面貌。它是一整个时代的画像和心灵史，体制下复杂多面生活的一部百科全书，20世纪最黑暗的一段历史的深刻反思。', 'num': '34928037', 'score': '8.8'}, {'title': '春日之书', 'image': 'https://img9.doubanio.com/view/subject/s/public/s33534795.jpg', 'author': '陆烨华/人民文学出版社/2020-3', 'content': '杂志编辑部连续五周收到匿名投稿，内容为一篇短篇推理小说。五个短篇，最后串联成一个完整的长篇推理。编辑张悠悠为了破解小说中的谜团，展开调查。', 'num': '34822422', 'score': '8.4'}, {'title': '草仍然绿，水仍在流', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33595640.jpg', 'author': '[加]托马斯·金/南京大学出版社/2020-3-20', 'content': '小说编织了现代生活和神话故事两条故事线索。两条线索在小说结尾交织，真实与想象重叠汇合……当代美洲文学“跨界之作”，可疑的北美原住民魔幻现实。', 'num': '34995955', 'score': '5'}, {'title': '梅塘之夜', 'image': 'https://img1.doubanio.com/view/subject/s/public/s33559908.jpg', 'author': '(法)左拉等/译林出版社/2020-2-1', 'content': '19世纪70年代末期，在左拉的提议下，他和阿莱克西、于斯曼、莫泊桑、塞阿尔、埃尼克这六位作家各写了一篇关于普法战争的小说，于是就诞生了这部《梅塘之夜》。', 'num': '34866954', 'score': '9.0'}, {'title': '血与火：坦格利安王朝史第一卷', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33531723.jpg', 'author': '[美]乔治·R·R·马丁/重庆出版社/2020-2', 'content': '全书以铁王座缔造者、传奇的“征服者”伊耿为开端，讲述了坦格利安王朝历代权力斗争。本书由乔治·马丁托名学城学士“葛尔丹”撰写。', 'num': '34907838', 'score': '9.3'}, {'title': '生尸之死', 'image': 'https://img1.doubanio.com/view/subject/s/public/s33594789.jpg', 'author': '[日]山口雅也/新星出版社/2020-2', 'content': '“墓碑村”周围最近发生了一些怪事，死去的人又站了起来，有的还若无其事地冲到了街上！……如果人能死而复生，那蓄意谋杀还有什么意义呢？', 'num': '34907836', 'score': '7.8'}, {'title': '北方狩猎', 'image': 'https://img1.doubanio.com/view/subject/s/public/s33595138.jpg', 'author': '魏市宁/陕西师范大学出版总社/2020-2', 'content': '4个悬疑故事，4段奇情人生，4则荒诞又现实的小人物之歌。冷酷怪诞，野性生猛，生活写实与心理惊悚的精彩融合，反转直到结尾一刻的阅读体验。', 'num': '34950090', 'score': '9.6'}, {'title': '柠檬桌子', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33587552.jpg', 'author': '[英]朱利安·巴恩斯/江苏凤凰文艺出版社/2020-3', 'content': '11个短篇淋漓尽致地展现了变老的每一种可能，在时间被缓慢榨尽的故事中，展现生命的真实。布克奖得主朱利安·巴恩斯作品。', 'num': '34969918', 'score': '8.4'}, {'title': '神探福迩，字摩斯', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33607582.jpg', 'author': '莫理斯/北京时代华文书局/2020-3', 'content': '神探福迩，字摩斯，满族镶蓝旗，主要活跃于光绪年间，其事迹由生平挚友华笙大夫记载……向福尔摩斯致敬的本土化作品。', 'num': '34885303', 'score': '9.2'}, {'title': '废墟阅读者', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33582583.jpg', 'author': '[法]大卫·博沙尔/DavidB./后浪丨贵州人民出版社/2020-4', 'content': '每个在战争中死去的人都会重生为天上的星星？11月1日发动进攻会带来不幸？梦见公交车是死亡在即的征兆？欢迎来到大卫·博沙尔的虚幻、怪诞世界。', 'num': '34920873', 'score': '5'}, {'title': '奥斯维辛的文身师', 'image': 'https://img9.doubanio.com/view/subject/s/public/s33601765.jpg', 'author': '[澳]希瑟·莫里斯/湖南文艺出版社/2020-3', 'content': '犹太人拉莱被迫当上集中营里的文身师，在囚犯的皮肤上留下印记。一日，拉莱在等候文身的队伍中邂逅了一名年轻女子，拉莱默默发誓，他们一定要活下来……', 'num': '34908363', 'score': '8.3'}, {'title': 'Sunny星之子', 'image': 'https://img1.doubanio.com/view/subject/s/public/s33529469.jpg', 'author': '[日]松本大洋/北京联合出版公司/2020-2', 'content': '在学园的角落有一辆废弃的Sunny1200轿车，这里是专属孩子们的秘密基地。孩子们相信，只要用念力开动Sunny，就能去到任何想去的地方。松本大洋漫画作品。', 'num': '34439699', 'score': '9.5'}, {'title': '第十二张牌', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33593113.jpg', 'author': '[美]杰夫里·迪弗/新星出版社/2020-4-1', 'content': '一百四十年前到底埋葬了什么秘密，会让一条鲜活的无辜生命被残忍杀害？杀手留下的塔罗牌——倒吊的人中，又隐藏着什么让人不寒而栗的信息？', 'num': '34970027', 'score': '5'}, {'title': '心！', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33555062.jpg', 'author': '陈希我/北京十月文艺出版社/2020-3', 'content': '日籍华人代表林修身回国后离奇地因“心脏破碎”去世。在对他生前故事的探询与追踪中，林修身的形象却越来越难以辨认，被构建起来的个体历史同时也在被解构。', 'num': '34881568', 'score': '5'}, {'title': '二重身', 'image': 'https://img9.doubanio.com/view/subject/s/public/s33590824.jpg', 'author': '[日]法条遥/化学工业出版社/2020-4', 'content': '二重身的容貌、记忆与本体一模一样，他们会破坏、夺取本体的生活，最终取而代之。没有人能确定，死去的究竟是二重身还是本体。', 'num': '34833836', 'score': '5'}, {'title': '蓝莓上尉：联盟国的宝藏', 'image': 'https://img9.doubanio.com/view/subject/s/public/s33563156.jpg', 'author': '[比]让-米歇尔·沙利耶编/[法]墨比斯绘/后浪丨湖南美术出版社/2020-4', 'content': '悍匪势如虎狼，枭雄九死无悔，且看蓝莓上尉如何在茫茫沙海搅起滔天巨浪。', 'num': '34952515', 'score': '5'}, {'title': '在森崎书店的日子', 'image': 'https://img1.doubanio.com/view/subject/s/public/s33609809.jpg', 'author': '八木泽里志/南海出版公司/2020-3-1', 'content': '我在森崎书店的日子，是从夏初到翌年的初春。房间光线不好，又很狭窄，再加上旧书的霉味挥之不去。然而直到今天，我从未忘怀过在那里度过的时光。', 'num': '34800934', 'score': '5'}, {'title': '树叶裙', 'image': 'https://img1.doubanio.com/view/subject/s/public/s33563107.jpg', 'author': '[澳]帕特里克·怀特/浙江文艺出版社/2020-1', 'content': '年轻的英国贵妇艾伦在海难后沦为澳洲岛民部落的奴隶，历经坎坷。然而，在回归文明世界的曙光到来时，她不知自己是否做好了准备……诺奖得主帕特里克·怀特作品。', 'num': '34879510', 'score': '7.6'}, {'title': '城堡', 'image': 'https://img3.doubanio.com/view/subject/s/public/s33544790.jpg', 'author': '[奥地利]弗兰茨·卡夫卡/天津人民出版社/2020-1', 'content': '城堡虽然近在咫尺，却是K.可望而不可即的……卡夫卡名作。', 'num': '34856482', 'score': '8.5'}, {'title': '欲望的旗帜', 'image': 'https://img9.doubanio.com/view/subject/s/public/s33586354.jpg', 'author': '格非/浙江文艺出版社/2020-1', 'content': '一场重要学术会议召开前夕，大会主席贾教授毫无预兆地跳楼自杀身亡，会议不得不中断。贾教授生前的信息通过其他人的回忆一点点拼贴起来，故事也随之展开。', 'num': '34841771', 'score': '8.6'}]



def new_book(request):
    """新书速递"""

    js = {
        'book': new_book_list
    }

    return JsonResponse(js,
                        charset='utf-8', safe=False, json_dumps_params={'ensure_ascii': False})


def comment_number(num):
    num = str(num)
    user_list = []
    shorts = Short.objects.filter(num=num).all()
    longs = Long.objects.filter(num=num).all()
    for short in shorts:
        if short.user_id not in user_list:
            user_list.append(short.user_id)
    for long in longs:
        if long.user_id not in user_list:
            user_list.append(long.user_id)
    number = len(user_list)
    return number


def book(request):
    if not request.GET.get('num'):
        return JsonResponse({'result': '400', 'detail': '参数有误'}, charset='utf-8', safe=False,
                            json_dumps_params={'ensure_ascii': False})
    num = request.GET.get('num')
    book_fail = Books.objects.filter(num=num).first()
    book_fail.people = comment_number(num)
    book_fail.save()
    detail1 = {
        "title": book_fail.title,
        "info": book_fail.info,
        "img": {'img_l': book_fail.img_l, 'img_s': book_fail.img_s},
        "introduce": book_fail.introduce,
        'score': book_fail.score,
    }

    detail2 = {
        "people": book_fail.people,
        "done": book_fail.done,
        "progress": book_fail.progress,
        "want": book_fail.want,
    }
    book_detail = {**detail1, **detail2}
    #  根据数据库对book_list操作

    long_comments = Long.objects.filter(num=num)
    comment_list2 = []
    if long_comments:
        long_flag = '1'
        for i in long_comments:
            username = i.user.username
            user_file = User.objects.get(username=username)
            state_file = State.objects.filter(user=username, num=num)[0]
            comment_list2.append({
                "image": user_file.image.name,
                "name": username,
                "status": state_file.state,  # 0，1，2分别代表想读，在读，已读(默认为3)
                "content": i.content,
                "title": i.title,
                "word": i.word,
                "score": i.score,
                "time": i.create_time,
                "book_num": num,
            }
            )
    else:
        long_flag = '0'

    short_comments = Short.objects.filter(num=num)
    comment_list1 = []
    if short_comments:
        short_flag = '1'
        for i in short_comments:
            username = i.user.username
            user_file = User.objects.get(username=username)
            state_file = State.objects.filter(user=username, num=num)[0]

            comment_list1.append(
                {
                    "image": user_file.image.name,
                    "name": username,
                    "status": state_file.state,  # 0，1，2分别代表想读，在读，已读(默认为3)
                    "content": i.content,
                    "score": i.score,
                    "time": i.create_time,
                    "book_num": num,
                }
            )
    else:
        short_flag = '0'

    json = {
        "book": book_detail,
        "shortcomments": comment_list1,
        "bookcomments": comment_list2,
        "number": {
            'shortcomments': short_flag,
            'bookcomments': long_flag,
        },
    }

    return JsonResponse(json, charset='utf-8', safe=False, json_dumps_params={'ensure_ascii': False})


@login_required
def book_review(request):
    if not (request.GET.get('num') and request.GET.get('type')):
        return JsonResponse({'result': '400', 'detail': '参数有误'}, charset='utf-8', safe=False,
                            json_dumps_params={'ensure_ascii': False})

    num = request.GET.get('num')
    type = request.GET.get('type')
    username = request.session.get('user')

    if request.method == 'POST':
        # comments = request.POST.get("comments")
        comments = {
            'title': request.POST.get('title'),
            "content": request.POST.get('content'),
            "score": request.POST.get('score')

        }
        '''
        'title': '评论标题'
        "content": "书评内容"
        "score": "评分"
        "book_num": '书籍id'
        '''

        if type == 'l':
            word = comments['content']
            del_list = re.findall("<.*?>", comments['content'], re.S)
            for i in del_list:
                word = word.replace(i, '')

            view_file = Long(user=User.objects.get(username=username), num=num, content=comments['content'],
                             title=comments['title'], score=comments['score'], word=word)

            view_file.save()
            result = '200'
            detail = 'OK'
        elif type == 's':
            view_file = Short(user=User.objects.get(username=username), num=num, content=comments['content'], score=comments['score'])

            view_file.save()
            result = '200'
            detail = 'OK'

        else:
            result = '400'
            detail = '参数有误'

    else:
        result = '402'
        detail = '请求有误'

    return JsonResponse({'result': result, 'detail': detail}, charset='utf-8', safe=False, json_dumps_params={'ensure_ascii': False})


@login_required
def status(request):
    if not request.GET.get('num'):
        return JsonResponse({'result': '400', 'detail': '参数有误'}, charset='utf-8', safe=False,
                            json_dumps_params={'ensure_ascii': False})
    username = request.session.get('user')
    num = request.GET.get('num')
    book_file = Books.objects.filter(num=num).first()

    if request.method == 'GET':
        if State.objects.filter(num=num, user=username):
            pass
        else:
            file = State(num=num, user=username)
            file.save()
        return JsonResponse({"result": State.objects.filter(num=num, user=username).first().state}, charset='utf-8', safe=False,
                            json_dumps_params={'ensure_ascii': False})

    elif request.method == 'POST':

        status_file = State.objects.filter(num=num, user=username)
        if status_file:
            state1 = status_file.first().state
            status_file.delete()
        else:
            state1 = '3'

        status_file = State(num=num, user=username)

        condition = request.POST.get('status')

        done = int(book_file.done)
        progress = int(book_file.progress)
        want = int(book_file.want)

        if state1 == '2':
            done -= 1
        elif state1 == '1':
            progress -= 1
        elif state1 == '0':
            want -= 1

        if condition == '2':
            done += 1
        elif condition == '1':
            progress += 1
        elif condition == '0':
            want += 1

        status_file.state = condition
        status_file.save()

        book_file.want = str(want)
        book_file.progress = str(progress)
        book_file.done = str(done)

        book_file.save()

        result = '200'
        detail = 'OK'

    else:
        result = '402'
        detail = '请求有误'
    return JsonResponse({"result": result, 'detail': detail}, charset='utf-8', safe=False, json_dumps_params={'ensure_ascii': False})


def delete_database(request):
    Long.objects.all().delete()
    Short.objects.all().delete()
    return HttpResponse('200')