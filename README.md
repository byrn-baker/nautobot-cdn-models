# Nautobot CDN Source of Truth

This nautobot plugin is to maintain and manage CDN LCDN configuration with Nautobot. 

## Required stuff
Before using this code, you will need to install Python, [Python Poetry](https://python-poetry.org/), and Docker.

Setup the virtual environment on a mac

```poetry env use 3.8```

```shell
$ poetry install
$ invoke build debug
```
After the Container is up and running you can start building your plugin

```shell
$ invoke makemigrations
$ invoke migrate
```


## To install on existing Nautobot deployment

```shell
$ poetry build
$ pip install ./dist/nautobot_cdn_configuration_manager-0.1.0.tar.gz
```
Poetry build will create the tar in the root of whatever directory you run ```poetry build``` in if you do not specify a directory.