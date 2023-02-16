import scrapy
import math
from scrapy.spiders import CrawlSpider, Spider
from scrapy.linkextractors import LinkExtractor

from ..items import MerlotItem

class MerlotSpider(Spider):
    name = "merlot"
    allowed_domains = ["merlot.org"]
    start_urls = ['https://merlot.org/merlot/materials.htm?page=1']
    pages = 0
    currentPage = 1
    categories_to_exclude = ['Online Course', 'Learning Object Repository',
                             'Hybrid or Blended Course', 'Online Course Module']

    def parse(self, response):
        if self.pages == 0:
            totalItems = response.xpath("//div[@class='results']/text()").extract()[0]
            totalItems = int(" ".join(totalItems.split()).split(" ")[2].replace(",", ""))
            self.pages = math.ceil(totalItems/24)

        for index, pageUrl in enumerate(response.xpath("//div[contains(@class, 'hitlist-item-header')]//a/@href").extract()):
            course_url = 'https://merlot.org' + pageUrl
            yield scrapy.Request(url=course_url, callback=self.parse_course)
        if self.currentPage < self.pages:
            self.currentPage += 1
            yield scrapy.Request(url='https://merlot.org/merlot/materials.htm?page=' + str(self.currentPage), callback=self.parse)


    def parse_course(self,response):
        materialType = response.xpath("//dl[contains(@class,'metadata-list')]/dd[1]/a/text()").extract()
        # controlla se un qualsiasi elemento di materialType combacia con un elemento di categories_to_exclude
        if any(x in materialType for x in self.categories_to_exclude):
            print("Not wanted course. Skipping")
        else:
            # =========== RATING =============
            try:
                rating = response.xpath("//div[@class='card quality-box']//li[2]/@title").extract()[0].split(" ")[3]
            except IndexError:
                rating = '0.0'

            # =========== LICENSE =============
            try:
                courseLicense = response.xpath("//a[@rel='license']/text()").extract()[2]
            except IndexError:
                courseLicense = "N/A"

            # =========== DESCRIPTION =============
            desc = response.xpath("//div[contains(@id,'material_description')]/p/text()").extract()
            if not desc:
                desc = response.xpath("//div[contains(@id,'material_description')]/text()").extract()
            if not desc:
                desc = response.xpath("//div[contains(@id,'material_description')]/span/text()").extract()[0]

            # =========== AUTHORS =============
            authorsList = response.xpath("//a[@itemprop='author']/span[1]/text()").extract()
            if not authorsList:
                authorsList = response.xpath("//span[@itemprop='author']/text()").extract()
            formattedAuthors = []
            for author in authorsList:
                formattedAuthors.append(" ".join(author.split()))



            item = MerlotItem()
            item["_id"] = response.url
            item["title"] = response.xpath("//div[contains(@class,'detail-title')]/h2/text()").extract()[0].replace('\n', '').lstrip(' ').rstrip(' ')
            item["description"] = desc[0]
            item["subject"] = response.xpath("//li[contains(@itemprop,'educationalAlignment')]//span/a/text()").extract()
            item["level"] = response.xpath("//dd[contains(@itemprop,'educationalRole')]//span/a/text()").extract()
            item["material_type"] = materialType
            item["author"] = formattedAuthors
            item["date_added"] = response.xpath("//dl[contains(@class,'metadata-list')]/dd[2]/text()").extract()[0]
            item["license"] = courseLicense
            item["language"] = response.xpath("//meta[@itemprop='inLanguage']/following::span[1]/text()").extract()[0]
            item["lor"] = "merlot"
            item["rating"] = rating
            # print(item)
            yield item

