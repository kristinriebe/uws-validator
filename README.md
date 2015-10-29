# UWS validator

This validator uses the Python  `behave` module for integration tests for a UWS server.

## Usage:
    `behave -D server="your_server" -D username="your_username" -D password="your_password"`

Currently, the validator expects that the service is protected with basic authentication, so a username and password needs to be provided for testing. 

You can also setup a `behave.ini` file that looks like this:

```
[behave]
[behave.userdata]
server = your_servername
username = your_username
password = your_password
```

## TODO
* Write self tests to check that xml-parsing etc. works properly
    - (cannot check exact outcome - may differ from server to server)
* Implement checks that need to pass parameters (jobId)


## License:
I've copied some pieces for basic http-steps from behave-http from https://github.com/mikek/behave-http (BSD 2-Clause License), but did not want to import the complete package, because of all its additional dependencies (for setting up test server, json-support). 
That part is licensed under BSD 2-Clause License, see LICENSE_behave-http.

Still need to clarify which License we need to use for the other stuff.
