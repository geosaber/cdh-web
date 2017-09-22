# CDH Website

[![Build Status](https://travis-ci.org/Princeton-CDH/cdh-web.svg)](https://travis-ci.org/Princeton-CDH/cdh-web)
[![codecov](https://codecov.io/gh/Princeton-CDH/cdh-web/branch/master/graph/badge.svg)](https://codecov.io/gh/Princeton-CDH/cdh-web)
[![Code Health](https://landscape.io/github/Princeton-CDH/cdh-web/master/landscape.svg?style=flat)](https://landscape.io/github/Princeton-CDH/cdh-web/master)
[![Requirements Status](https://requires.io/github/Princeton-CDH/cdh-web/requirements.svg?branch=master)](https://requires.io/github/Princeton-CDH/cdh-web/requirements/?branch=master)


`cdhweb` is a Django+Mezzanine application that powers the CDH website
with custom models for people, events, and projects.


## Development instructions

Initial setup and installation:

- recommended: create and activate a python 3.5 virtualenv
    `virtualenv cdhweb -p python3.5`
    `source cdhweb/bin/activate`

- pip install required python dependencies
    `pip install -r requirements.txt`
    `pip install -r dev-requirements.txt`

- copy sample local settings and configure for your environment
    `cp cdhweb/local_settings.py.sample cdhweb/local_settings.py`

- download licensed fonts and install locally under /sitemedia/fonts/

- django-compressor dependencies: [install sass](http://sass-lang.com/install) for your operating system as appropriate. If you have Ruby gems installed, `gem install sass`. Also install [Node.js](https://nodejs.org/en/) and `npm`. Globally install `postcss-cli` and `autoprefixer`, i.e. 
`npm -g postcss-cli autoprefixer`. You may need `sudo` for these operations.


## Unit Testing

Unit tests are written with [py.test](http://doc.pytest.org/) but use Django fixture loading and convenience
testing methods when that makes things easier.  To run them, first install
development requirements:
```
pip install -r dev-requirements.txt
```

Run tests using py.test:
```
py.test
```
