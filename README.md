![image](django_server_files/static/gjr_logo.png)

# Galaxy Job Radar (GJR)
GJR is a project for Galaxy-Pulsar traffic visualisation (see [https://galaxyproject.org/eu/](https://galaxyproject.org/eu/) for more information) by CESNET (see [https://www.cesnet.cz/](https://www.cesnet.cz/)).

Application visualizes jobs of an instance of a galaxy server, how they are distributed over Galaxy computational nodes, in which state they are and so on. Application supports live view, history replay of traffic and past schedule evaluation.

Application is still in early version and we work on development. 

## Official running instance by CESNET and Metacentrum

[https://gjr.metacentrum.cz](https://gjr.metacentrum.cz)

## Running Galaxy Job Radar for your own Galaxy instance
GJR takes data from InfluxDB of a Galaxy instance so first you need to set up InfluxDB for your instance and periodically fill it with necessary data. There is Galaxy tutorial for Galaxy admins how to set up InfluxDB ([https://training.galaxyproject.org/training-material/topics/admin/tutorials/monitoring/slides-plain.html](https://training.galaxyproject.org/training-material/topics/admin/tutorials/monitoring/slides-plain.html)). Ansible infrastructure play-book for filling InfluxDB with neccessary data can be find here: [https://github.com/usegalaxy-eu/infrastructure-playbook/tree/master/roles/usegalaxy-eu.job-radar-stats-influxdb](https://github.com/usegalaxy-eu/infrastructure-playbook/tree/master/roles/usegalaxy-eu.job-radar-stats-influxdb).

In all possibilities you first need to add necessery info about your Galaxy instance. That means configuration csv file with information about your Galaxy server instance and your Pulsar network. Examples can be find here: **django_server_files/static/db_static_data**.

Then it is necessary to provide your credentials to your InfluxDB and Django secrets as environment variables inside file: **django_server_files/.env**. (INFLUXDB_GALAXY_EU_PASSWORD, SECRET_KEY and DEBUG)

Then you can run GJR with _pure Python_, in _Docker container_, or you can use our _Ansible infrastructure play-book_.

### Running with Python virtual environment
This is ideal option for quick development of GJR if you would like to **contribute**. _For contributing feel free to fork the project and make pull request and describe your changes_.

#### Installing
To instal all dependencies just install requirements file: 

```
pip install requirements.txt
```

#### Running application

##### Inicialization
When you are running application for the first time, you need to inicialize server and database.

```
python3 manage.py sqlcreate
```

```
python3 manage.py migrate
```

In case there is problem with migrations you possibly need to run 

```
python3 manage.py makemigrations
```

before _migrate_ command.

##### Running
First you need to start the server with:

```
python3 manage.py runserver [PORT]
```

To add galaxies and pulsars into map, you need to run command that will add objects to database:

```
python3 manage.py static_info_to_db
```

In opposite, if you would like to clear whole database (including history and everything), you need to run:

```
python3 manage.py flush
```

For running on fake data you need to use command:

```
python3 manage.py simulate_pulsar_job_computing
```

If you would like to use real data from galaxy servers where you have acces, you need to run command:

```
python3 manage.py influx_data
```

But the command takes just once data from influx, so you need to run it repeatedly with for example [cron](https://en.wikipedia.org/wiki/Cron) script.

Other scripts for InfluxDB data downloading which could be run against InfluxDB are **influx_data_hour** for hour data like failed jobs and so on, and **influx_data_4hours** for statistics once in 4 hours which downloads schedule evaluation.

There are as well programmed commands for removing pulsars by name, for removing galaxies by name and for removing just all pulsar, for more information see: **django_server_files/core/management/commands**.

#### Via Docker image
This option is great for testing if the whole ecosystem works. Docker image comes with Ubuntu and running periodic commands with cron.

By running classic docker build inside root directory. In repository is accesible working Dockerfile.

```
docker build -t gjr --load .
```

Then running docker run.

```
docker run --name gjr -p 8000:8000 gjr
```

#### Use ansible deployment scripts
The most convenient way to run GJR on server is to use Ansible deployment scripts. We have our infrastructure which can be used, but it would need to be adjusted for you environment. Still, you need GJR dockerized in some your favourite docker hub.

For more information you can find our playbooks [here](https://github.com/CESNET/galaxy-iacr/blob/main/ansible/gjr_setup.yml).

Have fun! If you would like to ask more, use this repository.
