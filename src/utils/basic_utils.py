"""
This module provides utility functions for handling files and directories.
It includes functions for reading YAML files, CSV files, creating directories
and writing to CSV files. The functions are designed to handle exceptions and
log relevant information for debugging purposes.
"""

import json
import zipfile
from os import listdir, makedirs
from os.path import dirname, normpath
from typing import Any

import joblib
import yaml
from box import Box
from tabulate import tabulate

from src.exception import CustomException
from src.logger import logger


def read_yaml(yaml_path: str) -> Box:
    """
    This function reads a YAML file from the provided path and returns
    its content as a Box object.

    Args:
        yaml_path (str): The path to the YAML file to be read.

    Raises:
        CustomException: If there is any error while reading the file or
        loading its content, a CustomException is raised with the original
        exception as its argument.

    Returns:
        Box: The content of the YAML file, loaded into a Box object for
        easy access and manipulation.
    """
    try:
        yaml_path = normpath(yaml_path)
        with open(yaml_path, encoding="utf-8") as yf:
            content = Box(yaml.safe_load(yf))
            logger.info("yaml file: %s loaded successfully", yaml_path)
            return content
    except Exception as e:
        logger.error(CustomException(e))
        raise CustomException(e) from e


def create_directories(dir_paths: list, verbose=True) -> None:
    """
    This function creates directories at the specified paths.

    Args:
        dir_paths (list): A list of directory paths where directories need
        to be created.
        verbose (bool, optional): If set to True, the function will log
        a message for each directory it creates. Defaults to True.
    """
    for path in dir_paths:
        makedirs(normpath(path), exist_ok=True)
        if verbose:
            logger.info("created directory at: %s", path)


def save_as_joblib(file_path: str, serialized_object: Any) -> None:
    """
    Save a serialized object using joblib.

    Args:
        file_path (str): The file path where the serialized object will be saved.
        serialized_object (Any): The object to be serialized and saved.

    Raises:
        CustomException: If there is an error during the saving process.
    """
    save_path = normpath(file_path)
    makedirs(dirname(save_path), exist_ok=True)
    try:
        joblib.dump(serialized_object, save_path)
        logger.info("object saved at: %s", save_path)
    except Exception as e:
        logger.error(CustomException(e))
        raise CustomException(e) from e


def load_joblib(file_path: str) -> joblib:
    """
    This function loads a joblib file from a specified file path.

    Args:
        file_path (str): The path to the joblib file to be loaded.

    Raises:
        CustomException: If there is an error in loading the joblib file,
        a custom exception is raised with the error message.

    Returns:
        joblib: The loaded joblib object
    """
    saved_path = normpath(file_path)
    try:
        joblib_object = joblib.load(saved_path)
        logger.info("object loaded from: %s", saved_path)
        return joblib_object
    except Exception as e:
        logger.error(CustomException(e))
        raise CustomException(e) from e


def save_as_json(file_path: str, data: dict) -> None:
    """
    This function saves a dictionary as a JSON file at the specified file path.

    Args:
        file_path (str): The path where the JSON file will be saved. If the directories
        in the path do not exist, they will be created.
        data (dict): The dictionary that will be saved as a JSON file.

    Raises:
        CustomException: If there is an error during the file writing process,
        a CustomException will be raised with the original exception as its argument.
    """
    save_path = normpath(file_path)
    makedirs(dirname(save_path), exist_ok=True)
    try:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        logger.info("json file saved at: %s", save_path)
    except Exception as e:
        logger.error(CustomException(e))
        raise CustomException(e) from e


def dict_to_table(input_dict: dict, column_headers: list) -> str:
    """
    Convert a dictionary into a tabulated string.

    Args:
        input_dict (dict): The input dictionary to be converted into a table.
        column_headers (list): List of column headers for the table.

    Returns:
        str: A tabulated representation of the dictionary as a string.
    """

    table_vw = tabulate(
        input_dict.items(), headers=column_headers, tablefmt="pretty", stralign="left"
    )

    return table_vw


def unzip_file(zipfile_path: str, unzip_dir: str) -> str:
    """
    Unzips a file to a specified directory.

    Args:
        zipfile_path (str): The path to the zip file.
        unzip_dir (str): The directory where the files will be extracted.

    Returns:
        str: A list of the names of the extracted files.
    """
    zipfile_path = normpath(zipfile_path)
    unzip_dir = normpath(unzip_dir)
    try:
        with zipfile.ZipFile(zipfile_path, "r") as zf:
            zf.extractall(path=unzip_dir)
        unzipped_files = listdir(unzip_dir)
        return unzipped_files
    except Exception as e:
        logger.error(CustomException(e))
        raise CustomException(e) from e
