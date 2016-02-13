import logging


class Heuristic(object):

    def decide(self, properties, already_downloaded, **kwargs):
        if properties['id'] in already_downloaded:
            logging.warning(
                'Not adding %s because is already downloaded' %
                properties['name']
            )
            return False
