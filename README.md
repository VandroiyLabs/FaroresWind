# FaroresWind

This is a Python package to collect, analyze and integrate data from multiple
electronic noses distributed over different locations. The electronic noses are
a home-made model that uses 8 MOX sensors manufactured by Figaro. Because of the
fixed structure, we store the data into a relational database (PostGre). This
software can (and eventually will) be extended to a more generic configutation.
Currently it only supports Python2.(6,7).



## Architecture of this package and application

This package is divided into three major parts:

* [Collector](https://github.com/VandroiyLabs/FaroresWind/tree/master/faroreswind/collector): collects data and periodically sends to the server via
SSH connection.

* [Server](https://github.com/VandroiyLabs/FaroresWind/tree/master/faroreswind/server): integrates data from multiple, remote electronic noses into a
  PostGre database, and creates a webservice.

* [Client](https://github.com/VandroiyLabs/FaroresWind/tree/master/faroreswind/client): connects to the server to manage the database and retrieve data.


## Installation

### Using pip

You can install (and update) this package using
[PIP](https://en.wikipedia.org/wiki/Pip_%28package_manager%29).
Remember to run this with admin permissions.

```
pip install -U git+https://github.com/VandroiyLabs/FaroresWind
```


### Using setup.py

To install or update this package using setup.py, all you need
to do is to download it and run the setup.py script. Remember to
run this with admin permissions.

```
git clone https://github.com/VandroiyLabs/FaroresWind
python setup.py install
```


## Dependencies

List of Python libraries that this package depends on.

* Matplotlib
* Numpy
* Scipy
* pySerial
* Tornado
* json
* urllib2
* multiprocessing
* websocket and websocket-client
* gnupg

## License

This software is distributed under the GPL-3.0 public license. View a complete copy of the license in the file [LICENSE](https://github.com/VandroiyLabs/FaroresWind/blob/master/LICENSE).
