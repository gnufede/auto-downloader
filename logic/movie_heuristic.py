from .generic_heuristic import Heuristic
import logging


class MovieHeuristic(Heuristic):

    def decide(self, movie_properties, already_downloaded, **kwargs):

        cfg = kwargs['cfg']

        name = movie_properties.get('name', 'Unknown Name')
        quality = movie_properties.get('quality', '')
        rating = movie_properties.get('rating', 0)
        votes = movie_properties.get('votes', 0)
        genres = movie_properties.get('genres', ())

        if rating < float(cfg['IMDB']['rating_minimum']):
            logging.warning(
                'Not adding %s because its rating is %0.1f' %
                (name, rating)
            )
            return False
        if votes < int(cfg['IMDB']['votes_minimum']):
            logging.warning(
                'Not adding %s because its votes are %d' %
                (name, votes)
            )
            return False
        for genre in genres:
            if genre.lower() in [disliked for disliked in cfg['Disliked Genres']]:
                logging.warning(
                    'Not adding %s because it\'s a %s movie' %
                    (name, genre)
                )
                return False
        if quality not in [q for q in cfg['Accepted Qualities']]:
            logging.warning(
                'Not adding %s because its quality is %s' %
                (name, quality)
            )
            return False

        generic_heuristic_result = super(MovieHeuristic, self).decide(
            movie_properties,
            already_downloaded,
            **kwargs
        )

        if generic_heuristic_result is False:
            return False

        return True
