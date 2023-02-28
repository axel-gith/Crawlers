import scrapy
from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
import math
from ..items import OercommonsItem

class OercommonsSpider(Spider):
    name = "oercommons"
    allowed_domains = ["oercommons.org"]
    start_urls = ['https://www.oercommons.org/browse?batch_size=100&sort_by=title&view_mode=summary']
    pages = 0
    current_page = 0
    # 'https://www.oercommons.org/browse?batch_size=100&batch_start=100'

    # rules = (
    #     # Rule(LinkExtractor(allow="batch_start"), callback="load_page"),
    #     Rule(LinkExtractor(allow=("courses","courseware","authoring"), deny="add"), callback="parse"),
    # )

    def parse(self, response):
        print("=================== page ", self.current_page)
        # print(response.xpath('//span[@class="items-number"]/text()').extract()[0])
        number_courses = int(response.xpath('//span[@class="items-number"]/text()').extract()[0])
        self.pages = math.ceil(number_courses / 100)
        for course_url in response.xpath("//div[@class='item-title']//a[@class='item-link js-item-link']/@href").extract():
            yield scrapy.Request(url=course_url, callback=self.parse_course)
        if self.current_page < self.pages:
            self.current_page += 1
            yield scrapy.Request(url='https://www.oercommons.org/browse?batch_size=100&batch_start=' + str(self.current_page * 100),callback=self.parse)

    def parse_course(self,response):
        format = response.css('span[itemprop="genre"]::text').get()
        if not format: format = 'N/A'
        license = response.css('[rel="license"]::text').get()
        if not license: license = response.css(".material-details-second-part .text").get()
        if license:
            license = license.replace('<dd class="text">', "").split("<img", 1)[0]
        else:
            license = ""
        lvl = response.css('dd')[2].get().replace("\n", "").replace("<dd>", "").replace("</dd>", "").replace(
            '<span class="tx">', "").replace("</span>", "")
        item = OercommonsItem()
        item["_id"] = response.url
        item["title"] = response.css('h1 [itemprop="name"]::text').get()
        item["description"] = response.css('[itemprop="description"]::text').get()
        item["subject"] = response.css('[itemprop="about"]::text').getall()
        item["level"] = lvl.lstrip(' ').rstrip(' ').split(",")
        item["material_type"] = response.css('[itemprop="learningResourceType"]::text').get()
        item["format"] = format
        item["author"] = response.css('[itemprop="author"] a::text').getall()
        item["date_added"] = response.css(".text::text")[1].get()
        item["license"] = license.replace("\n", "").lstrip(' ').rstrip(' ')
        item["language"] = response.css('[itemprop="inLanguage"]::text').get()
        item["lor"] = "oercommons"
        item["rating"] = response.css('.stars::attr(data-rating-value)')[0].extract()
        item["number_visits"] = response.css('.counter-item:nth-child(1) span:nth-child(3)::text').get()
        item["number_saves"] = response.css('.counter-item:nth-child(2) span:nth-child(3)::text').get()

        yield item

    # def parse_item(self, response):
    #     yield {
    #         "title": response.css('h1 [itemprop="name"]::text').get(),
    #         "url": response.url,
    #         "description":  response.css('[itemprop="description"]::text').get(),
    #         "subject": response.css('[itemprop="about"]::text').get(),
    #         "level": response.css('dd::text')[3].get().replace("\n", "").lstrip(' ').rstrip(' '),
    #         "material_type": response.css('[itemprop="learningResourceType"]::text').get(),
    #         "author": response.css('[itemprop="author"] a::text').getall(),
    #         "date_add": response.css(".text::text")[1].get(),
    #         "license": response.css('[rel="license"]::text').get().replace("\n", "").lstrip(' ').rstrip(' '),
    #         "language": response.css('[itemprop="inLanguage"]::text').get(),
    #         "lor": "oercommons",
    #         "rating": response.css('.stars::attr(data-rating-value)')[0].extract()
    #     }
    #
    #
    # def load_page(self,response):
    #     next_page = response.css('.pagination a::attr(href)').extract()
    #     if next_page:
    #         next_href = next_page[0]
    #         next_page_url = 'https://www.oercommons.org' + next_href
    #         request = scrapy.Request(url=next_page_url)
    #         yield request