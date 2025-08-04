# hyrrokkin

```
 _                               _     _     _
| |__   _   _  _ __  _ __  ___  | | __| | __(_) _ __
| '_ \ | | | || '__|| '__|/ _ \ | |/ /| |/ /| || '_ \
| | | || |_| || |   | |  | (_) ||   < |   < | || | | |
|_| |_| \__, ||_|   |_|   \___/ |_|\_\|_|\_\|_||_| |_|
        |___/
```

A lightweight asynchronous directed acyclic graph (DAG) execution engine for Python (CPython) and Javascript (Deno)

* define nodes in using a simple API, grouped into packages
* define topologies which link nodes together
* run topologies
* attach clients to communicate with nodes while a topology is running 

## Installation Options

Hyrrokkin supports linux for python versions >= 3.10

Installation without dependencies (no support for YAML import/export, JSON schema checking):

```
pip install hyrrokkin
```

Installation with optional dependencies for YAML import/export:

```
pip install hyrrokkin[YAML]
```

Installation with optional dependencies for JSON schema validation:

```
pip install hyrrokkin[VALIDATION]
```

Installation with all optional dependencies

```
pip install hyrrokkin[VALIDATION,YAML]
```

## Documentation:

https://visualtopology.org/hyrrokkin

## Unit tests:

### Python unit tests

These cover the hyrrokkin CLI and API, and the python engine API

```
cd test/python/unit_tests
./run_all.sh
```

### Javascript unit tests

These cover the javascript engne API

```
cd test/javascript/unit_tests
./run_all.sh
```





