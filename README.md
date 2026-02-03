![image](django_server_files/static/gjr_logo.png)

# Galaxy Job Radar
GJR is a project that visualizes traffic between [Galaxy](https://galaxyproject.org) and its [Pulsars](https://github.com/galaxyproject/pulsar).

Namely it shows jobs of a Galaxy instance, their distribution over Pulsar computational nodes, in which state they are and more. It supports both live view and history replay of traffic and past schedule evaluation.

[CESNET](https://www.cesnet.cz/en) manages a central instance of GJR at [https://gjr.metacentrum.cz](https://gjr.metacentrum.cz)

**We invite any public Galaxy servers to join this effort and share the anonymous data about their jobs with the central instance.**

## How to join

If you are an admin of a Galaxy instance please read the technical process below, if you are not an admin please reach out to them.

### Summary

*Start with writing us an email at galaxy@cesnet.cz that you'd like to join. First we will celebrate and then happily walk you through what needs to be done.*

1) Your Galaxy needs to be sending data to your InfluxDB via [gxadmin scripts](https://github.com/usegalaxy-eu/infrastructure-playbook/tree/master/roles/usegalaxy-eu.job-radar-stats-influxdb)
1) You give us access to read the InfluxDB (we need: `influxdb_password_var_name;influxdb_host;influxdb_port;influxdb_username`) and some basic information about your server (we need: `name;lat;long;`)
1) You send us information about your Pulsar servers (we need: `galaxy;pulsar_id;lat;long;node_count;desc`)
1) Wait few days and your Galaxy and Pulsars show up at [https://gjr.metacentrum.cz](https://gjr.metacentrum.cz)

### Details

GJR periodically requests data from each connected Galaxy through their own `InfluxDB` instance. Schema of this setup:

<img width="583" height="449" alt="image" src="https://github.com/user-attachments/assets/d1429cd4-53da-4c33-a8f0-dec6896d314a" />

For this to work we need the contributors to run an InfluxDB, fill it periodically with anonymous new data (with `gxadmin` scripts below) and give us read access to this data on InfluxDB. 

Note: If you do not run InfluxDB for monitoring yet there is a Galaxy [training section](https://training.galaxyproject.org/training-material/topics/admin/#st-monitoring) available which will explain reasons and guide you through the setup. Simplified schema of the full setup:

<img width="537" height="212" alt="galaxy_data_flow" src="https://github.com/user-attachments/assets/b8d4dc16-8542-4c41-9e1b-b7800781c819" />

## How to deploy own GJR

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
