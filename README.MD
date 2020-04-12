
# mpymodcore - a micro framework for MicroPython

an approach to modularize MicroPython projects.

introduce a defined lifecycle and eventing model
for modules / devices for convenient handling
of loose coupled modules/ device

# what's new ?

check
[`CHANGELOG`](https://github.com/kr-g/mpymodcore/blob/master/CHANGELOG.MD)
for latest ongoing, or upcoming news


# Simple Web Server included

In package `modext.webserv` there are some functions for request handling.

In package `modext.webserv.serve` there is an example web server included.
Sample code in
[`serve.py`](https://github.com/kr-g/mpymodcore/blob/master/modext/webserv/serve.py)

Support for body data decoding e.g. form data, json

Delayed processing base on
[`fiber`](https://github.com/kr-g/mpymodcore/blob/master/modcore/fiber.py)


### new to fiber ?

like async coroutines is a fiber an approach of cooperative multitasking.
whereas objectives are the same.

pros ans cons? 
read more on wikipedia about
[fiber](https://en.wikipedia.org/wiki/Fiber_(computer_science))


# Platform

Tested ESP32 with PSRam and ESP8266 (for latter, see limitations below)

## Development status

Alpha state.
The API or logical call flow might change without prior notice.

In case your code breaks between two versions check
[`CHANGELOG`](https://github.com/kr-g/mpymodcore/blob/master/CHANGELOG.MD)
information first before creating a ticket / issue on github. thanks.


# Limitations

- no asyncio integration as of now 
- with all mod's enabled as shown here in the sample
 it will not run on ESP8266 due to memory limit.
 but wlan, softap, and ntp should work 


# Related project

`mpymodcore` is the successor of [mpyconfigbase](https://github.com/kr-g/mpyconfigbase)

for configuration of automatic startup of WLAN, SoftAP, and WebRepl refer to the 
source/ sample code also there


# Installation

- with pip

    `# install to the current (project) folder`
    
    `python3 -m pip install mpymodcore --target .` 
    
 
- with [pygitgrab](https://github.com/kr-g/pygitgrab)
 to sync the master branch to your project folder 
 download the `mpymodcore.pygg` file from the repo to your local project folder
 and download the sources then with:

    `python3 -m pygitgrab -f mpymodcore.pygg`
 

# Sample Code

some sample code can be found in [`boot.py`](https://github.com/kr-g/mpymodcore/blob/master/boot.py)


### :heart: credits

developed with [Thonny](https://github.com/thonny/thonny) :+1:
    
