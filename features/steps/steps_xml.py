from utils import append_path, get_UwsName, get_XlinkName, get_dict_from_paramtable, get_absolutelink
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


# Steps for parsing the XML-response from a UWS service

## Generic steps
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
        absolutelink = get_absolutelink(context, link)
        # Note: This is not necessarily a full link name, but could also be just the jobId! (e.g. CADC implementation)

        # make a get request and compare the startTime
        context.execute_steps(u'''
            When I make a GET request to URL "{url}"
            Then the UWS job startTime should be later than "{timestamp}"
            '''.format(url=absolutelink, timestamp=timestamp)
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
        jobId = jobref.get("id")
        link = jobref.get(get_XlinkName("href"))
        absolutelink = get_absolutelink(context, link)

        # make a get request and store the startTime
        context.execute_steps(u'''
            When I make a GET request to URL "{url}"
            Then the UWS job startTime should be later than "{timestamp}"
            '''.format(url=absolutelink, timestamp=timestamp)
        )
        timestamp = context.job.startTime