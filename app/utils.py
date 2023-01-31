import io
import json
import logging
import os
import sys
from pathlib import Path

import pandas
import pyproj
import requests
from pyproj import Transformer

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logger = logging.getLogger("papernest_logger")

from pandarallel import pandarallel

pandarallel.initialize(nb_workers=os.cpu_count())


def csv_to_dataframe(file):
    """Transform data file from csv to dataframe"""
    network_cov_df = pandas.read_csv(file, header=0, delimiter=";")
    network_cov_df.dropna(subset=["x", "y"], inplace=True)
    network_cov_df.drop_duplicates(inplace=True)
    return network_cov_df


def extract_operators(df):
    return df["Operateur"].drop_duplicates().to_list()


def extract_networks(df):
    return df.columns[-3:].to_list()


def add_city_to_df(df):
    df["lon"], df["lat"] = df.parallel_apply(
        lambert93_to_lat_long, axis=1, result_type="expand"
    ).T.values
    df = get_cities(df.to_csv())
    df.dropna(inplace=True)

    return df


def extract_cities(df):
    return df["city"].drop_duplicates().to_list()


# Reverse search: retrieve an address from gps coordinates
def get_cities(file):
    res = requests.post(
        "https://api-adresse.data.gouv.fr/reverse/csv/", files={"data": file}
    )
    res.raise_for_status()
    data_file = io.StringIO(res.text)
    df = pandas.read_csv(data_file, header=0, delimiter=",")
    df.rename(columns={"result_city": "city"}, inplace=True)
    # remove unwanted columns
    df = df.loc[:, ~df.columns.str.startswith("result")]
    df = df.iloc[:, 1:]
    return df


def lat_long_to_lambert93(x, y):
    """New way to transform gps coordinates wsg84 to lambert93"""

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
    lambert_x, lambert_y = transformer.transform(x, y)
    return lambert_x, lambert_y


def lambert93_to_lat_long_old(x, y):
    """Old way to transform lambert93 to gps coordinates wsg84 (deprecated)"""
    lambert = pyproj.Proj(
        "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
    )
    wgs84 = pyproj.Proj("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    long, lat = pyproj.transform(lambert, wgs84, x, y)
    return long, lat


def lambert93_to_lat_long(row):
    x, y = row["x"], row["y"]
    """New way to transform lambert93 to gps coordinates wsg84"""
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
    long, lat = transformer.transform(x, y)
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
        with open(path_json, "r") as json_file:
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
    except (IndexError, KeyError, ValueError) as e:
        logger.exception(f"Error: The following exception has occurred: {e}")
        raise ValueError
    return match
