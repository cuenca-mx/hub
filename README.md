# Hub

[![Build Status](https://travis-ci.com/cuenca-mx/hub.svg?branch=master)](https://travis-ci.com/cuenca-mx/hub)
[![Coverage Status](https://coveralls.io/repos/github/cuenca-mx/hub/badge.svg?branch=master)](https://coveralls.io/github/cuenca-mx/hub?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Library to send and receive data between several instances through Kinesis. It uses a worker to keep listening 
streams and a producer to send data and wait for the response.

## Install dev

```bash
make install-dev
make test
```


## Testing

```bash
$ make test
```

## Linter

```bash
make format
make lint
```
