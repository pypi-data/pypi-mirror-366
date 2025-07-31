from plexflow.core.context.partial_context import PartialContext
from datetime import datetime as dt
from plexflow.core.metadata.auto.auto_providers.auto.show import AutoShow
from plexflow.core.metadata.auto.auto_providers.tmdb.show import AutoTmdbShow
from plexflow.core.metadata.auto.auto_providers.tvdb.show import AutoTvdbShow
from plexflow.core.metadata.auto.auto_providers.imdb.show import AutoImdbShow
from plexflow.core.metadata.auto.auto_providers.plex.show import AutoPlexShow

class Show(PartialContext):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def sources(self) -> list:
        keys = self.get_keys("show/*")
        # extract the source from the key
        return [key.split("/")[-1] for key in keys]

    def from_source(self, source: str) -> AutoShow:
        return self.get(f"show/{source}")

    @property
    def title(self) -> str:
        for source in self.sources:
            details = self.from_source(source)
            if details and details.title:
                return details.title
    
    @property
    def year(self) -> int:
        for source in self.sources:
            details = self.from_source(source)
            if details and details.year:
                return details.year
    
    @property
    def release_date(self) -> dt:
        for source in self.sources:
            details = self.from_source(source)
            if details and details.release_date:
                return details.release_date
    
    @property
    def rank(self) -> int:
        return self.plex.rank
    
    @property
    def released(self) -> bool:
        dates = []
        for source in self.sources:
            details = self.from_source(source)
            if details and details.release_date:
                dates.append(details.release_date)
        
        sorted_dates = sorted(dates)
        now = dt.now()
        return all([date < now for date in sorted_dates])
    
    @property
    def runtime(self) -> int:
        for source in self.sources:
            details = self.from_source(source)
            if details and details.runtime:
                return details.runtime

    @property
    def titles(self) -> set:
        titles = set()
        for source in self.sources:
            details = self.from_source(source)
            if details and details.title:
                titles.add(details.title)
                titles.update(details.titles)
        return titles

    @property
    def summary(self) -> str:
        for source in self.sources:
            details = self.from_source(source)
            if details and details.summary:
                return details.summary
    
    @property
    def language(self) -> str:
        for source in self.sources:
            details = self.from_source(source)
            if details and details.language:
                return details.language

    @property
    def plex(self) -> AutoPlexShow:
        return self.from_source("plex")
        
    @property
    def tmdb(self) -> AutoTmdbShow:
        return self.from_source("tmdb")
        
    @property
    def imdb(self) -> AutoImdbShow:
        return self.from_source("imdb")
        
    @property
    def tvdb(self) -> AutoTvdbShow:
        return self.from_source("tvdb")
    
    def update(self, movie: AutoShow):
        self.set(f"show/{movie.source}", movie)
