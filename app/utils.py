import pandas
from pyproj import Transformer


def get_original_data_frame():
    """Transform data file from csv to dataframe"""
    original_data_frame = pandas.read_csv('resources/2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv',
                                          header=0,
                                          delimiter=';')

    original_data_frame.dropna(subset=['X', 'Y'], inplace=True)
    original_data_frame.drop_duplicates(inplace=True)
    return original_data_frame


def lat_long_to_lambert93(x, y):
	proj_gps = {"proj":'longlat', "ellps":'WGS84', "datum":'WGS84'}
	proj_lambert = {
		"proj":"lcc",
		"lat_2": 44,
		"lat_0": 46.5,
		"lon_0": 3,
		"x_0": 700000,
		"y_0": 6600000,
		"ellps": "GRS80",
		"towgs84": "0, 0, 0, 0, 0, 0, 0",
		"units": "m"
	}
	transformer = Transformer.from_crs(proj_gps, proj_lambert, always_xy=True)
	long, lat = transformer.transform(x, y)
	return long, lat
