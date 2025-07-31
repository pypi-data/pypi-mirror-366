# LAPIN

[![CI - Test](https://github.com/Agence-de-mobilite-durable/lapin/actions/workflows/tests.yml/badge.svg)](https://github.com/Agence-de-mobilite-durable/lapin/actions/workflows/tests.yml)

## What it is

A framework for the analysis of on street parking occupancy via Licence Plate Recognition (LPR) data.

## Getting started

### Requirements

Install Lapin python's requirments with conda :

```sh
conda env create --name <YOUR_ENV_NAME> -f environment.yml
```


#### Optional

You may need to have a docker installation available on your machine. See
Valhalla mapmatching.

### Configuration

#### Project configuration
Create a config file for your project . You can create a blank one by running :

```sh
python -m lapin -c
```

#### Mapmatching configuration

You have the choice between two mapmatching engine : OSRM and Valhalla. The main
difference being that while using Valhalla you can do the matching directly on
the Montreal Geobase. Doing so improve the accuracy of the positionning of the
plate on the geobase. Thus improving the quality of the results.


##### Valhalla

To use valhalla, you'll need to compute the OSM network from the geobase file.
Then create the valhalla graph with valhalla engine and the OSM network. The
step are the following :

1. Create the OSM graph
```sh
python -m lapin --generate-graph

```

2. Generate Valhalla's graph

```sh
sudo docker run --rm --name valhalla_gis-ops -p 8002:8002 -v $PWD/data/network/valhalla:/custom_files -e tile ghcr.io/gis-ops/docker-valhalla/valhalla:latest'
```

3. Specify the use of valhalla in `lapin/__main__.py` line 113-115.

```python
    matcher_host='<PATH_TO_LAPIN>/lapin/data/network/valhalla/valhalla_tiles.tar',
    matcher_client='valhalla',
    matcher_kwargs={'service_limits':{"trace": {"max_shape": 26000}}}, # your desired config
```

##### OSRM

To use OSRM simply identify a valid OSRM instance.


1. Specify the use of OSRM in `lapin/__main__.py` line 113-115.

```python
    matcher_host=<ADRESS_TO_OSRM_INSTANCE>,
    matcher_client='osrm',
    matcher_kwargs={},
```

__Note__ : the instance must be launched with a sufficiently large `max-matching-size` parameter (e.g. 100000)

### Lauching an analysis

Then excecute the package with the following command :

```sh
python -m lapin --conf-file <PATH_TO_YOUR_CONF_FILE>
```


### Installing the module

Clone the repo and install the lapin package.

```sh
cd <repo_dir>
pip install .
```
