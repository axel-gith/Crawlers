from requests_html import HTMLSession
import pymongo
from pymongo import MongoClient
import certifi

CONNECTION_STRING = "mongodb+srv://<usr>:<psw>@moodlerec.w2j6m9t.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
dbname = client['moodlerec']
collection = dbname['wisconline']

url = "https://www.wisc-online.com"
s = HTMLSession()
r = s.get(url)

r.html.render(sleep=1)

def get_learning_obj(categoryurl):
    resp = s.get(url + categoryurl)
    resp.html.render(sleep=1)
    for index, title in enumerate(resp.html.xpath("//div[contains(@class, 'searchItemModel-title')]/p/a/text()")):
        current_xpath_element = "(//div[contains(@class,'searchItemModel ')])[" + str(index + 1) + "]"
        authors = resp.html.xpath(current_xpath_element + "//span[contains(@class ,'authors')]/text()")
        if not authors:
            authors = ['N/A']
        partial_url = resp.html.xpath(current_xpath_element + "//div[contains(@class, 'searchItemModel-title')]/p/a/@href")[0]
        try:
            description = resp.html.xpath(current_xpath_element + "//a[contains(@class,'descriptionText')]/p/text()")[0]
        except IndexError:
            description = ['N/A']
        thumbs_up = resp.html.xpath(current_xpath_element + "//span[contains(@class,'glyphicon glyphicon-thumbs-up')]/following-sibling::text()")[0]
        views = resp.html.xpath(current_xpath_element + "//span[contains(@class,'glyphicon glyphicon-eye-open')]/following-sibling::text()")[0]
        objToSave = {
            "_id": url + partial_url,
            "title": title,
            "authors": authors[0].split(","),
            "description": description,
            "thumbs_up": thumbs_up.replace("\n", "").lstrip(' ').rstrip(' '),
            "views": views.replace("\n", "").lstrip(' ').rstrip(' '),
            "lor": "wisc-online"
        }
        try:
            collection.insert_one(objToSave)
            print(index, " - ", objToSave)
        except pymongo.errors.DuplicateKeyError:
            print("duplicate")
            continue

    pageInfo  = resp.html.xpath("//div[contains(@class,'pageNumberDisplay')]/text()")
    if pageInfo:
        pageInfo = pageInfo[0].split(' ')
        categoryurl_no_page = (categoryurl.split("?"))[0]
        go_to_next_page(pageInfo, categoryurl_no_page)
    else:
        print("No next page")
    return

def go_to_next_page(page_info, category_url):

    current_page = int(page_info[1])
    last_page = int(page_info[3])
    print('########', page_info, current_page, last_page )
    if current_page < last_page:
        current_page += 1
        print('=== ', category_url + "?s=Rating&d=Desc&p=" + str(current_page))
        get_learning_obj(category_url + "?s=Rating&d=Desc&p=" + str(current_page))

all_categories = r.html.xpath("//li[contains(@class, 'linkContainer')]/a/@href")
# \
for category in all_categories:
    print(category)
    get_learning_obj(category)




