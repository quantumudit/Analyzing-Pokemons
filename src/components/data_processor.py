"""
summary
"""

import sqlite3
from os.path import dirname, normpath

import pandas as pd

from src.constants import CONFIGS
from src.exception import CustomException
from src.logger import logger
from src.utils.basic_utils import create_directories, read_yaml


class DataProcessor:
    """_summary_"""

    def __init__(self):
        # Read the configuration file
        self.configs = read_yaml(CONFIGS).data_processor

        # Input file path
        self.scraped_data_path = normpath(self.configs.scraped_data_path)

        # Output file path
        self.database_path = normpath(self.configs.database_path)

    @staticmethod
    def transform_data(df: pd.DataFrame) -> tuple[pd.DataFrame]:
        """_summary_

        Args:
            df (pd.DataFrame): _description_

        Returns:
            tuple[pd.DataFrame]: _description_
        """
        # Create custom range index
        custom_index_col = pd.RangeIndex(
            start=1000, stop=1000 + len(df), step=1, name="pokemon_id"
        )
        # Add custom index as dataframe index & Modify it to have a "P" prefix
        df.index = custom_index_col
        df.index = "P" + df.index.astype("string")

        # Reset index to make "pokemon_id" as row identifier column
        df = df.reset_index()

        # Split the "types" column into rows
        df["types"] = df["types"].str.split(",")
        df = df.explode("types").reset_index(drop=True)

        # Drop "total_power" column
        df = df.drop(columns=["total_power"])

        # Unpivot columns
        df = df.melt(
            id_vars=[
                "pokemon_id",
                "rank",
                "name",
                "types",
                "icon_url",
                "details_url",
                "scrape_ts",
            ],
            value_vars=[
                "hit_points",
                "attack",
                "defense",
                "special_attack",
                "special_defense",
                "speed",
            ],
            var_name="metric",
            value_name="value",
        )

        # Create data for "pokemons" table
        pokemons_tbl_cols = ["pokemon_id", "rank", "name", "icon_url", "details_url"]
        pokemons_tbl = df[pokemons_tbl_cols].drop_duplicates().reset_index(drop=True)

        # Create data for "stats" table
        stat_tbl_cols = ["pokemon_id", "types", "metric", "value"]
        stats_tbl = df[stat_tbl_cols].drop_duplicates().reset_index(drop=True)

        return (pokemons_tbl, stats_tbl)

    def load_processed_tables(self) -> None:
        """_summary_"""
        try:
            # create save directory if not exists
            create_directories([dirname(self.database_path)])

            # Read the scraped data
            logger.info("Loading the scraped data")
            scraped_df = pd.read_csv(self.scraped_data_path)
            logger.info("Scraped data loaded successfully")

            # Transform the scraped data and receive individual tables
            logger.info("Started data transformation")
            pokemons_tbl, stats_tbl = self.transform_data(scraped_df)
            logger.info("Data transformation completed successfully")

            # Create s SQLlite connection
            logger.info("Building connection with SQLite database")
            conn = sqlite3.connect(self.database_path)
            logger.info("SQLite connection build successfully")

            # Load/Replace tables in the database
            logger.info("Loading tables into the database")
            pokemons_tbl.to_sql("pokemons", conn, index=False, if_exists="replace")
            stats_tbl.to_sql(
                "stats", conn, index=True, if_exists="replace", index_label="row_id"
            )
            logger.info("All tables loaded to the database successfully")

            # Close the connection
            conn.close()
            logger.info("SQLite connection closed successfully")
        except Exception as e:
            logger.error(CustomException(e))
            raise CustomException(e) from e
