"""
Utils Module
"""
import io
import json
import logging
import os
import sys
from pathlib import Path

import pandas
import pyproj
import requests
from pandarallel import pandarallel
from pyproj import Transformer

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logger = logging.getLogger("papernest_logger")


pandarallel.initialize(nb_workers=os.cpu_count())


def csv_to_dataframe(file):
    """
    Transform data file from csv to dataframe
    :param file: file
    :return: dataframe
    """
    network_cov_dataframe = pandas.read_csv(file, header=0, delimiter=";")
    network_cov_dataframe.dropna(subset=["x", "y"], inplace=True)
    network_cov_dataframe.drop_duplicates(inplace=True)
    return network_cov_dataframe


def extract_operators(dataframe):
    """
    Extract Operators from dataframe
    :param dataframe: dataframe
    :return: List of operators
    """
    return dataframe["Operateur"].drop_duplicates().to_list()


def add_city_to_dataframe(dataframe):
    """
    Add cities to each row, based on lambert 93 coord in each row,
     using pyproj to convert coords to lat and long first
    :param dataframe: dataframe
    :return: dataframe with 3 new cols: lat, lon and city
    """
    dataframe["lon"], dataframe["lat"] = dataframe.parallel_apply(
        lambert93_to_lat_long, axis=1, result_type="expand"
    ).T.values
    dataframe = get_cities(dataframe.to_csv())
    dataframe.dropna(inplace=True)

    return dataframe


def extract_cities(dataframe):
    """
    Extract city from dataframe
    :param dataframe: dataframe
    :return: List of cities
    """
    return dataframe["city"].drop_duplicates().to_list()


def get_cities(file):
    """
    Reverse search: retrieve an address from gps coordinates
    :param file: csv file
    :return: dataframe with city inside
    """
    res = requests.post(  # pylint: disable=W3101
        "https://api-adresse.data.gouv.fr/reverse/csv/",
        files={"data": file},
    )
    res.raise_for_status()
    data_file = io.StringIO(res.text)
    dataframe = pandas.read_csv(data_file, header=0, delimiter=",")
    dataframe.rename(columns={"result_city": "city"}, inplace=True)
    # remove unwanted columns
    dataframe = dataframe.loc[:, ~dataframe.columns.str.startswith("result")]
    dataframe = dataframe.iloc[:, 1:]
    return dataframe


def lat_long_to_lambert93(lat, lon):
    """
    Not used for this project for the moment
    New way to transform gps coordinates wsg84 to lambert93
    :param lat: x coord (lat)
    :param lon: y coord (lon)
    :return: lambert93 coords
    """

    proj_gps = {"proj": "longlat", "ellps": "WGS84", "datum": "WGS84", "no_defs": True}
    proj_lambert = {
        "proj": "lcc",
        "lat_2": 44,
        "lat_0": 46.5,
        "lon_0": 3,
        "x_0": 700000,
        "y_0": 6600000,
        "ellps": "GRS80",
        "towgs84": "0, 0, 0, 0, 0, 0, 0",
        "units": "m",
        "no_defs": True,
    }
    transformer = Transformer.from_crs(proj_gps, proj_lambert, always_xy=True)
    lambert_x, lambert_y = transformer.transform(lat, lon)  # pylint: disable=E0633
    return lambert_x, lambert_y


def lambert93_to_lat_long_old(lambert_x, lambert_y):
    """
    Old way to transform lambert93 to gps coordinates wsg84 (deprecated)
    :param lambert_x: x coord (lambert93)
    :param lambert_y: y coord (lambert93)
    :return: lon, lat
    """
    lambert = pyproj.Proj(
        "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"  # pylint: disable=C0301
    )
    wgs84 = pyproj.Proj("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    long, lat = pyproj.transform(  # pylint: disable=E0633
        lambert, wgs84, lambert_x, lambert_y
    )
    return long, lat


def lambert93_to_lat_long(row):
    """
    New way to transform lambert93 to gps coordinates wsg84
    :param lambert_x: x coord (lambert93)
    :param lambert_y: y coord (lambert93)
    :return: lon, lat
    """
    lambert_x, lambert_y = row["x"], row["y"]
    proj_gps = {"proj": "longlat", "ellps": "WGS84", "datum": "WGS84"}
    proj_lambert = {
        "proj": "lcc",
        "lat_2": 44,
        "lat_1": 49,
        "lat_0": 46.5,
        "lon_0": 3,
        "x_0": 700000,
        "y_0": 6600000,
        "ellps": "GRS80",
        "towgs84": "0, 0, 0, 0, 0, 0, 0",
        "units": "m",
    }
    # transformer = Transformer.from_crs("epsg:2154", "epsg:4326")
    transformer = Transformer.from_crs(proj_lambert, proj_gps, proj_lambert)
    long, lat = transformer.transform(lambert_x, lambert_y)  # pylint: disable=E0633
    return long, lat


def find_operator(operator):
    """
    Attempts to match the country of which matches the passed CC
    and/or MCC/MNC. Prints respective MCC-MNC data if match is found.
    :param user_mcc: User's desired Mobile Country Code (MCC)
    :param user_mnc: User's desired Mobile Network Code (MNC)
    :return:
    """
    operator = str(operator)
    user_mcc = operator[:3]
    user_mnc = operator[3:]
    match_found = False
    match = None
    path_json = Path("app/resources/mccmnc.json")
    try:
        with open(path_json, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)

        if user_mcc and user_mnc:
            user_mcc = str(user_mcc)
            user_mnc = str(user_mnc)
            for country in json_data.keys():
                if (
                    user_mcc == json_data[country]["MCC"]
                    and user_mnc == json_data[country]["MNC"]
                ):
                    return json_data[country]["NETWORK"]

        if not match_found:
            raise ValueError(f"No Match Found for op {operator}")
    except (IndexError, KeyError, ValueError) as exc:
        logger.exception(f"Error: The following exception has occurred: {exc}")
        raise exc
    return match
