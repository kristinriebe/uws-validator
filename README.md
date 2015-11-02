# UWS validator

This validator uses the Python  `behave` module for integration tests for a UWS server.

## Usage:
    behave -D server="your_server" -D base_url="your_baseurl" -D username="your_username" -D password="your_password"

For UWS services without authentication, you can omit these keywords or set them to an empty string "", otherwise please provide the credentials of a user than can access the job list and create new jobs for testing. 

You can also setup a `behave.ini` file that includes these settings, e.g. like this:

```
[behave]
[behave.userdata]
server = your_servername
base_url = your_baseurl
username = your_username
password = your_password
```

Then, if you omit the -D arguments, the defaults from this configuration file will be used. If you use both, configuration file and command line arguments, then the command line arguments overwrite the defaults.

### Using only a selection of tests
Each feature is stored in one feature file. If you only want to test one feature, then call behave with the name of the feature file, e.g.

    behave features/account.feature

`behave` also allows to use *tags* for each scenario and to only test tagged scenarios using:

    behave --tags=<tagname>

The tags used here are (have a look inside the features-files!):
    * `@uws1_1`: tag for the features/scenarios that belong exclusively to UWS 1.1 standard
    * `@daiquiri`: tag for scenarios that are expected from the Daiquiri-implementation of UWS 1.1, but are not strictly required by the standard (e.g. behaviour if invalid filter values are given)

Also see https://pythonhosted.org/behave/tutorial.html#controlling-things-with-tags for more information on tags in general


## TODO
* Finish simple tests
* Write self tests to check that xml-parsing etc. works properly
    - (cannot check exact outcome - may differ from server to server)
* Implement checks that need to pass parameters (jobId)
* Check if it also works for non-Daiquiri webservices


## License:
I've copied some pieces for basic http-steps from behave-http from https://github.com/mikek/behave-http (BSD 2-Clause License), but did not want to import the complete package, because of all its additional dependencies (for setting up test server, json-support). 
That part is licensed under BSD 2-Clause License, see LICENSE_behave-http.

Still need to clarify which License we need to use for the other stuff.
