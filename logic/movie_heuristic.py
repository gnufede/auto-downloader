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
        languages = movie_properties.get('languages', None)
        subtitles = movie_properties.get('subtitles', None)

        if cfg['IMDB'] and cfg['IMDB']['rating_minimum']:
            if rating < float(cfg['IMDB']['rating_minimum']):
                logging.warning(
                    'Not adding %s because its rating is %0.1f' %
                    (name, rating)
                )
                return False

        if cfg['IMDB'] and cfg['IMDB']['votes_minimum']:
            if votes < int(cfg['IMDB']['votes_minimum']):
                logging.warning(
                    'Not adding %s because its votes are %d' %
                    (name, votes)
                )
                return False

        if cfg['Disliked Genres']:
            for genre in genres:
                if genre in [
                    g.capitalize() for g in cfg['Disliked Genres']
                ]:
                    logging.warning(
                        'Not adding %s because it\'s a %s movie' %
                        (name, genre)
                    )
                    return False

        if cfg['Accepted Qualities']:
            if quality not in [
                q.capitalize() for q in cfg['Accepted Qualities']
            ]:
                logging.warning(
                    'Not adding %s because its quality is %s' %
                    (name, quality)
                )
                return False

        if cfg['Accepted Languages']:
            if not len(
                set(languages) &
                set(l.capitalize() for l in cfg['Accepted Languages'])
            ):
                logging.warning(
                    'Not adding %s because its languages are %s' %
                    (name, languages)
                )
                return False

        if cfg['Accepted Subtitles'] and subtitles:
            if not len(
                set(subtitles) &
                set(s.capitalize() for s in cfg['Accepted Subtitles'])
            ):
                logging.warning(
                    'Not adding %s because its subtitles are %s' %
                    (name, subtitles)
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
