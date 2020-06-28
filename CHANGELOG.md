
# Changelog

## next version v0.0.12

- variable `$id$` as part of ssid name in `softap.cfg` will be expanded to machine unique id
- intr Counter rework
- 


### backlog

- ~~integrate fiber in modext.webserv~~
- ~~integrate fiber in modcore~~
- ~~tls/ssl support~~
- ~~WindUp security hardening, user module, secure router with redirect/bad request response~~
- Bluetooth®
- MQTT
- fiber and fiber call stack, fiber api change
- fiber stream integration
- WindUp configuration rework
- code review, coding standards
- package structure
- testing, automatic testing
- documentation



## version v0.0.11

- added __contains__ to Namespace. -> fix destorying windup session at the
 end of the request
- added `modext.irq` module for Interrupt and Counter handling
- base for [`mpymodcore_watering`](https://github.com/kr-g/mpymodcore_watering)
- 


## version v0.0.10

- added experimental template engine under
 [`mod3rd`](https://github.com/kr-g/mpymodcore/tree/master/mod3rd)
 current working name `Simplicity`. samples under
 [`samples/other3rd`](https://github.com/kr-g/mpymodcore/tree/master/samples/other3rd)
- fixed xpost group checking in `AuthRouter`, added samples
- added `IGNORE` option to [`TestRecorder`](https://github.com/kr-g/mpymodcore/tree/master/modext/testrecorder)
- added `TestRecoder.print()` for selective capturing content
- added code snipplet for websocket's under `samples/untested`
- moved `fiber channel/stream` to `modext.fiber_stream`
- moved `fiber worker` to `modext.fiber`
- fiber version 1 is marked as deprecated, will be slowly replaced by fiber worker
 (rename of fiber worker to fiber, and fiber loop resp.)
- addded `modext.config.Config` for json based configuration values
- added `modext.config.ReprDict` mixin which creates dict from __repr__ method,
 common usage is ReprDict -> dict -> json.dumps()
- added events `break` and `exit` to `moddev.control`
- moved loop from boot to `modext.misc.main` as generic optional module
-


## version v0.0.9

- reworked `Router` api: @get, @xget, @post and @xpost, so that accessing request
 parameter, and data needs less complex code
  - the function `args` parameter has changed __incompatible__ to the former versions!!!
  - the `args` parameter is now implemented as a namespace, meaning parameter can accessed without
    string quotations and using dict. here an example following
    [`REST`](https://en.wikipedia.org/wiki/Representational_state_transfer)
    having a [`Clean URL`](https://en.wikipedia.org/wiki/Clean_URL)
    
        @router.xget("/pin/:pin/:mode")
        def get_pin(req,args):
            
            # namespace access using args...
            # 
            logger.info( "sid cookie", args.cookies.sessionid )
            
            # probably a bit confusing, but looking on the cookie explains
            # why the sid is here at an other variable...
            logger.info("session_id", args.session.xsession_id )
            
            # log the rest args
            logger.info("rest parameter", args.rest )
            
            # keep the variable to avoid dict lookups -> performance
            rest = args.rest
            logger.info("pin", rest.pin )
            logger.info("mode", rest.mode )
            
            # avoid this -> dict lookup
            logger.info("mode", args.rest.mode )
            
            # do something else here...
            
            req.send_response( response="ok" )

  - the same applies to session, form, and json data
    - args.session [.session_variable]*
    - args.form [.form_field_name]
    - args.json [.attr_name]*
    
  - the 'old' method of accessing this data via `req.request.x[form|json|args|session]`
   is still possible, but will be removed in the future
    
- all `windup_*.py` [`samples`](https://github.com/kr-g/mpymodcore/blob/master/samples)
 have been updated 
  
- WindUp security hardening, user module, secure router with redirect/bad request response
  - added `AuthRouter` for checking permissions on role/group based access.
   the authentication data is saved under
   `/etc/shadow`.
   for each user 2 files are required.
   `_username_.pwd.txt`, and `_username_.grp.txt`. first contains the hashed password, and
   second contains the roles/groups the user belongs too. the roles are separeted by `:`.
   some sample code:
  
        from modext.windup_auth import AuthRouter

        secured_router = AuthRouter()

        @secured_router.get("/top-secret",groups=["admin"])
        def tops(req,args):
            req.send_response( response="ok, admin. you have permission" )

        @secured_router.get("/user-site",groups=["normaluser"])
        def tops(req,args):
            req.send_response( response="ok, buddy. you have permission" )
           
  - added one example [windup_security.py](https://github.com/kr-g/mpymodcore/blob/master/samples/windup_security.py). 
   there are 2 predefined users `test` and `admin`.
   by enter an invalid user name it fake's a session with no user / roles /groups, so that
   it possible to see how rejecting a request works.
   try the following URLs to play with it:
    - http://your-ip/login
    - http://your-ip/logout
    - http://your-ip/top-secret # only admin has permission
    - http://your-ip/user-site # only admin and test have permssion
  - important: there are no predefined roles/groups, and no default behaviour comes with it.
   the security sub-system only checks if a secured request is matching the user role/group.
   even the 2 example roles/groups in the sample `admin` and `normaluser` are just strings.
   e.g. the admin user has 2 roles/groups [assigned](https://github.com/kr-g/mpymodcore/tree/master/etc/shadow).
   these are: admin, and normaluser.
- added `mod3rd.admin_user.login` module. handling of URL `/login` and `/logout` with checking password.
 under `/etc/shadow` there are 3 sample user. `admin`,`test`, and `john` all password `test`
- added first draft for `Bluetooth®` [`GATT`](https://www.bluetooth.com/de/specifications/gatt/characteristics/)
 support under [`samples/untested`](https://github.com/kr-g/mpymodcore/tree/master/samples/untested)
   - sample for Broadcaster/Advertiser and GATT Server/ Peripheral, full
    roundtrip samples covering read, write, and notify with connected
    PC (testing done with `bluetoothctl`)
-


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

