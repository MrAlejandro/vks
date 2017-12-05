import scrapy
from scrapy.selector import Selector
import logging

class VkSpider(scrapy.Spider):
    name = 'vk'
    vk_url = 'https://vk.com'
    group_url = ''
    priority = 1

    def __init__(self, group='', *args, **kwargs):
        super(VkSpider, self).__init__(*args, **kwargs)
        self.group_url = group

    def start_requests(self):
        if self.group_url:
            yield scrapy.Request(url=self.group_url, callback=self.fetch_group_users)
        else:
            logging.error("You should pass VK group URL, ex: \033[1;31mscrapy crawl vk -o users.jl -a group=https://vk.com/eminlive\033[0m")

    def fetch_group_users(self, response):
        followers_link = response.selector.xpath('//div[@id="public_followers"]/a/@href').extract_first()
        followers_link = self.vk_url + followers_link.strip()

        if followers_link:
            offset = 0

            for offset in range(0, 1000, 20):
                yield scrapy.Request(url=followers_link + '&c[sex]=1&offset=' + str(offset), callback=self.process_users_bunch, priority=self.priority)
                yield scrapy.Request(url=followers_link + '&c[sex]=2&offset=' + str(offset), callback=self.process_users_bunch, priority=self.priority+1)

            self.priority += 1

        else:
            pass
            # TODO: notify user of error

    def process_users_bunch(self, response):
        users_bunch = response.selector.xpath('//div[contains(@class, "info")]/div[contains(@class, "name")]/a/@href').extract()
        self.priority += 1

        for user in users_bunch:
            profile_url = self.vk_url + user.strip(),
            yield scrapy.Request(url=profile_url[0], callback=self.parse_user_profile, priority=self.priority)

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

