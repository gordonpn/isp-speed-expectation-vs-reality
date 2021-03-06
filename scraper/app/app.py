import datetime
import logging
import os
import time
from logging.config import fileConfig

import schedule
import speedtest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from speedtest import SpeedtestBestServerFailure

from .healthcheck.healthcheck import HealthCheck, Status

logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("speedtest_scraper")


class SpeedtestScraper:
    def __init__(self):
        self.db_name = os.getenv("MONGO_INITDB_DATABASE")
        self.db_username = os.getenv("MONGO_NON_ROOT_USERNAME")
        self.db_password = os.getenv("MONGO_NON_ROOT_PASSWORD")
        self.db_collection = os.getenv("MONGO_COLLECTION")

    def run(self):
        logger.debug("Setting schedule")
        if "DEV_RUN" in os.environ:
            schedule.every(1).minutes.do(self.job)
        else:
            schedule.every(10).to(20).minutes.do(self.job)

        logger.debug("Job pending")
        while True:
            schedule.run_pending()
            time.sleep(5 * 60)

    def job(self):
        try:
            logger.debug("Starting up job")
            HealthCheck.ping_status(Status.START)
            speed_data: float = self.scrape()
            self.insert_to_db(speed_data)
            HealthCheck.ping_status(Status.SUCCESS)
            logger.debug("Job completed")
        except SpeedtestBestServerFailure as e:
            logger.error(str(e))
        except Exception as e:
            HealthCheck.ping_status(Status.FAIL)
            logger.error(str(e))
            raise Exception

    def scrape(self) -> float:
        logger.debug("Starting speed test")
        current_test = speedtest.Speedtest()
        current_test.get_servers()
        current_test.get_best_server()
        logger.info("Speed test in progress...")
        current_test.download()
        results_dict = current_test.results.dict()
        raw_speed = results_dict.get("download")
        instant_speed: float = round((raw_speed / 8000000), 2)
        logger.debug(f"Download speed test result is {instant_speed} MB/s")
        return instant_speed

    def connect_to_db(self) -> Collection:
        logger.debug("Making connection to mongodb")
        host = "mongodb"
        uri: str = f"mongodb://{self.db_username}:{self.db_password}@{host}:27017/{self.db_name}"
        connection: MongoClient = MongoClient(uri)
        db: Database = connection[self.db_name]
        return db.collection[self.db_collection]

    def insert_to_db(self, data: float) -> None:
        logger.debug("Inserting into collection")
        collection: Collection = self.connect_to_db()
        recorded_time = datetime.datetime.utcnow()
        logger.debug(f"{collection=} {recorded_time=}, {data=}")
        result = collection.insert_one(document={"time": recorded_time, "speed": data})
        logger.debug(f"Insertion ID: {result.inserted_id}")


def run():
    speedtest_scraper = SpeedtestScraper()
    speedtest_scraper.run()
