import os
from pathlib import Path

import scrapy


class ImdbSpider(scrapy.Spider):
    name = "imdb"

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        url = "https://m.imdb.com/list/ls055386972/?view=detailed"
        yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        try:
            os.remove("output.json")
            print(f"Deleted existing file:")
        except OSError:
            pass

        if response.css("li.ipc-metadata-list-summary-item"):
            for movie in response.css("li.ipc-metadata-list-summary-item"):
                movie_name = str(movie.css("h3.ipc-title__text::text").get())
                movie_name = movie_name.split(".", 1)

                yield {
                    "movie_name": movie_name[-1].strip(),
                    "year": movie.css("span.dli-title-metadata-item::text").get(),
                    "director": movie.css("a.dli-director-item::text").get(),
                    "stars": movie.css("a.dli-cast-item::text").getall(),
                }
        else:
            for movie_item in response.css(
                ".col-xs-12.col-md-6.lister-item.mode-simple"
            ):
                title_element = movie_item.css(".h4:not(.unbold)::text").get()
                print("title_element: ", title_element)
                # Check if title element exists before extracting
                year = str(movie_item.css(".nowrap::text").get())
                year = year.replace("(", "")
                year = year.replace(")", "")

                yield {
                    "movie_name": title_element.strip(),
                    "year": year.strip(),
                    # 'director': movie_item.xpath('//div[@class="credit_summary_item"]/span[@itemprop="director"]/a/span/text()').extract()
                    # 'stars': movie_item.css('.text-muted.text-small a[href*="/name/"]::text').getall()[1:]
                }
