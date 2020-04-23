
# Changelog

## next version v0.0.9

- 



### backlog

- ~~integrate fiber in modext.webserv~~
- ~~integrate fiber in modcore~~
- ~~tls/ssl support~~
- rework api in @get and @post, so that accessing request parameter, and data needs less complex code
- WindUp security hardening, user module, secure router with redirect/bad request response
- fiber and fiber call stack, fiber api change
- fiber stream integration
- WindUp configuration rework
- code review 
- package structure
- testing
- documentation


## version v0.0.8

- added `ntp-sync` event to ntp module, after sync was done sucessfully `ntp` event is raised
- added custom configurable event to fire to `moddev.interval`
 (see `boot.py` for `ntp-sync` event).
 e.g. with a few lines of code ntp sync can be triggered periodically 
- added module `moddev.control`. listens to events below:
  - `restart` values `[hard|modcore]`. hardreset, or restart all modcore modules (modc)
  - `status` values `[mem_0|mem_1|memfree]`. print the memory info
  - `gc` perform gc, print before, and after memory info
  - `pin`  control output pin, value data format `pinno:[on|off|toggle]`
- added `EventEmitter` as base class for `Interval`
  - evaluates id:event in config, and fires this. whereas event value can be also a list of strings
- added `AlarmClock` for defined alarm handling (once a day), with optional raising an event
- ntp module fires `ntp` now also after timezone change
- added `Button` for button optional with sending event. supports debouncing
- Button can emit event direclty by pressing, or when released (default)
- added `AlarmCounter` check upper and lower bounds, fires optional event
- moved global `SessionStore` to module `session`, added `session_mod` serving event `session-man`
 which purges all the expired sessions. can be triggered together with `Inverval` periodically
 - fix socket close after 404
 - added `switch` to [`FiberWorker`](https://github.com/kr-g/mpymodcore/blob/master/samples/untested/fiber_worker.py)
  as simple approach for scheduling and balancing workload to a given overall system reaction time
- added `sleep_ms` and `waitfor_ms` to `FiberWorker`
- added new samples in [`samples`](https://github.com/kr-g/mpymodcore/blob/master/samples)
 and in [`boot.py`](https://github.com/kr-g/mpymodcore/blob/master/boot.py) see config section
- fiber worker can spawn now into a different workerloop for execution (e.g. loop with higher prio)
- 


## version v0.0.7

- reworked fiber samples
- FibreWatchdog timer exposed
- custom HTML 404 handling
- simple admin html app for wlan (in unsupported mod3rd folder, not on pypi)
- wlan module rework, scan added, reconnect, `wlan-restart` event
- package redesign, allowing to run simple web based app (e.g. single status page) 
 on smaller devices (ESP8266) too
- new package `modext.http` containing basic request handling func
- new package `modext.windup`, move code out of webserv (which is not available any more)
- moved `fiber` from `modcore` to `modext.fiber` package
- removed WindUp request processing from loop to Processor class
- added fiber processor class, to allow WindUp to work in non-fiber-mode
- added [`fiber worker`](https://github.com/kr-g/mpymodcore/blob/master/samples/untested/fiber_worker.py)
 under new concepts/ untested in samples
- added [`fiber channel/stream`](https://github.com/kr-g/mpymodcore/blob/master/samples/untested/fiber_channel.py)
 under new concepts/ untested in samples
- added [`TestRecorder`](https://github.com/kr-g/mpymodcore/blob/master/modext/testrecorder/testrecorder.py) 
 for testing complex scenarios with id() tracking, approach as simple as `doctest`.
 see [`trec.txt`](https://github.com/kr-g/mpymodcore/blob/master/modext/testrecorder/testrecorder.trec.txt) file.
 __limitation__: not running under micropython as of now
- 


## version v0.0.6

- set_cookie path parameter
- url path filter decode %20 as space
- redirect http request
- fix REST xurl
- WindUp as included web server
- moved samples to own folder
- added ssl suppport (ussl.wrap_socket callback after accept in class WebServer and WindUp)
- 


## version v0.0.5

- added Guard, Detachable, and FiberContext in
 [`fiber`](https://github.com/kr-g/mpymodcore/blob/master/modext/fiber/core.py)
 module
- added fiber samples
- added performance counters to fiber loop
- added send_head and send_data to webserver RequestHandler
- added fiber, and fiberloop processing to
 [`serve.py`](https://github.com/kr-g/mpymodcore/blob/master/modext/webserv/serve.py)
 sample webserver 
- added send json response
-


## version v0.0.4 

- support for long running tasks (without asyncio) with
 [`fiber`](https://github.com/kr-g/mpymodcore/blob/master/modext/fiber/core.py)
 (wrapper around performance optimized generator functions)
- FormDataDecodeFilter for decoding "%" chars in form data


## version v0.0.3

- router with url root parameter
- extra slashes dense for path
- send chunks buffer for static file
- content generator supports py-generator functions
- some more code samples
- changed license to dual licensed
- rest style urls with url variables with @xget and @xpost decorators
- simple session manager (in-memory)
- 


## version v0.0.2

- fixed event name to lower case during fire_event
- added timeout class
- changed event model
- added ifconfig() to softap and wlan
- added minimalistic webserver under modext
- added url filtering for path, query, and parameter
- added simple static content generator
- added cookie filter
- changed package structure
- added index file handling
- added set_cookie()
- added simple router
- changed logging, support check of log level
- addded body content filter for decode
- added json parser filter
- added form data filter

