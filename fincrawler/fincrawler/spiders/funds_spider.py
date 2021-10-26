import requests
import scrapy


class FundsSpider(scrapy.Spider):
    name = "funds"
    cnpjs = [
        '23.865.920/0001-78',
        '35.637.151/0001-30',
    ]

    def start_requests(self):
        urls = self.make_urls()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def make_urls(self) -> list:
        return [
            f'https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CConsolFdo/ResultBuscaParticFdo.aspx?CNPJNome='
            f'{cnpj}&TpPartic=0&Adm=false&SemFrame='
            for cnpj in self.cnpjs
        ]

    def parse(self, response):
        data = {
            "__EVENTTARGET": "ddlFundos$_ctl0$Linkbutton2",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": response.xpath('//input[contains(@id, "__VIEWSTATE")]/@value').get(),
            "__VIEWSTATEGENERATOR": response.xpath('//input[contains(@id, "__VIEWSTATEGENERATOR")]/@value').get(),
            "__EVENTVALIDATION": response.xpath('//input[contains(@id, "__EVENTVALIDATION")]/@value').get(),
        }
        post_response = requests.post(response.url, data=data)
        yield response.follow(post_response.url, callback=self.parse_detail_funds)

    def parse_detail_funds(self, response):
        link_cda = response.xpath('//a[contains(@id, "Hyperlink1")]/@href').get()
        link_cda = link_cda.split('..')[-1]
        url = f'https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/{link_cda}'
        yield response.follow(url, callback=self.get_cda)

    def get_cda(self, response):
        self.log(f'-------------------------->>>>> {response.url}')
