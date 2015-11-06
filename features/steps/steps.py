from utils import append_path, get_UwsName, get_XlinkName, get_dict_from_paramtable
from lxml import etree as et
import requests
import uws
from ensure import ensure
from purl import URL

# for parsing dates:
from datetime import datetime
import dateutil.parser
import pytz

# for job parameters in json format
import json


# basic http support, mainly copied from behave-http,
# https://github.com/mikek/behave-http/, BSD 2-Clause License
@given('I am using server "{server}"')
def using_server(context, server):
    context.server = URL(server)

@given('I set base URL to "{base_url}"')
def set_base_url(context, base_url):
    context.server = context.server.add_path_segment(base_url)

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
    #raise NotImplementedError('%r %r %r ' % (url, context.username, context.password))
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

## Own steps

@given('I set BasicAuth username and password to user-defined values')
def set_basic_auth_headers(context):
    context.auth = (context.username, context.password)

@given('I set base URL to user-defined value')
def set_base_url(context):
    context.server = context.server.add_path_segment(context.base_url)

@when('I make a GET request to base URL')
def step_impl(context):
    url = context.server
    context.response = requests.get(
        url,
        headers=context.headers,
        auth=context.auth
    )

# general things, for UWS
@when('I make a GET request to URL "{url}"')
def step_impl(context, url):
    context.response = requests.get(
        url,
        headers=context.headers,
        auth=context.auth
    )


@then('the "{var}" header should contain "{value}"')
def check_header_inline(context, var, value):
    ensure(value.encode('ascii')).is_in(context.response.headers[var].encode('ascii'))

@then('the response status should not be "{status}"')
def response_not_status(context, status):
    ensure(context.response.status_code).is_not(int(status))

@then('the attribute "{attribute}" should be "{value}"')
def step_impl(context, attribute, value):
    parsed = et.fromstring(str(context.response.text))
    attribute_value = parsed.get(attribute)
    ensure(attribute_value).equals(value)

@then('the UWS element "{element}" should exist')
def step_impl(context, element):
    parsed = et.fromstring(str(context.response.text))
    #raise NotImplementedError("%r" % parsed)
    foundvalue = parsed.find(get_UwsName(element), namespaces=parsed.nsmap)
    ensure(foundvalue).is_not_none()

@then('the UWS element "{element}" should not be None')
def step_impl(context, element):
    parsed = et.fromstring(str(context.response.text))
    #raise NotImplementedError("%r" % parsed)
    foundvalue = parsed.find(get_UwsName(element), namespaces=parsed.nsmap).text
    ensure(foundvalue).is_not_none()
    # TODO: This actually tests for Not none, not if the element just exists or not!!!!

@then('the UWS root element should be "{root}"')
def step_impl(context, root):
    parsed = et.fromstring(str(context.response.text))
    foundroot = parsed.tag
    #raise NotImplementedError("%r" % foundroot)
    ensure(foundroot).equals(get_UwsName(root))

@then('the UWS element "{element}" should be one of "{values}"')
def step_impl(context, element, values):
    #raise NotImplementedError('%r' %  context.response.text)
    parsed = et.fromstring(str(context.response.text))
    foundvalue = parsed.find(get_UwsName(element), namespaces=parsed.nsmap).text
    ensure(foundvalue).is_in([value.strip() for value in values.split(',')])

@then('the UWS element "{element}" should be "{value}"')
def step_impl(context, element, value):
    #raise NotImplementedError('%r' %  context.response.text)
    parsed = et.fromstring(str(context.response.text))
    foundvalue = parsed.find(get_UwsName(element), namespaces=parsed.nsmap).text
    ensure(foundvalue).equals(value)

#@then('each UWS element "{element}" should contain an UWS element "{child}"')
#def step_impl(context, element, child):
#    parsed = et.fromstring(str(context.response.text))
#    elementlist = parsed.findall('.//'+str(get_UwsName(element)), namespaces=parsed.nsmap)
#    for e in elementlist:
#        subelement = e.find(get_UwsName(child), namespaces=parsed.nsmap)
#        raise NotImplementedError(e, subelement)
#        ensure(subelement).is_not_none


@then('the UWS root element should contain UWS elements "{child}"')
def step_impl(context, child):
    parsed = et.fromstring(str(context.response.text))
    for subelement in parsed.iterchildren():
        ensure(subelement.tag).equals(get_UwsName(child))


@then('all UWS elements "{element}" should be one of "{values}"')
def step_impl(context, element, values):
    values = [value.strip() for value in values.split(',')]
    parsed = et.fromstring(str(context.response.text))
    # find all elements, anywhere in the tree
    elementlist = parsed.findall('.//'+str(get_UwsName(element)), namespaces=parsed.nsmap)
    #raise NotImplementedError('%r, %r' % (elementlist, uwselement))
    for elem in elementlist:
        ensure(elem.text).is_in(values)

@then('all UWS elements "{element}" should be "{value}"')
# TODO: this also validates as True, if there is no job at all
def step_impl(context, element, value):
    parsed = et.fromstring(str(context.response.text))
    # find all elements, anywhere in the tree
    elementlist = parsed.findall('.//'+str(get_UwsName(element)), namespaces=parsed.nsmap)
    for elem in elementlist:
        ensure(elem.text).equals(value)

@then('the number of UWS elements "{element}" should be less than or equal to "{last}"')
# TODO: this also validates as True, if there is no job at all
def step_impl(context, element, last):
    parsed = et.fromstring(str(context.response.text))
    count = len(parsed.findall(get_UwsName(element), namespaces=parsed.nsmap))
    ensure(count).is_less_than_or_equal_to(last)

@then('the number of UWS elements "{element}" should be equal to 0')
def step_impl(context, element):
    parsed = et.fromstring(str(context.response.text))
    count = len(parsed.findall(get_UwsName(element), namespaces=parsed.nsmap))
    ensure(count).equals(0)

@then('the UWS job startTime should be later than "{timestamp}"')
def step_impl(context, timestamp):
    parsed = et.fromstring(str(context.response.text))
    startTime = parsed.find(get_UwsName("startTime"), namespaces=parsed.nsmap).text
    # convert startTime to UTC, in case it has a timezone attached:
    date = dateutil.parser.parse(startTime)
    if date.utcoffset() is not None:
        utz = pytz.timezone('UTC')
        date = date.astimezone(utz).replace(tzinfo=None)
    date = date.isoformat()
    context.job = uws.Job()
    context.job.startTime = date

    ensure(date).is_greater_than_or_equal_to(timestamp)

@then('all UWS joblist startTimes should be later than "{timestamp}"')
def step_impl(context, timestamp):
    parsed = et.fromstring(str(context.response.text))
    element = "jobref"
    jobreflist = parsed.findall(get_UwsName(element), namespaces=parsed.nsmap)
    for jobref in jobreflist:
        #context.jobref = uws.JobRef()
        #jobId = context.jobref.get_jobId()
        jobId = jobref.get("id")
        link = jobref.get(get_XlinkName("href"))
        # Note: This is not necessarily a full link name, but could also be just the jobId! (e.g. CADC implementation)

        # make a get request and compare the startTime
        context.execute_steps(u'''
            When I make a GET request to URL "{url}"
            Then the UWS job startTime should be later than "{timestamp}"
            '''.format(url=link, timestamp=timestamp)
        )

@then('the UWS joblist should be sorted by startTime in ascending order')
def step_impl(context):
    parsed = et.fromstring(str(context.response.text))
    element = "jobref"
    jobreflist = parsed.findall(get_UwsName(element), namespaces=parsed.nsmap)
    timestamp = '0000-00-00T00:00:00'
    for jobref in jobreflist:
        jobId = jobref.get("id")
        link = jobref.get(get_XlinkName("href"))
        # Note: This is not necessarily a full link name, but could also be just the jobId! (e.g. CADC implementation)

        # make a get request and store the startTime
        context.execute_steps(u'''
            When I make a GET request to URL "{url}"
            Then the UWS job startTime should be later than "{timestamp}"
            '''.format(url=link, timestamp=timestamp)
        )
        timestamp = context.job.startTime

# job specific
@when('I create a user-defined immediate job')
def step_impl(context):
    when_step = u'''When I make a POST request to base URL with\n'''
    paramtext = u'''| key | value |\n'''
    for key, value in context.job_parameters["immediate"].items():
        paramtext = paramtext + u'''| {key}  | {value} |\n'''.format(key=key, value=value)

    context.execute_steps(when_step + paramtext)

    # look for jobId immediately and store it
    parsed = et.fromstring(str(context.response.text))
    jobId = parsed.find(get_UwsName("jobId"), namespaces=parsed.nsmap).text

    context.job = uws.Job()
    context.job.set_jobId(jobId)
    # write to a file or a database as well??
    context.created_jobs.append(jobId)

@when('I create and start a user-defined immediate job')
def step_impl(context):
    when_step = u'''When I make a POST request to base URL with\n'''
    paramtext = u'''| key | value |\n'''
    for key, value in context.job_parameters["immediate"].items():
        paramtext = paramtext + u'''| {key}  | {value} |\n'''.format(key=key, value=value)

    phasetext = u'''| PHASE  | RUN |\n'''
    context.execute_steps(when_step + paramtext + phasetext)

    # look for jobId immediately and store it
    parsed = et.fromstring(str(context.response.text))
    jobId = parsed.find(get_UwsName("jobId"), namespaces=parsed.nsmap).text

    context.job = uws.Job()
    context.job.set_jobId(jobId)
    context.created_jobs.append(jobId)

@when('I create a user-defined short job')
def step_impl(context):
    when_step = u'''When I make a POST request to base URL with\n'''
    paramtext = u'''| key | value |\n'''
    for key, value in context.job_parameters["short"].items():
        paramtext = paramtext + u'''| {key}  | {value} |\n'''.format(key=key, value=value)

    context.execute_steps(when_step + paramtext)

    # look for jobId immediately and store it
    parsed = et.fromstring(str(context.response.text))
    jobId = parsed.find(get_UwsName("jobId"), namespaces=parsed.nsmap).text

    context.job = uws.Job()
    context.job.set_jobId(jobId)
    context.created_jobs.append(jobId)

@when('I create a user-defined long job')
def step_impl(context):
    when_step = u'''When I make a POST request to base URL with\n'''
    paramtext = u'''| key | value |\n'''
    for key, value in context.job_parameters["long"].items():
        paramtext = paramtext + u'''| {key}  | {value} |\n'''.format(key=key, value=value)

    context.execute_steps(when_step + paramtext)

    # look for jobId immediately and store it
    parsed = et.fromstring(str(context.response.text))
    jobId = parsed.find(get_UwsName("jobId"), namespaces=parsed.nsmap).text

    context.job = uws.Job()
    context.job.set_jobId(jobId)
    # write to a file or a database as well??
    context.created_jobs.append(jobId)

@when('I create a user-defined error job')
def step_impl(context):
    when_step = u'''When I make a POST request to base URL with\n'''
    paramtext = u'''| key | value |\n'''
    for key, value in context.job_parameters["error"].items():
        paramtext = paramtext + u'''| {key}  | {value} |\n'''.format(key=key, value=value)

    context.execute_steps(when_step + paramtext)

    parsed = et.fromstring(str(context.response.text))
    jobId = parsed.find(get_UwsName("jobId"), namespaces=parsed.nsmap).text

    context.job = uws.Job()
    context.job.set_jobId(jobId)
    context.created_jobs.append(jobId)

@when('I delete the same job')
def step_impl(context):
    jobId = context.job.get_jobId()
    context.execute_steps(u'''
            When I make a DELETE request to "{jobId}"
            '''.format(jobId=jobId)
    )
    context.created_jobs.remove(jobId)
    context.removed_jobs.append(jobId)

@when('I get the job details of the same job')
def step_impl(context):
    jobId = context.job.get_jobId()
    context.execute_steps(u'''
            When I make a GET request to "{jobId}"
            '''.format(jobId=jobId)
    )

@then('the response should be status "{status}" or the job has phase "{phase}"')
def step_impl(context, status, phase):
    if context.response.status_code == 200:
        context.execute_steps(u'''
            Then the UWS element "phase" should be "{phase}"
            '''.format(phase=phase)
        )
    else:
        ensure(context.response.status_code).equals(int(status))


@when('I send PHASE="{phase}" to the phase of the same job')
def step_impl(context, phase):
    jobId = context.job.get_jobId()
    context.execute_steps(u'''
        When I make a POST request to "{jobId}/phase" with
        | key   | value   |
        | PHASE | {phase} |
        '''.format(jobId=jobId, phase=phase)
    )

@when(u'I make a POST request to "{url_path_segment}" with')
def step_impl(context, url_path_segment):

    # convert given table-data to dictionary
    datadict = get_dict_from_paramtable(context.table)

    url = append_path(context.server, url_path_segment)
    context.response = requests.post(
        url,
        data=datadict,
        headers=context.headers,
        auth=context.auth
    )

@when(u'I make a POST request to base URL with')
def step_impl(context):

    # convert given table-data to dictionary
    datadict = get_dict_from_paramtable(context.table)

    url = context.server
    context.response = requests.post(
        url,
        data=datadict,
        headers=context.headers,
        auth=context.auth
    )

@given('I pick a job in inactive phase')
def step_impl(context):
    context.execute_steps(u'''
        When I make a GET request to base URL
        '''
    )
    # find a job with phase COMPLETED, ERROR, ABORTED or ARCHIVED
    desired_phases = ['COMPLETED', 'ERROR', 'ABORTED']
    parsed = et.fromstring(str(context.response.text))
    # find all elements, anywhere in the tree
    elementlist = parsed.findall('.//'+str(get_UwsName("phase")), namespaces=parsed.nsmap)
    for elem in elementlist:
        if elem.text in desired_phases:
            jobId = elem.getparent().get("id")
            #raise NotImplementedError("job Id %r" % jobId)
            context.job = uws.Job()
            context.job.set_jobId(jobId)

            return
    raise NotImplementedError("Could not find a matching job.")

@given('I pick a job in active phase')
def step_impl(context):
    context.execute_steps(u'''
        When I make a GET request to base URL
        '''
    )
    # find a job with phase COMPLETED, ERROR, ABORTED or ARCHIVED
    desired_phases = ['PENDING', 'QUEUED', 'EXECUTING']
    parsed = et.fromstring(str(context.response.text))
    # find all elements, anywhere in the tree
    elementlist = parsed.findall('.//'+str(get_UwsName("phase")), namespaces=parsed.nsmap)
    for elem in elementlist:
        if elem.text in desired_phases:
            jobId = elem.getparent().get("id")
            context.job = uws.Job()
            context.job.set_jobId(jobId)
            #raise NotImplementedError("job Id %r" % jobId)
            return
    raise NotImplementedError("Could not find a matching job.")

@when('I use blocking with WAIT="{waittime}"')
def step_impl(context, waittime):
    jobId = context.job.get_jobId()

    starttime = datetime.now()
    context.execute_steps(u'''
        When I make a GET request to "{jobId}?WAIT={waittime}"
        '''.format(jobId=jobId, waittime=waittime)
    )
    context.waittime = int(waittime) # check?
    endtime = datetime.now()
    difftime = endtime - starttime
    context.requesttime = difftime.seconds
    # TODO: maybe check that days is 0 first


@when('I use advanced blocking with WAIT="{waittime}" and PHASE="{phase}"')
def step_impl(context, waittime, phase):
    jobId = context.job.get_jobId()

    starttime = datetime.now()
    context.execute_steps(u'''
        When I make a GET request to "{jobId}?WAIT={waittime}&PHASE={phase}"
        '''.format(jobId=jobId, waittime=waittime, phase=phase)
    )
    context.waittime = int(waittime) # check?
    endtime = datetime.now()
    difftime = endtime - starttime
    context.requesttime = difftime.seconds
    # TODO: maybe check that days is 0 first


@then('the request time should be at least the wait time')
def  step_impl(context):
    requesttime = context.requesttime
    waittime = context.waittime
    ensure(requesttime).is_greater_than_or_equal_to(waittime)
    # NOTE: server could respond earlier, if overuse of resources etc!!


@then('the request time should not be much longer than the wait time')
def  step_impl(context):
    requesttime = context.requesttime
    waittime = context.waittime
    # allow a max. of requestdelay seconds more than the waittime for the request
    ensure(requesttime).is_less_than(waittime + context.requestdelay)

@then('the request time should be shorter than the wait time')
def  step_impl(context):
    requesttime = context.requesttime
    waittime = context.waittime
    ensure(requesttime).is_less_than(waittime)

@then('the server should return immediately')
# i.e. request time is smaller than allowed delay for server response
def  step_impl(context):
    requesttime = context.requesttime
    ensure(requesttime).is_less_than(context.requestdelay)

@then('the server should not return immediately')
def  step_impl(context):
    requesttime = context.requesttime
    ensure(requesttime).is_greater_than(context.requestdelay)

