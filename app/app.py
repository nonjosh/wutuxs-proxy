import time
import requests
from bs4 import BeautifulSoup
from hanziconv import HanziConv
from flask import Flask, render_template

# from flask import Flask, render_template, json, redirect, request

BASE_URL = "http://www.wutuxs.com"
RETRY_INTERVAL = 60 * 5  # unit in second
MAX_RETRY_NUM = 5

url = "http://www.wutuxs.com/html/9/9715/"

a_link = url.replace(BASE_URL, "")

# Flask constructor
app = Flask(__name__)


def get_soup(target_url):
    """
    Get soup object from target_url

    Args:
        target_url: target url
    Returns:
        soup: soup object
    """
    request_sucess = False
    retry_num = 0

    while not request_sucess:
        try:
            # Connect to the URL
            response = requests.get(target_url)
            if response.status_code == 200:
                response.encoding = "gb18030"
                request_sucess = True
            else:
                time.sleep(RETRY_INTERVAL)
        except requests.exceptions.RequestException:
            time.sleep(RETRY_INTERVAL)
        retry_num += 1
        # break and return current chapter if reach MAX_RETRY_NUM
        if retry_num >= MAX_RETRY_NUM:
            print("Reach max retry num, break and return current chapter")

    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def get_chapter_list():
    """
    Get chapter list from url

    Returns:
        chapter_list: chapter list
    """
    soup = get_soup(url)

    a_tags = soup.findAll("a")
    chapter_list = []
    for i in range(0, len(a_tags) - 1):  # 'a' tags are for links
        one_a_tag = a_tags[i]

        try:
            link = one_a_tag["href"]
            if link.startswith(a_link) and link != a_link:
                chapter_title = one_a_tag.string
                chapter_list.append((link, chapter_title))
        except KeyError:
            pass
    return chapter_list


# # Homepage URL call
# @app.route("/")
# def toc():
#     return render_template("home.html", headings=headings, data=data)


@app.route("/")
@app.route("/latest")
def latest():
    """
    Return the latest chapter
    """
    chapter_list = get_chapter_list()
    if len(chapter_list) > 0:
        # Get latest content
        latest_chapter_url, latest_chapter_title = chapter_list[-1]
    latest_chapter_soup = get_soup(BASE_URL + latest_chapter_url)
    title = HanziConv.toTraditional(latest_chapter_title)
    content = latest_chapter_soup.find("dd", id="contents")
    content = HanziConv().toTraditional(str(content))

    return render_template("latest.html", title=title, content=content)


# @app.route("/GetPlayerInfo/<row>")
# def GetPlayerInfo(row):
#     return row


# Listener
if __name__ == "__main__":
    app.run(port=2509, debug=True)
