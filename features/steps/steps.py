#from behave_http.steps import append_path
from utils import append_path
from lxml import etree as et
#from uws import Job
import requests
import uws
from ensure import ensure
from purl import URL

# basic http support, copied from behave-http, but use my own custom append-function
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

@when('I make a POST request to "{url_path_segment}"')
def post_request(context, url_path_segment):
    url = append_path(context.server, url_path_segment)
    context.response = requests.post(
        url,
        data=context.data,
        headers=context.headers,
        auth=context.auth
    )

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

@then('the response status should be {status}')
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
@then('the response status should not be {status}')
def response_status(context, status):
    ensure(context.response.status_code).is_not(int(status))

@given('I set BasicAuth username and password to user-defined values')
def set_basic_auth_headers(context):
    context.auth = (context.username, context.password)

@then('the "{var}" header should contain "{value}"')
def step_impl(context, var, value):
    header = context.response.headers[var].encode('ascii')
    ensure(value).is_in(header)

@when('I make a GET request to base URL')
def step_impl(context):
    url = context.server
    context.response = requests.get(
        url,
        headers=context.headers,
        auth=context.auth
    )

# general things, for UWS
@then('the attribute "{attribute}" should be "{value}"')
def step_impl(context, attribute, value):
    parsed = et.fromstring(str(context.response.text))
    attribute_value = parsed.get(attribute)
    ensure(attribute_value).equals(value)

@then('the UWS element "{element}" should exist')
def step_impl(context, element):
    parsed = et.fromstring(str(context.response.text))
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwselement = et.QName(uws_1_namespace, element)
    #raise NotImplementedError("%r" % parsed)
    foundvalue = parsed.find(uwselement, namespaces=parsed.nsmap).text
    ensure(foundvalue).is_not_none()

@then('the UWS root element is "{root}"')
def step_impl(context, root):
    parsed = et.fromstring(str(context.response.text))
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwsroot = et.QName(uws_1_namespace, root)
    foundroot = parsed.tag
    #raise NotImplementedError("%r" % foundroot)
    ensure(foundroot).equals(uwsroot)

@then('the UWS element "{element}" should be one of "{values}"')
def step_impl(context, element, values):
    #raise NotImplementedError('%r' %  context.response.text)
    parsed = et.fromstring(str(context.response.text))
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwselement = et.QName(uws_1_namespace, element)
    foundvalue = parsed.find(uwselement, namespaces=parsed.nsmap).text
    ensure(foundvalue).is_in([value.strip() for value in values.split(',')])

@then('the UWS element "{element}" should be "{value}"')
def step_impl(context, element, value):
    #raise NotImplementedError('%r' %  context.response.text)
    parsed = et.fromstring(str(context.response.text))
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwselement  = et.QName(uws_1_namespace, element)
    foundvalue = parsed.find(uwselement, namespaces=parsed.nsmap).text
    ensure(foundvalue).equals(value)

@then('all UWS elements "{element}" should be one of "{values}"')
def step_impl(context, element, values):
    values = [value.strip() for value in values.split(',')]
    parsed = et.fromstring(str(context.response.text))
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwselement = et.QName(uws_1_namespace, element)
    # find all elements, anywhere in the tree
    elementlist = parsed.findall('.//'+str(uwselement), namespaces=parsed.nsmap)
    #raise NotImplementedError('%r, %r' % (elementlist, uwselement))
    for elem in elementlist:
        ensure(elem.text).is_in(values)

@then('all UWS elements "{element}" should be "{value}"')
# TODO: this also validates as True, if there is no job at all
def step_impl(context, element, value):
    parsed = et.fromstring(str(context.response.text))
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwselement = et.QName(uws_1_namespace, element)
    # find all elements, anywhere in the tree
    elementlist = parsed.findall('.//'+str(uwselement), namespaces=parsed.nsmap)
    for elem in elementlist:
        ensure(elem.text).equals(value)

#@then('the number of UWS elements "{element}" should be less or equal to "{last}"')
#def step_impl(context, element, last)

# job specific
@when('I create a new job with')
def step_impl(context):
    #print (context)
    #queryparam = getattr(context, "query", None)
    for row in context.table:
        if row['qkey'] == 'query':
            queryparam = row['qvalue']
    
    #print ("queryparam");
    #raise NotImplementedError('%r' % (queryparam))
    # send post with query
    #client = Client("http://127.0.0.1:8000/soap/")
    #print ("query: %s " % (query))
    context.execute_steps(u'''
        When I make a POST request to "/" with
        | qkey   | qvalue      |
        | query  | {queryparam}  |
        
        '''.format(queryparam=queryparam))
    #raise NotImplementedError('%r' % (context.job.get_jobId()))
    # can also use: When I make my own GET request ....
    #context.execute_steps(u'''
    #    When I make a GET request to "{jobId}/phase"
    #    '''.format(jobId=context.job.get_jobId()))
    #print ('jobId: %s ' % str(context.job.get_jobId()) )
    # TODO: go on here! 
    # passing jobId here works fine!
    # Need to check, if I can also pass jobId from the top level in features.
    # Can I reuse scenarios in the same way as steps?




@when(u'I make a POST request to "{url_path_segment}" with')
def step_impl(context, url_path_segment):
    for row in context.table:
        name = row['qkey']
        value = row['qvalue']
        if (name == 'query'):
            query = value
    if not query:
        raise NotImplementedError('query parameter missing in test Scenario!')
    
    if not url_path_segment:
        url = context.server
    else:
        url = append_path(context.server, url_path_segment)
    
    context.response = requests.post(
        url, 
        data=context.data, 
        headers=context.headers, 
        auth=context.auth,
        params=context.table)
    
    # TODO: params should probably be stored in data!!!


    # look for jobId immediately and store it
    parsed = et.fromstring(str(context.response.text))
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwselement  = et.QName(uws_1_namespace, "jobId")
    jobId = parsed.find(uwselement, namespaces=parsed.nsmap).text

    context.job = uws.Job()
    context.job.set_jobId(jobId)

    # execute further checks

    #context.execute_steps(u'''
    #    When I make a GET request to "{jobId}/phase"
    #    Then the response status should be 200
    #    And the response body should contain "PENDING"
    #'''.format(jobId=context.job.get_jobId()))
    #raise NotImplementedError('%r, %r' % (context.response.text, context.job.get_jobId()))


@when(u'GET the job afterwards')
def step_impl(context):
    jobId = context.job.get_jobId()
    #raise NotImplementedError('%r' % jobId)
    # YES!!! jobId is known here!!! Can go on now!!!!
    # Should use outline or so, since jobId must have been set beforehand!!!
#    print ('jobId: ') % jobId
    context.execute_steps(u'''
        When I make a GET request to "{jobId}/phase"
        '''.format(jobId=context.job.get_jobId())
    )