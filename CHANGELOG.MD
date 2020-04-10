
# Changelog

## next version v0.0.4 - beta 1

- support for long running tasks (without asyncio) with
 [`fibers`](https://github.com/kr-g/mpymodcore/blob/master/modcore/fiber.py)
 (wrapper around performance optimized generator functions)

### backlog

- integrate fiberloop in modext.webserv and modcore
- finalize modext.webserv as own class
- tls/ssl support
- code review 
- package structure
- testing
- documentation


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

