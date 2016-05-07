from utils import append_path, add_multi_path_segments, get_UwsName, get_XlinkName, get_dict_from_paramtable, get_joblink
from lxml import etree as et
import requests
import uws
from ensure import ensure, check
from purl import URL

# for parsing dates:
from datetime import datetime
import dateutil.parser
import pytz

# for job parameters in json format
import json

## basic http support, mainly copied from behave-http,
## https://github.com/mikek/behave-http/, BSD 2-Clause License
@given('I am using server "{server}"')
def using_server(context, server):
    context.server = URL(server)

@given('I set base URL to "{base_url}"')
def set_base_url(context, base_url):
    context.server = add_multi_path_segments(context.server, base_url)

@given('I set "{var}" header to "{value}"')
def set_header(context, var, value):
    # We must keep the headers as implicit ascii to avoid encoding failure when
    # the entire HTTP body is constructed by concatenating strings.
    context.headers[var.encode('ascii')] = value.encode('ascii')

@given('I set BasicAuth username to "{username}" and password to "{password}"')
def set_basic_auth_headers(context, username, password):
    context.auth = (username, password)

@when('I make a GET request to "{url_path_segment}"')
def step_impl(context, url_path_segment):
    url = append_path(context.server, url_path_segment)
#    if not url_path_segment.startswith('?'):
    # raise NotImplementedError("url: %r" % url)
    context.response = requests.get(
        url,
        headers=context.headers,
        auth=context.auth
    )

@when('I make a DELETE request to "{url_path_segment}"')
def delete_request(context, url_path_segment):
    url = append_path(context.server, url_path_segment)
    context.response = requests.delete(
        url,
        headers=context.headers,
        auth=context.auth
    )

@then('the response status should be one of "{statuses}"')
def response_status_in(context, statuses):
    ensure(context.response.status_code).is_in(
        [int(s) for s in statuses.split(',')]
    )

@then('the response status should be "{status}"')
def response_status(context, status):
    ensure(context.response.status_code).equals(int(status))

@then('the response body should contain "{content}"')
def response_body_contains(context, content):
    ensure(content).is_in(context.response.content.decode('utf-8'))

@then('the "{var}" header should be "{value}"')
def check_header_inline(context, var, value):
    ensure(context.response.headers[var].encode('ascii')).equals(
        value.encode('ascii'))
## end of part from behave-http


@given('I set BasicAuth username and password to user-defined values')
def set_basic_auth_headers(context):
    context.auth = (context.username, context.password)

@given('I set base URL to user-defined value')
def set_base_url(context):
    #context.server = context.server.add_path_segment(context.base_url)
    # This causes trouble on at least one setup (Windows 8, 64bit, Anaconda Python installation; '/' in path gets url-encoded!)
    # Thus try to avoid this:
    context.server = add_multi_path_segments(context.server, context.base_url)

@when('I make a GET request to base URL')
def step_impl(context):
    url = context.server
    print("      GET request to URL: ", url)
    print("      with authentication details: ", context.auth)

    context.response = requests.get(
        url,
        headers=context.headers,
        auth=context.auth
    )

@when('I make a GET request to URL "{url}"')
def step_impl(context, url):
    print("      GET request to URL: ", url)
    print("      with authentication details: ", context.auth)
    context.response = requests.get(
        url,
        headers=context.headers,
        auth=context.auth
    )

@when('I make a POST request to "{url_path_segment}" with')
def step_impl(context, url_path_segment):

    # convert given table-data to dictionary
    datadict = get_dict_from_paramtable(context.table)

    url = append_path(context.server, url_path_segment)

    print("      POST request to URL: ", url)
    print("      with authentication details: ", context.auth)

    context.response = requests.post(
        url,
        data=datadict,
        headers=context.headers,
        auth=context.auth
    )

@when('I make a POST request to base URL with')
def step_impl(context):

    # convert given table-data to dictionary
    datadict = get_dict_from_paramtable(context.table)

    url = context.server

    print("      POST request to URL: ", url)
    print("      with authentication details: ", context.auth)

    context.response = requests.post(
        url,
        data=datadict,
        headers=context.headers,
        auth=context.auth
    )
    #print("response: ", context.response, context.response.text)

@then('the "{var}" header should contain "{value}"')
def check_header_inline(context, var, value):
    ensure(value.encode('ascii')).is_in(context.response.headers[var].encode('ascii'))

@then('the response status should not be "{status}"')
def response_not_status(context, status):
    ensure(context.response.status_code).is_not(int(status))

