import os
import logging

import numpy as np
import pandas as pd
from dotenv import load_dotenv



class Calculator:

    SPECIFIC_CATEGOTY_FEATURE = "OUTER_CATEGORY_POTENTIAL"

    THRESHOLD_CATEGOTY_AMOUNT = 10

    REQUIRED_COLUMNS_OF_DB = [
        "staff_pick",
        "spotlight",
        "category_slug",
        "country",
        "usd_pledged",
    ]

    COMMON_CATEGORY_FETURES = [
        "COUNTRY_SCORE",
        "VIDEO_APPEARANCE",
        "STOTLIGHT_PROB",
        "STAFF_PEAK_PROB",
    ]

    PEAK_COUNTRIES_INCREMENT = {
        "HK": 0.1,
        "PL": 0.06,
        "GR": 0.03,
        "JP": 0.01,
    }

    GAME_CATEGORIES_INCREMENT = {
        "games/video games": 0.1,
        "games/playing cards": 0.05,
        "games/puzzles": 0.05,
        "games/mobile games": 0.03,
    }

    MOVIE_CATEGORIES_INCREMENT = {
        "film & video/animation": 0.1,
        "film & video/documentary": 0.05,
        "film & video/science fiction": 0.05,
        "film & video/drama": 0.03,
        "film & video/comedy": 0.03,
        "film & video/music videos": 0.01,
    }

    MUSIC_CATEGORIES_INCREMENT = {
        "music/r&b": 0.1,
        "music/pop": 0.1,
        "music/classical music": -0.1,
        "music/latin": -0.1
    }

    COMICS_CATEGORIES_INCREMENT = {
        "comics/graphic novels": 0.1,
        "comics/comic books": 0.05,
        "comics/webcomics": -0.03,
    }

    SPECIAL_CATEGORIES = {
        "comics": COMICS_CATEGORIES_INCREMENT,
        "games": GAME_CATEGORIES_INCREMENT,
        "movies": MOVIE_CATEGORIES_INCREMENT,
        "music": MUSIC_CATEGORIES_INCREMENT,
    }

    def __init__(
        self,
        db_path="data/kickstarter_preparation.csv",
    ):
        self.df = None
        self.common_category_stats = {}
        self.country_stats = {}

        if os.path.exists(db_path): 
            self.df = pd.read_csv(db_path)
        
        categories = self.df.category_slug.unique()

        self._build_probability_stats(categories)
        countries = self.df.country.unique()
        self._buuild_country_stats(countries)


    def check_df(self, df):
        for col in self.REQUIRED_COLUMNS_OF_DB:
            if col not in df.columns.values:
                return False
        return True


    def _buuild_country_stats(self, countries):
        country_stats = {
            c: self.PEAK_COUNTRIES_INCREMENT.get(c, 0) for c in countries
        }
        self.country_stats.update(country_stats)
        return


    def _build_probability_stats(self, categories):
        for category_name in categories:
            category_statistics = self.get_statistics_by_category(category_name)
            self.common_category_stats[category_name] = category_statistics
        return

    
    def get_parent_category(self, category):
        if "/" in category:
            return category.split("/")[0]
        return category

        

    def get_statistics_by_category(self, category_name):
        stats = {}

        data_category = self.df[self.df.category_slug == category_name]
        if data_category.shape[0] < self.THRESHOLD_CATEGOTY_AMOUNT:
            parent_category =  self.get_parent_category(category_name)
            data_category = self.df[self.df.category_slug == parent_category]

        avg_category_spotlight = data_category.spotlight.mean()
        avg_category_staff_peak = data_category.staff_pick.mean()
        avg_category_fundings = data_category.usd_pledged.mean()

        stats["prob_spotlight"] = avg_category_spotlight
        stats["prob_staff_peak"] = avg_category_staff_peak
        stats["avg_fundings"] = avg_category_fundings
        return stats


    def get_success_chance(self, record, params):
        category = record["category_slug"]
        avg_funds = self.common_category_stats[category]["avg_fundings"]
        k = 1 + np.mean(np.array(list(params.values())))

        if avg_funds * k > 1.5 * record["goal"]: return True
        return False


    def unique_category_features(self, record):
        category_name = record["category_slug"]
        head_category = self.get_parent_category(category_name)
        category_features = {self.SPECIFIC_CATEGOTY_FEATURE: 0}

        if head_category in self.SPECIAL_CATEGORIES.keys() and category_name in self.SPECIAL_CATEGORIES[head_category].keys():
            category_features[self.SPECIFIC_CATEGOTY_FEATURE] = self.SPECIAL_CATEGORIES[head_category][category_name]
        return category_features


    def common_category_features(self, record):
        features = {
            x: 0 for x in self.COMMON_CATEGORY_FETURES
        }

        features["COUNTRY_SCORE"] = self.country_stats.get(record["country"], 0)
        features["VIDEO_APPEARANCE"] = int(record["is_video"]) / 10

        category = record["category_slug"]
        features["STOTLIGHT_PROB"] = self.common_category_stats[category]["prob_spotlight"]
        features["STAFF_PEAK_PROB"] = self.common_category_stats[category]["prob_staff_peak"]

        return features


    def process_object(self, record):
        common_features = self.common_category_features(record)
        category_specific_features = self.unique_category_features(record)
        params = {}
        params.update(common_features)
        params.update(category_specific_features)
        params["is_success"] = self.get_success_chance(record, params)
        return params


objects = [
    {
        "country": "HK",
        "is_video": True,
        "category_slug": "comics/graphic novels",
        "goal": 1234,
    },
    {
        "country": "RU",
        "is_video": False,
        "category_slug": "games",
        "goal": 42,
    },
    {
        "country": "JP",
        "is_video": True,
        "category_slug": "games/mobile games",
        "goal": 12345678,
    },
    {
        "country": "UK",
        "is_video": False,
        "category_slug": "film & video/music videos",
        "goal": 1,
    }
]


load_dotenv(".env")

FORMAT = '%(asctime)s  %(message)s'
is_logging_mode = os.getenv('LOGGING') == "True"

default_logger_level = logging.FATAL
if is_logging_mode:
    default_logger_level = logging.INFO

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='logs/calculator.log',
    level=default_logger_level,
    format=FORMAT
)


calc = Calculator()
for obj in objects:
    resp = calc.process_object(obj)
    logger.info(resp)
