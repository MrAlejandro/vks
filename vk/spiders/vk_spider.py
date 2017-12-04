import time
import scrapy
from scrapy.selector import Selector

class QuotesSpider(scrapy.Spider):
    name = 'vk'
    vk_url = 'https://vk.com'

    def start_requests(self):
        yield scrapy.Request(url='https://vk.com/eminlive', callback=self.fetch_group_users)

    def fetch_group_users(self, response):
        followers_link = response.selector.xpath('//div[@id="public_followers"]/a/@href').extract_first()
        followers_link = self.vk_url + followers_link.strip()

        if followers_link:
            offset = 0

            for offset in range(0, 700, 20):
                yield scrapy.Request(url=followers_link + '&offset=' + str(offset), callback=self.process_users_bunch, priority=1)
                time.sleep(0.5)

        else:
            pass
            # TODO: notify user of error

    def process_users_bunch(self, response):
        users_bunch = response.css('div.people_row div.name a::attr(href)').extract()

        for user in users_bunch:
            profile_url = self.vk_url + user.strip(),
            yield scrapy.Request(url=profile_url[0], callback=self.parse_user_profile)

    def parse_user_profile(self, response):
        name = response.selector.xpath('//h2[@class="page_name"]/text()').extract_first()

        if not name:
            # TODO: notify of error
            pass

        user_data = {
            'url': response.url,
            'name': name,
        }

        for row in response.selector.xpath('//div[contains(@class, "profile_info_row")]'):
            key = row.xpath('./div[contains(@class, "label")]/text()').extract_first()
            links = row.xpath('./div[contains(@class, "labeled")]/a/text()').extract()
            value = ' '.join(links)

            if not value:
                value = row.xpath('./div[contains(@class, "labeled")]/text()').extract_first()
            else:
                url = row.xpath('./div[contains(@class, "labeled")]/a/@href').extract_first()

                if url and not url[0] == '/':
                    value += ' (url:' + url + ')'

            if key and value:
                user_data[key.replace(':', '')] = value.strip()

        yield user_data


    def parse(self, response):
        yield {
            't': response.selector.xpath('//h2[@class="page_name"]/text()').extract(),
            'title': response.css('h2.page_name').extract_first(),
        }

