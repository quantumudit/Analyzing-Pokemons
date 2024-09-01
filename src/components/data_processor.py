"""
Module for processing and transforming Pokémon data.

This module contains the DataProcessor class, which is responsible for reading
configuration settings, loading scraped Pokémon data, transforming it into
structured tables, and saving the processed data into CSV files.

Classes:
    DataProcessor: A class to process and transform Pokémon data from a scraped dataset.
"""

from os.path import dirname, normpath

import pandas as pd

from src.constants import CONFIGS
from src.exception import CustomException
from src.logger import logger
from src.utils.basic_utils import create_directories, read_yaml


class DataProcessor:
    """
    A class to process and transform Pokémon data from a scraped dataset.

    This class reads configuration settings, loads scraped Pokémon data,
    transforms it into structured tables, and saves the processed data
    into CSV files.

    Methods:
        transform_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
            Transforms the input DataFrame into "pokemons" and "stats" tables.

        load_processed_tables() -> None:
            Loads and processes scraped data, then saves the processed
            tables to CSV files.
    """

    def __init__(self):
        # Read the configuration file
        self.configs = read_yaml(CONFIGS).data_processor

        # Input file path
        self.scraped_data_path = normpath(self.configs.scraped_data_path)

        # Output file path
        self.processed_data_path = self.configs.processed_data_path

    @staticmethod
    def transform_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms the input DataFrame to generate transformed and clean dataset.

        Args:
            df (pd.DataFrame): Input DataFrame containing Pokémon data.

        Returns:
            pd.DataFrame: Processed DataFrame.
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
        logger.info("Added custom index column")

        # Split the "types" column into rows
        df["types"] = df["types"].str.split(",")
        df = df.explode("types").reset_index(drop=True)
        logger.info("Split the pokemon types column into rows")

        # Strip any leading and trailing whitespace from "types" Column
        df["types"] = df["types"].str.strip()
        logger.info("Stripped any leading and trailing whitespace from 'types' column")

        # Creating custom columns
        df["Attack"] = df["attack"].astype("int") + df["special_attack"].astype("int")
        df["Defense"] = df["defense"].astype("int") + df["special_defense"].astype(
            "int"
        )
        df["Data As On"] = pd.to_datetime(df["scrape_ts"]).max()
        logger.info("Created required custom columns")

        # Drop unnecessary column
        df = df.drop(
            columns=[
                "attack",
                "defense",
                "special_attack",
                "special_defense",
                "total_power",
                "scrape_ts",
            ]
        )
        logger.info("Dropped unnecessary column")

        # Renaming columns
        col_names = {
            "pokemon_id": "PokeID",
            "rank": "Rank",
            "name": "Pokemon",
            "types": "Type",
            "hit_points": "HP",
            "speed": "Speed",
            "icon_url": "Icon",
            "details_url": "Details Link",
        }

        df = df.rename(columns=col_names)
        logger.info("Renamed the columns")

        # Unpivot columns
        df = df.melt(
            id_vars=[
                "PokeID",
                "Rank",
                "Pokemon",
                "Type",
                "Icon",
                "Details Link",
                "Data As On",
            ],
            value_vars=[
                "HP",
                "Attack",
                "Defense",
                "Speed",
            ],
            var_name="Metric",
            value_name="Values",
        )
        logger.info("Unpivot numeric columns")

        # Fix the datatypes of columns
        df["Values"] = df["Values"].astype(int)
        df["Rank"] = df["Rank"].astype(int)

        for col in df.columns:
            if col not in ["Rank", "Values", "Data As On"]:
                df[col] = df[col].astype(str)
        logger.info("Assigned proper datatype to columns")

        # Create data for "pokemons" table
        pokemons_tbl_cols = [
            "PokeID",
            "Rank",
            "Pokemon",
            "Type",
            "Metric",
            "Values",
            "Icon",
            "Details Link",
            "Data As On",
        ]
        pokemons_tbl = df[pokemons_tbl_cols].drop_duplicates().reset_index(drop=True)
        logger.info("Rearranged columns in Pokémons table")

        return pokemons_tbl

    def load_processed_tables(self) -> None:
        """
        Loads and processes scraped data, then saves the processed tables to CSV files.

        Raises:
            CustomException: If any error occurs during the process, a CustomException
            is raised with the original exception.
        """
        try:
            # create save directory if not exists
            create_directories([dirname(self.processed_data_path)])

            # Read the scraped data
            logger.info("Loading the scraped data")
            scraped_df = pd.read_csv(self.scraped_data_path)
            logger.info("Scraped data loaded successfully")

            # Transform the scraped data and receive individual tables
            logger.info("Started data transformation")
            pokemons_tbl = self.transform_data(scraped_df)
            logger.info("Data transformation completed successfully")

            # Load/Replace tables in the CSV files
            pokemons_tbl.to_csv(self.processed_data_path, index=False)
            logger.info("Pokémons data exported successfully")
        except Exception as e:
            logger.error(CustomException(e))
            raise CustomException(e) from e
