Welcome to this technical test.
=======

# This project enable you to retrieve network coverage giving a postal adress.

## Prerequisite

* You must have docker installed on your machine
* You must hace git account

## Setting Up application


* Clone the repository onto your local drive.
    ```shell
    git clone https://github.com/YvanBetremieux/fastapi-network-coverage.git
    ```
* Navigate into the project directory and start containers with docker-compose.
    ```shell
    $ cd fastapi-network-coverage/docker
    $ docker-compose up -d 
    ```
  
Once the 2 containers are started, navigate to <a href="http://localhost:8000/docs" target="_blank">the api url</a>

## First Step

* You have to populate db before starting retrieving adresses by running the endpoint
    ```shell
    [GET] add_data/csv
    ```

This endpoint is waiting a CSV file. You can find an example file to push into db in the directory
    
`fastapi-network-coverage/app/resources/2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv`


## Second Step
* You can search your network coverage's city by giving to this endpoint your adress
    ```shell
    [GET]/network/coverage
    ```

## In addition
* You will find in this project many others endpoints. I created them just to simulate a CRUD api. With these
  you can perform basic operations on db

## Additionnal informations

* You will find an additionnal file in resources folder name `` mccmnc.json``
    It is a file containing all Network Providers from France with additionnal infos. I extracted the infos i needed of the mccmnc package, 
    that did not satisfy me. I implemented my version with my needs.
* To retrieve cities from csv file, i use a snippet code: 
  ``` python
  import pyproj

    def lamber93_to_gps(x, y):
        lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
        wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        long, lat = pyproj.transform(lambert, wgs84, x, y)
        return long, lat
  ```
  This snippet works like a charm, but tend to be deprecated in the future. I'm now using the new approch of pyproj package
* To retreive city of the entire file (70K rows), I was first apply to each row using native pandas the previous snippet
  But it took more than 8 minutes to iter overs rows. I drastically reduce this time, using first Dask package, then pandarallel wich is a bit faster
  and it reduce the time using parallelization with core cpu.
* To populate db, I transform the original csv file into desired dataframe using pandas.
  Then, I use the to_sql method of a dataframe, wich allows me to insert multiple row within few seconds.
  I first loop over all the row and uses the orm insert, row by row, which was taking arround 40 minutes. With the to_sql method, i reduce it
  to 3 minutes.
* This api project is an hybrid beetween classic 'rest api' and 'crud Api'


## Improvements
* Add more unit tests
* Add integrations tests
* Using more Pydantic to improve data validation
