
# Changelog

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


### backlog

- ~~integrate fiber in modext.webserv~~
- ~~integrate fiber in modcore~~
- ~~tls/ssl support~~
- rework api in @get and @post, so that accessing request parameter, and data needs less complex code
- fiber and fiber call stack, fiber api change
- WindUp configuration rework
- code review 
- package structure
- testing
- documentation


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
 [`fiber`](https://github.com/kr-g/mpymodcore/blob/master/modcore/fiber.py)
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
 [`fiber`](https://github.com/kr-g/mpymodcore/blob/master/modcore/fiber.py)
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

