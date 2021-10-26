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
        yield response.follow(url, callback=self.parse_cda)

    def parse_cda(self, response):
        fund_name = response.xpath('//span[contains(@id, "lbNmDenomSocial")]/text()').get()
        fund_cnpj = response.xpath('//span[contains(@id, "lbNrPfPj")]/text()').get()
        fund_admin = response.xpath('//span[contains(@id, "lbNmDenomSocialAdm")]/text()').get()

        table = response.css('table#dlAplics')

        datetime_register_cda = table.xpath('//span[contains(@id, "lbDtRegDoc")]/text()').get()

        rows = table.xpath('./tr')[4:]
        rowsdata = [row.xpath('./td') for row in rows]

        exclude_ativos = ['Valores a pagar', 'Valores a receber']
        rowsdata = [
            data for data in rowsdata
            if data.xpath('./span/text()')[0].get().strip().upper() not in [item.upper() for item in exclude_ativos]
        ]

        data = {
            "nome": fund_name,
            "cnpj": fund_cnpj,
            "administrador": fund_admin,
            "datetime_registro_cda": datetime_register_cda,
            "cda": [
                {
                    "ativo": rowdata.xpath('./span/text()')[1].get().strip(),
                    "tipo_ativo": rowdata.xpath('./span/text()')[0].get().strip(),
                    "quantidade": self.get_quantity(rowdata),
                    "valor_mercado": rowdata.xpath(
                        "./span[@id[substring(.,string-length(.) - string-length('VlPosFim') + 1) = 'VlPosFim']]/text()"
                    ).get(),
                    "pl_percent": rowdata.xpath('./text()').getall()[-1]
                } for rowdata in rowsdata
            ]
        }

        yield data

    def get_quantity(self, rowdata):
        asset_type = rowdata.xpath('./span/text()')[0].get().strip()
        if asset_type.upper() == 'Títulos Públicos'.upper():
            return rowdata.xpath('./text()').getall()[2]
        else:
            return rowdata.xpath('./text()').getall()[0]
