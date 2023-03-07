import time
from pathlib import Path

from etl_utils.pipelines import (
    FilmETLPipeline,
    GenreETLPipeline,
    PersonETLPipeline,
)


def main() -> None:
    states_dir = Path('states').resolve()
    states_dir.mkdir(parents=True, exist_ok=True)
    pipelines = {
        'person_pipeline': PersonETLPipeline(redis_key='person_etl'),
        'genre_pipeline': GenreETLPipeline(redis_key='genre_etl'),
        'filmwork_pipeline': FilmETLPipeline(
            redis_key='filmwork_etl', table_name='film_work'
        ),
        'filmwork_by_person_pipeline': FilmETLPipeline(
            redis_key='filmwork_by_person_etl',
            table_name='person',
            enrich=True,
        ),
        'filmwork_by_genre_pipeline': FilmETLPipeline(
            redis_key='filmwork_by_genre_etl', table_name='genre', enrich=True
        ),
    }
    for _, pipeline in pipelines.items():
        pipeline.run()
        time.sleep(3)


if __name__ == '__main__':
    main()
