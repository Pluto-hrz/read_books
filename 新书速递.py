from bs4 import BeautifulSoup
import requests
import re


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
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.79 Safari/537.36'
}
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
real = soup.find("div", {"class": "aside"})
real_li = real.find_all("li")
real_list = []
for li in real_li:
    image = li.find("img").get("src")
    title_p = li.find("h2").text
    title = delete_kg(title_p)
    score_p = li.find("p", {"class": "rating"}).text
    score = delete_kg(score_p)
    author_p = li.find("p", {"class": "color-gray"}).text
    author = delete_kg(author_p)
    content_p = li.find_all("p")[2].text
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
    real_list.append(temp)

print(unreal_list)
print (real_list)



