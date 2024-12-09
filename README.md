![image](django_server_files/static/gjr_logo.png)

# GJR (Galaxy Job Radar)
Project for Galaxy-Pulsar traffic visualisation (see [https://galaxyproject.org/eu/](https://galaxyproject.org/eu/) for more information) by CESNET (see [https://www.cesnet.cz/](https://www.cesnet.cz/)).

Application visualize jobs of galaxy server, how they are distributed over pulsar network and galaxy TPVs, and in which state they are. Application supports live view and history replay of traffic.

Application is still in very early version and we work on development. 

## Official running instance by CESNET and Metacentrum

[https://gjr.metacentrum.cz](https://gjr.metacentrum.cz)

## Running locally with Docker
By running classic docker build inside root directory. In repository is accesible working Dockerfile.

```
docker build -t gjr --load .
```

Then running docker run.

```
docker run --name gjr -p 8000:8000 gjr
```

## Development in virtual environment
### Installing
To instal all dependencies just install requirements file: 

```
pip install requirements.txt
```

### Running application

#### Inicialization
When you are running application for first time, you need to inicialize server and database.

```
python3 manage.py sqlcreate
```

```
python3 manage.py migrate
```

#### Running
First you need just to start the server with:

```
python3 manage.py runserver [PORT]
```

To add pulsars into map, you need to run command that will add pulsars to database:

```
python3 manage.py create_pulsars
```

In opposite, if you would like to clear pulsar database, you need to run:

```
python3 manage.py flush
```

For running on fake data you need to use command:

```
python3 manage.py simulate_pulsar_job_computing
```

If you would like to use real data from galaxy servers where you have acces, you need to run command:

```
python3 manage.py take_data_from_influx
```

### Use real data from galaxy eu influxdb
To be able use data from influx database of real galaxies you need to set your environment variables with .env file:
