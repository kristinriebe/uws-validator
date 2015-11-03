# UWS validator

This validator uses the [behave](https://pypi.python.org/pypi/behave) Python module for functional tests of a UWS (1.1) server.
It uses the [Gherkin](https://cucumber.io/docs/reference) syntax (known from the Cucumber project) to define features to be tested in an easy-to-read English-like language. The features that I defined for UWS services are given in the `features`-directory. There is one file for each feature, containing one to many scenarios.

## Installation
First you need to have Python (2.7) installed. To run this validator, following additional packages are needed:

* **behave:** https://pypi.python.org/pypi/behave
* requests: for sending http requests
* ensure: for assertions
* lxml: for xml parsing
* json: for converting json-parameters from user to Python dictionary
* purl: for URL appending
* datetime: for parsing datetimes
* pytz: for timezone support


## Usage
    behave -D server="your_server" -D base_url="your_baseurl" -D username="your_username" -D password="your_password" <feature_file>

For UWS services without authentication, you can omit the username and password keywords or set them to an empty string "", otherwise please provide the credentials of a user who can access the job list and create new jobs for testing. 

Provide one or more <feature_file>'s on the command line to run the validator only for these features. This is recommended, if you want to run only a subset if the tests.

If you want full testing, you also need to specify the parameters for a short-running job, e.g. like this:

    behave [...] -D shortjob_parameters='{"query": "SELECT * FROM MDR1.Redshifts", "queue": "short"}'

You can also setup a `behave.ini` file that includes all these settings, e.g. like this:

```
[behave]
[behave.userdata]
server = your_servername
base_url = your_baseurl
username = your_username
password = your_password
shortjob_parameters = {"query": "SELECT x, y, z FROM MDR1.FOF LIMIT 10", "queue": "short"}
longjob_parameters = {"query": "SELECT SLEEP(1000)", "queue": "long"}
```

Then, if you omit the -D arguments, the defaults from this configuration file will be used. If you use both, configuration file and command line arguments, then the command line arguments overwrite the defaults.

### Using only a selection of tests
Each feature is stored in one feature file. If you only want to test one feature, then call behave with the name of the feature file, e.g.

    behave [...] features/account.feature

`behave` also allows to use *tags* for each scenario and to only test tagged scenarios using:

    behave [...] --tags=<tagname>

Use `--tags=-<tagname>` for excluding scenarios with the given tag name.

The tags used here are (have a look inside the feature-files!):
    * `uws1_1`: tag for the features/scenarios that belong exclusively to UWS 1.1 standard
    * `daiquiri`: tag for scenarios that are expected from the Daiquiri-implementation of UWS 1.1, but are not strictly required by the standard (e.g. behaviour if invalid filter values are given)
    * `slow`: tag for scenarios that are expected to be slow because they make a number of requests to the server (one for each job in the job list)

Also see https://pythonhosted.org/behave/tutorial.html#controlling-things-with-tags for more information on tags and their syntax in behave.


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
