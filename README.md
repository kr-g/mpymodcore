
# mpymodcore - a micro framework for MicroPython

An approach to modularize MicroPython projects.

Introduce a defined lifecycle and eventing model
for modules / devices for convenient handling
of loose coupled modules/ device

# What's new ?

Check
[`CHANGELOG`](https://github.com/kr-g/mpymodcore/blob/master/CHANGELOG.md)
for latest ongoing, or upcoming news


# Web Server included

In package `modext.http` there are basic HTTP request handling functions.

In package `modext.windup` is WindUp as included web server.

The WindUp web server is like 
[Apache](https://en.wikipedia.org/wiki/Apache_HTTP_Server)
based on the concept of Filter and Content Generator. 
What makes WindUp easy extensible; and flexible how requests are processed.

WindUp comes already with a bunch of Filters, e.g. HTML Form data parser, 
JSON processing, Query parameter extraction, Cookies, 
Session handling (in-memory), REST stlye URL parameter parser, and extraction, etc.

Multi-tasking processing support of HTTP requests based on fiber 
([`source`](https://github.com/kr-g/mpymodcore/blob/master/modcore/fiber.py)).

WindUp is in Alpha state and not performance optimized. 
Anyway response times under 1 secs are already possible.


### New to fiber ?

Like a async coroutines is a fiber an approach of cooperative multitasking.
Whereas objectives are the same.

Pros and Cons? 
Read more on wikipedia about
[`fiber`](https://en.wikipedia.org/wiki/Fiber_(computer_science))


#### Do i need to fiber my code ?

No. Serve traditional as you go, or fiber the code.


# Platform

Tested on ESP32 with PSRam and ESP8266 (for latter, see limitations below)

## Development status

Alpha state.
The API or logical call flow might change without prior notice.

In case your code breaks between two versions check
[`CHANGELOG`](https://github.com/kr-g/mpymodcore/blob/master/CHANGELOG.md)
information first before creating a ticket / issue on github. thanks.


# Limitations

- no asyncio integration as of now 
- with all mod's enabled as shown here in the sample
 it will not run on ESP8266 due to memory limit.
 but wlan, softap, and ntp should work 


# Sample Code

Some sample code can be found in
[`boot.py`](https://github.com/kr-g/mpymodcore/blob/master/boot.py)
and under [`samples`](https://github.com/kr-g/mpymodcore/tree/master/samples).

In order to run the samples sync the folder `www` from github to the local
project folder from where running the samples.
If running together with `boot.py` check for `run_not_in_sample_mode` and
set to `False` to prevent autostarting WindUp and blocking the socket,
or provide your own `boot.py`.

In oder to run the unsuported modules from the `mod3rd` folder download
this folder from github to the local project folder.


# Related project

`mpymodcore` is the successor of [mpyconfigbase](https://github.com/kr-g/mpyconfigbase)

For configuration of automatic startup of WLAN, SoftAP, and WebRepl refer to the 
source/ sample code also there


# Installation

- with pip (recommended)

    `# install to the current (project) folder`
    
    `python3 -m pip install mpymodcore --target .` 
    
 
- with [pygitgrab](https://github.com/kr-g/pygitgrab)
 to sync the master branch to your project folder 
 download the `mpymodcore.pygg` file from the repo to your local project folder
 and download the sources then with:

    `python3 -m pygitgrab -f mpymodcore.pygg`
 

### :heart: Credits

Developed with [Thonny](https://github.com/thonny/thonny) :+1:
    
