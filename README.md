# UWS validator

This projects shall help to make functional tests of UWS (1.1) services as specified by the [IVOA](http://www.ivoa.net/documents/UWS). It uses [behave](https://pypi.python.org/pypi/behave), a Python module for functional testing.

The [Gherkin](https://cucumber.io/docs/reference) syntax (which originates from the Cucumber project) is used to define features that shall be tested in an easy-to-read English-like language. The features that I defined for UWS services are given in the `features`-directory. There is one file for each feature, each containing one to many scenarios. The `steps`-subdirectory contains the actual implementations for each step of the scenarios.

For the **impatient**: Please have a look at [User configuration](#user-configuration-parameters) and [Recommended usage](#recommended-usage) first for a quick start.


## Installation
First you need to have Python (2.7) installed. Then download the files of this project to a directory of your choice. Following additional packages are needed to run this validator:

* **behave:** https://pypi.python.org/pypi/behave
* requests: for sending http requests
* ensure: for assertions
* lxml: for xml parsing
* json: for converting json-parameters from user to Python dictionary
* purl: for URL appending
* datetime, dateutil: for parsing datetimes
* pytz: for timezone support
* time

## Usage
This section first covers some general things about running `behave` for the uws-validator. For the [Recommended usage](#recommended-usage), see the corresponding section below.

### General things
The general command line for running `behave` for a given feature is:

    behave [options] <feature_file>

Provide one or more `<feature_file>`'s on the command line to run the validator only for these features. This is recommended, if you want to run only a subset of the tests (see sections below). If you run `behave` from within the uws-validator directory, it will automatically detect the features-directory and make tests with all the available features. But before doing this, you need to first define some user parameters, as explained in the next section.

### User configuration parameters
There are a number of parameters required, which you can pass on the command line or using an ini/config file.

* `server`: name of your server, e.g. https://gaia.aip.de  
* `base url`: path to the UWS-endpoint, e.g. /tap/async or /uws/query  
* `username` + `password`: credentials for basic authentication, user must have permission to access the job list and create new jobs for testing. For UWS services without authentication, you can omit the username and password keywords or set them to an empty string "".  
* `job_parameters`: If you want full testing, you also need to specify the parameters for a number of jobs:

    - `"veryshort"` job: running < 1 sec., e.g. a simple select of 10 lines from a table, used for quickly checking if creating and starting a job works, can also take longer but will then slow down the whole testing process  
    - `"short"` job: running for a few seconds (~10, < 30 seconds), for checking the WAIT-blocking behaviour  
    - `"long"` job: running at least 30 seconds, only used for a few scenarios; can be ignored when excluding the scenarios tagged with "longjob", i.e. use `--tags=-longjob`  
    - `"error"` job: a job that will return with an error  
* (optional) `requestdelay`: a delay time in seconds which the server needs to respond to a simple request. The default is 2 seconds, but you can make it longer if the server takes more time to respond. Important for testing UWS1.1 blocking behaviour with WAIT.

All user parameters can be passed to `behave` in 3 different ways:

* **command line**: use the -D flag, e.g. like this:
    
    ```
    behave -D server="your_server" -D base_url="your_baseurl" -D username="your_username" -D password="your_password" -D job_parameters={"veryshort": {"query": "SELECT * FROM MDR1.Redshifts", "queue": "short"} ... <feature_file>
    ```

* **ini settings**: You can setup a `behave.ini` file that includes all the settings, for example:

    ```
    [behave]
    [behave.userdata]
    server = your_servername
    base_url = your_baseurl
    username = your_username
    password = your_password
    job_parameters = {"veryshort": {"query": "SELECT x, y, z FROM MDR1.FOF LIMIT 10", "queue": "short"},
                        "short": {"query": "SELECT SLEEP(10)", "queue": "long"},
                        "long": {"query": "SELECT SLEEP(1000)", "queue": "long"},
                        "error": {"query": "SELECT something to create an error"}
                    }
    ```

    If you omit the -D arguments, the defaults from this configuration file will be used. If you use both, configuration file and command line arguments, then the command line arguments overwrite the defaults.

* **userconfig.json**: For more advanced uses, e.g. when testing a number of services, you can also define json configuration files. They should be stored as `<filename>.json` and should look similar to this:

    ```json
    {
        "server": "your_servername",
        "base_url": "your_baseurl",
        "username": "your_username",
        "password": "your_password",
        "job_parameters": {
            "veryshort": {
                "query": "SELECT x, y, z FROM MDR1.FOF LIMIT 10"
            },
            "short": {
                "query": "SELECT SLEEP(10)"
            },
            "long": {
                "query": "SELECT SLEEP(1000)",
                "queue": "long"
             },
            "error": {
                "query": "SELECT something to create an error"
            }
        }
    }
    ```

    The file will only be used by behave, if you provide it as the configuration file:

    `behave [...] -D config_file=<filename>`

    where `<filename>` needs to be replaced by your chosen filename.


### Running a subset of tests
Each feature is stored in one feature file. If you only want to test one feature, then call behave with the name of the feature file, e.g.

    behave [...] features/account.feature

You can also run a certain scenario only by providing the row in the feature file (which is printed when running the tests on the right side):

    behave [...] features/joblist.feature:69

This can even be used to run just one example of many.

`behave` also allows to use *tags* for each scenario and to only test tagged scenarios using:

    behave [...] --tags=<tagname>

Use `--tags=-<tagname>` for excluding scenarios with the given tag name.

The tags used here are (have a look inside the feature-files!)  

* `basics`: Run these tests first to identify basic problems with user authentication, server name or running a job. All the other jobs rely on these basic tests to succeed.  
* `uws1_1`: tag for the features/scenarios that belong exclusively to UWS 1.1 standard  
* `version`: Use this tag to check (or exclude the check) for the correct version number for UWS 1.1 servers. This will be automatically excluded, if uws1_1 is excluded.  
* `invalid`: Tag for UWS 1.1 scenarios with examples for invalid values, used in some (most probably not all) implementations. They are not strictly required by the standard.    
* `slow`: tag for scenarios that are expected to be slow because they make a larger number of requests to the server (e.g. one for each job in the job list) or wait for certain things to happen  
* `neverending`: tag for the waiting forever feature (WAIT=-1)
* `longjob`: exclude this tag if you have no long job defined in user configuration  
* `shortjob`: exclude this tag if you have no short job defined in user configuration (needed only for testing WAIT-blocking)  

Also see https://pythonhosted.org/behave/tutorial.html#controlling-things-with-tags for more information on tags and their syntax with behave.

### Recommended usage
Store your details in the file `userconfig.json` and run the following steps one after each other. Make sure after each step that all scenarios pass without error before continuing.

1. `behave -D configfile="userconfig.json" features/account.feature`  
    This ensures that the user can access the given UWS-endpoint
2. `behave -D configfile="userconfig.json" --no-skipped --tags=basics`  
    This additionally checks if the user gets a job list returned and if he/she can create a "veryshort" pending job. If this fails, you need to fix this first. If it cannot be fixed, then only some tests for the *joblist.feature* will work, all other tests will fail.
3. For UWS 1.0 services exclude all 1.1 tests:  
    `behave -D configfile="userconfig.json" --no-skipped --tags=-uws1_1`  
    For UWS 1.1 services, first do the fast tests:  
    `behave -D configfile="userconfig.json" --no-skipped --tags=-slow --tags=-veryslow`
4. Do the remaining slow tests:  
    `behave -D configfile="userconfig.json" --no-skipped --tags=slow,veryslow`

You can also exclude all tests for the WAIT-blocking mechanism by
excluding the *job_wait.feature* file like this:
`behave -D configfile="userconfig.json" --no-skipped -e features/job_wait.feature`

## TODO
* The validator just uses the existing list of jobs for checking job-filtering. If there are no existing jobs in the list, the joblist-features cannot really be tested. Thus need to create a setup with a number of jobs with different phases before doing the joblist-tests + remove them all at the end.
* Properly define different testing levels, tag accordingly and describe how to use; maybe wrap behave with own main-function
* Use skip to exclude features/scenarios automatically, if given-conditions are not met, see
  http://pythonhosted.org//behave/new_and_noteworthy_v1.2.5.html#exclude-feature-scenario-at-runtime
* Properly treat errors.
* Improve error messages.
* Write self tests to check that xml-parsing etc. works properly
  (cannot check exact outcome - may differ from server to server)
* Check if it also works for non-Daiquiri webservices (tested so far with DaCHS, CADC)

## Known Issues
* If jobs can be deleted on the tested server at any time during the test runs by someone else, then certain assumptions are changing in between and tests are not reliable and may fail due to missing jobs. This can happen if the server is live and uses no authentication or if jobs are destroyed rather quickly.
* For AFTER- and LAST-filters, the startTime of each job must be known. Thus jobs that are generated during testing must first start, before they can appear in the job list and be filtered. For services which have a queueing mechanism and are under heavy load this may take hours or even days.
* Some servers support the WAIT-feature only as long as the server is not under heavy load. That means the WAIT-tests may pass at one time and fail at another time.

## License
I've copied some pieces for basic http-steps from behave-http from https://github.com/mikek/behave-http (BSD 2-Clause License), but did not want to import the complete package, because of all its additional dependencies (for setting up test server, json-support). 
That part is included in `steps_http.py` licensed under BSD 2-Clause License, see LICENSE_behave-http.

Still need to clarify which License we need to use for the other stuff, for now just expect it's free to use by anyone for anything without any restrictions and without any warranty from our side.
