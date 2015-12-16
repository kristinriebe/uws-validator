from utils import append_path, get_UwsName, get_XlinkName, get_dict_from_paramtable, get_joblink
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


# Steps for parsing the XML-response from a UWS service

## Generic steps
@then('the attribute "{attribute}" should be "{value}"')
def step_impl(context, attribute, value):
    parsed = et.fromstring(str(context.response.text))
    attribute_value = parsed.get(attribute)
    ensure(attribute_value).equals(value)

@then('each UWS element "{element}" should have an attribute "{attribute}"')
def step_impl(context, element, attribute):
    parsed = et.fromstring(str(context.response.text))
    # get elements:
    elementlist = parsed.findall('.//'+str(get_UwsName(element)), namespaces=parsed.nsmap)
    for elem in elementlist:
        # check if attribute exists in list of attributes:
        ensure(attribute).is_in(elem.attrib)
        # ensure(elem.get(attribute)).is_not_none() -- if to ensure that value is not None

@then('the UWS element "{element}" should exist')
def step_impl(context, element):
    parsed = et.fromstring(str(context.response.text))
    #raise NotImplementedError("%r" % parsed)
    found = parsed.find(get_UwsName(element), namespaces=parsed.nsmap)
    ensure(found).is_not_none()

@then('the UWS element "{element}" should not be None')
def step_impl(context, element):
    parsed = et.fromstring(str(context.response.text))
    #raise NotImplementedError("%r" % parsed)
    foundvalue = parsed.find(get_UwsName(element), namespaces=parsed.nsmap).text
    ensure(foundvalue).is_not_none()

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
    parsed = et.fromstring(str(context.response.text))
    foundvalue = parsed.find(get_UwsName(element), namespaces=parsed.nsmap).text
    ensure(foundvalue).equals(value)

@then('the UWS root element should contain UWS elements "{child}"')
def step_impl(context, child):
    parsed = et.fromstring(str(context.response.text))
    for subelement in parsed.iterchildren():
        ensure(subelement.tag).equals(get_UwsName(child))

@then('each UWS element "{element}" should have an element "{child}"')
def step_impl(context, element, child):
    parsed = et.fromstring(str(context.response.text))
    elementlist = parsed.findall('.//'+str(get_UwsName(element)), namespaces=parsed.nsmap)
    for elem in elementlist:
        subelement = elem.find(get_UwsName(child), namespaces=parsed.nsmap)
        ensure(subelement).is_not_none()

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
    ensure(count).is_less_than_or_equal_to(int(last))

@then('the number of UWS elements "{element}" should be greater than or equal to "{number}"')
def step_impl(context, element, number):
    parsed = et.fromstring(str(context.response.text))
    count = len(parsed.findall(get_UwsName(element), namespaces=parsed.nsmap))
    ensure(count).is_greater_than_or_equal_to(int(number))

@then('the number of UWS elements "{element}" should be "{number}"')
def step_impl(context, element, number):
    parsed = et.fromstring(str(context.response.text))
    count = len(parsed.findall(get_UwsName(element), namespaces=parsed.nsmap))
    ensure(count).equals(int(number))


## UWS element specific steps
@then('the UWS job startTime should be later than "{timestamp}"')
def step_impl(context, timestamp):
    #raise NotImplementedError(context.response.text)
    parsed = et.fromstring(str(context.response.text))
    startTime = parsed.find(get_UwsName("startTime"), namespaces=parsed.nsmap).text
    # make sure there is a startTime (NULL startTime should be ignored with AFTER filter)
    check(startTime).is_not_none().or_raise(Exception, "Error with startTime: {msg}. Job link is %s. The http response was: %r" % (context.joblink, context.response))

    # convert startTime to UTC, in case it has a timezone attached:
    date = dateutil.parser.parse(startTime)
    if date.utcoffset() is not None:
        utz = pytz.timezone('UTC')
        date = date.astimezone(utz).replace(tzinfo=None)
    date = date.isoformat()
    context.job = uws.Job()
    context.job.startTime = date

    # also convert timestamp to a useful format for comparison (not helping with format like 2015-W01 though)
    timestamp = dateutil.parser.parse(timestamp)

    ensure(date).is_greater_than(timestamp)

@then('the UWS job startTime should be later than or equal to "{timestamp}"')
def step_impl(context, timestamp):
    parsed = et.fromstring(str(context.response.text))
    startTime = parsed.find(get_UwsName("startTime"), namespaces=parsed.nsmap).text
    check(startTime).is_not_none().or_raise(Exception, "Error with startTime: {msg}. Job link is %s. The http response was: %r" % (context.joblink, context.response))

    # convert startTime to UTC, in case it has a timezone attached:
    date = dateutil.parser.parse(startTime)
    if date.utcoffset() is not None:
        utz = pytz.timezone('UTC')
        date = date.astimezone(utz).replace(tzinfo=None)
    date = date.isoformat()
    context.job = uws.Job()
    context.job.startTime = date

    # also convert timestamp to a useful format for comparison (not helping with format like 2015-W01 though)
    timestamp = dateutil.parser.parse(timestamp)

    ensure(date).is_greater_than_or_equal_to(timestamp)

@then('all UWS joblist startTimes should be later than "{timestamp}"')
def step_impl(context, timestamp):
    parsed = et.fromstring(str(context.response.text))
    element = "jobref"
    jobreflist = parsed.findall(get_UwsName(element), namespaces=parsed.nsmap)
    for jobref in jobreflist:
        refId = jobref.get("id")
        link = jobref.get(get_XlinkName("href"))
        joblink = get_joblink(context.server, link, refId)
        # make a get request and compare the startTime
        #raise NotImplementedError("joblink", joblink)
        context.joblink = joblink
        context.execute_steps(u'''
            When I make a GET request to URL "{url}"
            Then the response status should be "200"
            And the UWS job startTime should be later than "{timestamp}"
            '''.format(url=joblink, timestamp=timestamp)
        )

@then('all UWS joblist startTimes should be later than the stored startTime')
def step_impl(context):
    context.execute_steps(u'''
        Then all UWS joblist startTimes should be later than "{timestamp}"
        '''.format(timestamp=context.startTime_filter)
    )


@then('the UWS joblist should be sorted by startTime in ascending order')
def step_impl(context):
    parsed = et.fromstring(str(context.response.text))
    element = "jobref"
    jobreflist = parsed.findall(get_UwsName(element), namespaces=parsed.nsmap)
    timestamp = '0000-00-00T00:00:00'
    for jobref in jobreflist:
        refId = jobref.get("id")
        link = jobref.get(get_XlinkName("href"))
        joblink = get_joblink(context.server, link, refId)
        context.joblink = joblink;

        # make a get request and store the startTime
        context.execute_steps(u'''
            When I make a GET request to URL "{url}"
            Then the UWS job startTime should be later than or equal to "{timestamp}"
            '''.format(url=joblink, timestamp=timestamp)
        )
        timestamp = context.job.startTime
