import scrapy


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
            yield scrapy.Request(url=followers_link + '&offset=' + str(offset), callback=self.process_users_bunch)

        else:
            pass
            # TODO: notify user of error

    def process_users_bunch(self, response):
        users_bunch = response.css('div.people_row div.name a::attr(href)').extract()

        for user in users_bunch:
            profile_url = self.vk_url + user.strip(),
            yield scrapy.Request(url=profile_url[0], callback=self.parse_user_profile)

    def parse_user_profile(self, response):
        name = response.selector.xpath('//h2[@class="page_name"]/text()').extract()
        if not name:
            print(response.body)

        yield {
            'url': response.url,
            'name': name,
        }


    def parse(self, response):
        yield {
            't': response.selector.xpath('//h2[@class="page_name"]/text()').extract(),
            'title': response.css('h2.page_name').extract_first(),
        }

