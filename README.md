# Galaxy-Pulsar Traffic Visualization (galaxy_visualisation)
Cesnet galaxy visualization project.

## Installation
To instal all dependencies just install requirements file: 

```
pip install requirements.txt
```

## Running application

### Inicialization
When you are running application for first time, you need to inicialize server and database.

```
python3 manage.py sqlcreate
```

```
python3 manage.py migrate
```

### Running
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

## Use real data from galaxy eu influxdb
To be able use data from influx database of real galaxies you need to set your environment variables with command as below:

```
export INFLUXDB_GALAXY_EU_PASSWORD='[password]'
```

## Example running instantiation
If you would like to, you can acces example running instantiation on:

[http://cloud255-46.cerit-sc.cz:8000/](http://cloud255-46.cerit-sc.cz:8000/)
