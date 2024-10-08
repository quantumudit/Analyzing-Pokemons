"""
This module provides functionality to scrape Pokémon data from a specified URL and
save it to a CSV file.

The module includes the `PokemonScraper` class, which reads configuration settings
from a YAML file, sends an HTTP request to a specified URL to retrieve Pokémon data,
parses the HTML content using BeautifulSoup, and extracts relevant information about
each Pokémon. The extracted data is then saved to a CSV file.

Classes:
    PokemonScraper: A class used to scrape Pokémon data from a specified URL and save
    it to a CSV file.

Functions:
    extract_pokemon_info(): Extracts information about a Pokémon.
    scrape_data(): Scrapes data from a specified URL and saves it to a CSV file.
"""

import time
from dataclasses import asdict
from datetime import datetime
from os.path import dirname, exists, normpath
from urllib.parse import urljoin

import bs4
import requests

from src.constants import CONFIGS, PokemonInfo
from src.exception import CustomException
from src.logger import logger
from src.utils.basic_utils import create_directories, read_yaml, write_to_csv


class PokemonScraper:
    """
    A class used to scrape Pokémon data from a specified URL and save it to a CSV file.

    This class reads configuration settings from a YAML file, sends an HTTP request to
    a specified URL to retrieve Pokémon data, parses the HTML content using
    BeautifulSoup, and extracts relevant information about each Pokémon. The extracted
    data is then saved
    to a CSV file.

    Attributes:
        configs (dict): Configuration settings read from the YAML file.
        root_url (str): The root URL of the website to scrape data from.
        data_url (str): The specific URL containing the Pokémon data.
        user_agent (str): The user-agent string to be used in the HTTP request headers.
        timeout (int): The timeout duration for the HTTP request.
        clear_contents (bool): Flag to clear the existing output file contents or, not
        scraped_data_path (str): The file path where the scraped data will be saved.
        headers (dict): HTTP request headers.

    Methods:
        extract_pokemon_info(pokemon: bs4.element.Tag) -> dict:
            Extracts information about a Pokémon from a BeautifulSoup Tag object.

        scrape_data() -> None:
            Scrapes data from a specified URL and saves it to a CSV file.
    """

    def __init__(self):
        # Read the configuration file
        self.configs = read_yaml(CONFIGS).data_scraper

        # Inputs
        self.root_url = self.configs.root_url
        self.data_url = self.configs.data_url
        self.user_agent = self.configs.user_agent
        self.timeout = self.configs.timeout
        self.clear_contents = self.configs.clear_contents

        # Output file path
        self.scraped_data_path = normpath(self.configs.scraped_data_path)

        # Clear the contents if exists for fresh update & avoid duplication
        if self.clear_contents:
            if exists(self.scraped_data_path):
                with open(self.scraped_data_path, "w", encoding="utf-8") as f:
                    f.truncate()
                logger.info("Cleared existing contents from %s", self.scraped_data_path)

        # Create the headers
        self.headers = {"user-agent": self.user_agent, "accept-language": "en-US"}

    def extract_pokemon_info(self, pokemon: bs4.element.Tag) -> dict:
        """
        Extracts information about a Pokémon from a BeautifulSoup Tag object.

        Args:
            pokemon (bs4.element.Tag): A BeautifulSoup Tag object containing the
            HTML of a Pokémon entry.

        Returns:
            dict: A dictionary with the Pokémon's rank, name, types, stats, icon URL,
            details URL, and scrape timestamp.
        """

        # Get the name of the pokemon (also mega/extra name info, if exists)
        common_name = pokemon.find("a", class_="ent-name").text
        try:
            extra_name = pokemon.find("small", class_="text-muted").text
            name = f"{common_name} ({extra_name})"
        except AttributeError:
            name = common_name

        # Partial details URL path of the pokemon
        partial_details_path = pokemon.find("a", class_="ent-name")["href"]

        # Pokemon type(s) list
        types_list = [type.text for type in pokemon.find_all("a", class_="type-icon")]

        # Power stats of the pokemon
        power_stats = pokemon.find_all("td", class_="cell-num")[2:]

        pokemon_stats = PokemonInfo(
            rank=pokemon.find("span", class_="infocard-cell-data").text,
            name=name,
            types=", ".join(types_list),
            total_power=pokemon.find("td", class_="cell-total").text,
            hit_points=power_stats[0].text,
            attack=power_stats[1].text,
            defense=power_stats[2].text,
            special_attack=power_stats[3].text,
            special_defense=power_stats[4].text,
            speed=power_stats[5].text,
            icon_url=pokemon.find("img", class_="icon-pkmn")["src"],
            details_url=urljoin(self.root_url, partial_details_path),
            scrape_ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        return asdict(pokemon_stats)

    def scrape_data(self) -> None:
        """
        Scrapes data from a specified URL and saves it to a CSV file.

        Raises:
            CustomException: If an error occurs during the scraping process.
        """
        # create save directory if not exists
        create_directories([dirname(self.scraped_data_path)])

        # Get the response from the website
        response = requests.get(
            self.data_url, headers=self.headers, timeout=self.timeout
        )
        try:
            logger.info(
                "Request responded with the status code: %s", response.status_code
            )
            soup = bs4.BeautifulSoup(response.content, "html.parser")
            pokedex_table = soup.find("table", attrs={"id": "pokedex"})
            pokemon_entries = pokedex_table.find("tbody").find_all("tr")
            logger.info("Total entries found in Pokedex: %s", len(pokemon_entries))

            # Scraping start time
            start_time = time.time()

            # Start scraping product in loop
            logger.info("Scraping started")

            # Write scraped info into CSV file
            for idx, pokemon in enumerate(pokemon_entries):
                data = self.extract_pokemon_info(pokemon)
                write_to_csv(self.scraped_data_path, data)
                logger.info("%s pokemons data scraped", idx + 1)

            # Scraping end time
            end_time = time.time()

            # Scraping time interval
            time_diff = round(end_time - start_time)

            # Log time taken for scraping
            logger.info("Time taken for scraping: %s seconds", f"{time_diff:.2f}")
            logger.info("All data scraped")
        except Exception as e:
            logger.error(CustomException(e))
            raise CustomException(e) from e
