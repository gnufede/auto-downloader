import logging
import argparse
import requests
import pickle
from transmission import Transmission
from configparser import ConfigParser

from sources.kat_page import KatPage


def main():
    parser = argparse.ArgumentParser(description='Auto download stuff.')
    parser.add_argument('--log', dest='loglevel', help='log level')

    args = parser.parse_args()
    # assuming loglevel is bound to the string value obtained from the
    # command line argument. Convert to upper case to allow the user to
    # specify --log=DEBUG or --log=debug
    loglevel = args.loglevel or 'WARNING'
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=numeric_level)

    cfg = ConfigParser(interpolation=None)
    cfg.read('config.ini')

    try:
        already_downloaded_items = pickle.load(
            open(cfg['Main']['already_downloaded'], 'rb')
        )
    except OSError:
        already_downloaded_items = []
        logging.error('Creating a new list of items')

    transmission_client = Transmission(
        host=cfg['Transmission']['host'],
        username=cfg['Transmission']['username'],
        password=cfg['Transmission']['password']
    )

    for search_name, search_url in cfg.items('Urls'):
        logging.info('Getting: %s' % search_name)
        current_search = None
        if KatPage.is_this(search_url):
            session = requests.Session()
            current_search = KatPage(search_url, requests_session=session)

        if current_search:
            logging.info('Getting: %s results' % search_name)
            for torrent in current_search.results:
                if torrent.decide(already_downloaded_items, cfg=cfg):
                    logging.warning('Adding: %s' % torrent.properties['name'])
                    transmission_client(
                        'torrent-add',
                        filename=torrent.properties['magnet_link']
                    )
                    already_downloaded_items.append(
                        torrent.properties['id']
                    )
    pickle.dump(
        already_downloaded_items,
        open(cfg['Main']['already_downloaded'], 'wb')
        )

if __name__ == "__main__":
    main()
