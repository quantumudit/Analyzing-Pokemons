"""
This module contains the paths to the configuration and schema files. The paths are
normalized to ensure they are in the correct format for the current operating system.

The configuration file is expected to be in YAML format and contains various settings
for the application. The schema file is also expected to be in YAML format and defines
the structure of the data the application works with.
"""

from dataclasses import dataclass
from os.path import normpath

CONFIGS = normpath("conf/configs.yaml")


@dataclass(frozen=True)
class PokemonInfo:
    """
    A dataclass for storing product information.
    Attributes:
        title (str): The title of the product.
    """

    title: str
    price: str
    in_stocks: str
    sku: str
    category: str
    description: str
    product_image_link: str
    additional_info: dict
    product_link: str
    scrape_ts: str
