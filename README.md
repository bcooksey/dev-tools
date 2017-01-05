A collection of handy tools for web development, all accessible via a stand-alone server.

The primary objectives of this suite are to run locally (so your data doesn't leave your machine) and to have
no external dependencies besides Python.

Included tools are:

 * JSON/XML pretty printer
 * Time converter for Unix timestamps <-> ISO-8601 datetime strings
 * URL encoder/decoder
 * A file hosting service for testing uploading/downloading files (can also be used to serve up random JSON data files to fake out REST endpoints)
 * A UTC clock

## Installing

1. Snag the repo

  `git clone <repo>`

1. Setup the two required directories

  `mkdir data; mkdir uploads`

1. Copy any files you want to be able to serve up into the `data` directory.

1. Run the server (can optionally specify the `PORT` environment variable)

  `python server.py`

Visit `http://localhost:8084/` and enjoy!

## How to use it

Follow the install instructions and then visit `/` to read the documentation
