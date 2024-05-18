import json
import random
from pathlib import Path

import lxml
import scrapy
from lxml import etree
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ["m.imdb.com"]
    movie_list = []

    def start_requests(self):
        urls = ["https://m.imdb.com/list/ls055386972/"]
        random_user_agent = random.choice(settings.get("USER_AGENT_LIST"))
        for url in urls:
            request = scrapy.Request(url=url, callback=self.parse)
            request.headers["User-Agent"] = random_user_agent
            yield request

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"imdb-{page}.html"
        Path(filename).write_bytes(response.body)

        self.log(f"Saved file {filename}")

        response_text = response.text
        hxs = lxml.html.document_fromstring(response_text)
        list_items_container = hxs.xpath(
            '//div[contains(@class, "list_items_container")]/div[contains(@class, "row")]//div[contains(@class, "media")]/a/@href'
        )
        if list_items_container:
            for url in list_items_container:
                url = f"https://m.imdb.com{url}"
                request = scrapy.Request(url=url, callback=self.get_url_data)
                random_user_agent = random.choice(settings.get("USER_AGENT_LIST"))
                request.headers["User-Agent"] = random_user_agent
                yield request
            return

        list_page_mc_list_content = hxs.xpath(
            '//div[contains(@data-testid, "list-page-mc-list-content")]/ul/li//div[contains(@class, "ipc-poster")]//a/@href'
        )
        if list_page_mc_list_content:
            for url in list_page_mc_list_content:
                url = f"https://m.imdb.com{url}"
                request = scrapy.Request(url=url, callback=self.get_url_data)
                random_user_agent = random.choice(settings.get("USER_AGENT_LIST"))
                request.headers["User-Agent"] = random_user_agent
                yield request

    def get_url_data(self, response):
        response_text = response.text
        hxs = lxml.html.document_fromstring(response_text)

        movie_name = hxs.xpath(
            '//div[contains(@class, "ipc-page-content-container")]//div[contains(@class, "sc-92625f35-3")]//span[contains(@class, "hero__primary-text")]/text()'
        )

        movie_year = hxs.xpath(
            '//div[contains(@class, "ipc-page-content-container")]//div[contains(@class, "sc-92625f35-3")]//ul/li/a/text()'
        )
        movie_director = hxs.xpath(
            '//section[contains(@class, "sc-b7c53eda-4")]//div[contains(@class, "sc-b7c53eda-3")]/div/ul/li/div'
        )

        for index, movie in enumerate(movie_director):
            temp_list = []
            star = False
            director = False
            if index == 1:
                continue
            if index == 2:
                star = True
            if index == 0:
                director = True

            movie = etree.tostring(movie, encoding="UTF-8", pretty_print=True)
            # Find all occurrences of '<a' in the HTML content
            start_indices = [
                pos
                for pos, char in enumerate(movie)
                if char == ord("<") and movie[pos + 1 : pos + 3] == b"a "
            ]

            # Iterate over the start indices of '<a' tags
            for start_index in start_indices:
                # Find the corresponding end index of '</a>'
                end_index = movie.find(b"</a>", start_index)
                if end_index != -1:
                    # Extract the content between '<a>' and '</a>'
                    a_tag_content = movie[start_index:end_index].decode("utf-8")
                    # Find the start index of the closing '>' in '<a>'
                    inner_start_index = a_tag_content.find(">") + 1
                    # Extract the text content after the '>'
                    text_content = a_tag_content[inner_start_index:].strip()
                    # Decode Unicode escape sequences
                    text_content = text_content.encode("utf-8").decode("unicode_escape")
                    temp_list.append(text_content)
            if star:
                star_list = temp_list
            if director:
                director_list = temp_list
        self.movie_list.append(
            {
                "movie_year": movie_year[0],
                "movie_name": movie_name,
                "star_list": star_list,
                "director_list": director_list,
            }
        )

    def close(self, reason):
        # Serialize movie_list to JSON file
        output_file = "movie_data.json"
        with open(output_file, "w") as json_file:
            json.dump(self.movie_list, json_file, indent=4)
        self.logger.info(f"Saved {len(self.movie_list)} movies to {output_file}")
