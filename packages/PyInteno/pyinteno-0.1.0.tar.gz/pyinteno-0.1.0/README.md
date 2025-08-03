# PyInteno - a very basic Inteno python bridge
[![Build and Test](https://github.com/nielstron/pyinteno/actions/workflows/build.yml/badge.svg)](https://github.com/nielstron/pyinteno/actions/workflows/build.yml)
[![Coverage Status](https://coveralls.io/repos/github/nielstron/pyinteno/badge.svg?branch=main)](https://coveralls.io/github/nielstron/pyinteno?branch=master)
 [![PyPI version](https://badge.fury.io/py/PyInteno.svg)](https://pypi.org/project/pyinteno/)
 ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PyInteno.svg)
 [![PyPI - Status](https://img.shields.io/pypi/status/PyInteno.svg)](https://pypi.org/project/pyinteno/)

A package that connects to a Inteno device in the local network and provides data
It uses the Inteno Websocket API to fetch data from the device.

## Features 

The package supports the following data provided by Inteno devices:

- Device list: A list of devices connected to the Inteno device
- Hardware Information: Information about the hardware of the Inteno device

That's it for now. I only use it for a home automation project, so I only implemented the features I needed.

## Contributing

Pull requests are very welcome.

If you own a Inteno device, feel free to provide us with raw data returned
by fetching the API endpoints manually.
