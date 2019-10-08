## Hub

[![Build Status](https://travis-ci.com/cuenca-mx/hub.svg?branch=master)](https://travis-ci.com/cuenca-mx/hub)
[![Coverage Status](https://coveralls.io/repos/github/cuenca-mx/hub/badge.svg?branch=master)](https://coveralls.io/github/cuenca-mx/hub?branch=master)

Library to send and receive data between several instances through Kinesis. It uses a worker to keep listening 
streams and a producer to send data and wait for the response.

## Testing
```bash
$ make test
```

### Linter

Para validar que todo se esta funcionando bien ejecutar el comando `make lint`. Se tiene activado el linter `flake8`.
Ejecutar previamente el comando `make format` para asegurarse que el formato de todos los archivos es correcto