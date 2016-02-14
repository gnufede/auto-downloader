import logging
from lxml import html

from logic.movie_heuristic import MovieHeuristic


class KatPage(object):
    domain = 'https://kat.cr'

    @classmethod
    def is_this(cls, url):
        return url.startswith(cls.domain)

    def __init__(self, url, *args, **kwargs):
        self.url = url
        self.requests_session = kwargs['requests_session']
        self.url_type = None
        logging.debug('downloading html...')
        self.original_html = self.requests_session.get(self.url)
        logging.debug('html downloaded')
        self.parsed_html = self.parse_html()
        if self.url.startswith('%s/usearch/' % self.domain):
            self.init_search_page()
        elif self.url.endswith('.html'):
            self.init_torrent_page(**kwargs)
        else:
            logging.warning("url: %s is unknown page" % self.url)

    def init_search_page(self):
        logging.debug("url: %s is search" % self.url)
        self.url_type = 'search'
        self.results = self.get_result_pages()

    def init_torrent_page(self, **kwargs):
        logging.debug("url: %s is page" % self.url)
        self.results = None
        self.url_type = 'torrent'
        self.description = self.get_meta_description()
        self.category = None
        if 'Movies' in self.description:
            self.init_movie_page(**kwargs)
        elif 'TV' in self.description:
            self.init_tv_page()
        else:
            logging.warning("url: %s is unknown category" % self.url)
        self.properties = self.extract_properties()

    def init_movie_page(self, **kwargs):
        logging.debug("url: %s is movie" % self.url)
        self.category = 'Movie'
        if 'heuristic_config' in kwargs:
            self.heuristic = MovieHeuristic(
                config=kwargs['heuristic_config']
            )
        else:
            self.heuristic = MovieHeuristic()

    def init_tv_page(self, **kwargs):
        logging.debug("url: %s is tv" % self.url)
        self.category = 'TV'

    def parse_html(self):
        parsed_html = html.fromstring(self.original_html.content)
        parsed_html.make_links_absolute(self.domain)
        return parsed_html

    def decide(self, already_downloaded, **kwargs):
        try:
            return self.heuristic.decide(
                self.properties,
                already_downloaded,
                **kwargs
            )
        except AttributeError:
            logging.error("No heuristic set")
            return False

    def get_meta_description(self):
        return self.parsed_html.xpath(
            '/html/head/meta[@name="description"]/@content'
        )[0]

    def get_result_pages(self):
        return [
            KatPage(link.get('href'), requests_session=self.requests_session)
            for link in
            self.parsed_html.xpath('//*[contains(@class, "cellMainLink")]')
        ]

    def extract_properties(self):
        info_block = self.parsed_html.xpath(
            '//ul[contains(@class, "botmarg0")]'
        )

        if not info_block:
            return
        else:
            info_block = info_block[0]

        properties = {
            'magnet_link':
            self.parsed_html.xpath(
                '//*[contains(@title, "Magnet link")]'
            )[0].get('href')
        }
        for li in info_block.iterchildren():
            if li.getchildren()[0].text == 'Detected quality:':
                properties['quality'] = li.getchildren()[1].text

            elif li.getchildren()[0].text == 'Movie:':
                properties['movie'] = li.getchildren()[1].getchildren()[0].text

            elif li.getchildren()[0].text == 'IMDb link:':
                properties['imdb_link'] = li.getchildren()[1].text

            elif li.getchildren()[0].text == 'IMDb rating:':
                rating_str = li.text_content()
                properties['rating'] = float(
                    rating_str[
                        rating_str.index(':') + 2:
                        rating_str.index('(') - 1
                    ]
                )
                properties['votes'] = int(
                    rating_str[
                        rating_str.index('(') + 1:
                        rating_str.index(' votes')
                    ].replace(',', '')
                )

            elif li.getchildren()[0].text == 'Genre:':
                properties['genres'] = [
                    li.getchildren()[1].text_content(),
                ]

            elif li.getchildren()[0].text == 'Genres:':
                properties['genres'] = [
                    genre.text_content() for genre in li.getchildren()[1:]
                ]

        if self.category == 'Movie':
            properties['name'] = properties['movie']
            properties['id'] = properties['imdb_link']

        return properties
