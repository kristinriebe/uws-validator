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
import time


# Job specific steps

@when('I create and start a user-defined "{jobtype}" job')
def step_impl(context, jobtype):
    when_step = u'''When I make a POST request to base URL with\n'''
    paramtext = u'''| key | value |\n'''
    for key, value in context.job_parameters[jobtype].items():
        paramtext = paramtext + u'''| {key}  | {value} |\n'''.format(key=key, value=value)

    phasetext = u'''| PHASE  | RUN |\n'''
    context.execute_steps(when_step + paramtext + phasetext)

    # look for jobId immediately and store it
    parsed = et.fromstring(str(context.response.text))
    jobId = parsed.find(get_UwsName("jobId"), namespaces=parsed.nsmap).text

    context.job = uws.Job()
    context.job.set_jobId(jobId)
    context.created_jobs.append(jobId)

@when('I create a user-defined "{jobtype}" job')
def step_impl(context, jobtype):
    when_step = u'''When I make a POST request to base URL with\n'''
    paramtext = u'''| key | value |\n'''
    for key, value in context.job_parameters[jobtype].items():
        paramtext = paramtext + u'''| {key}  | {value} |\n'''.format(key=key, value=value)

    context.execute_steps(when_step + paramtext)

    # look for jobId immediately and store it
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


## Timing issues

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
def step_impl(context):
    requesttime = context.requesttime
    ensure(requesttime).is_less_than(context.requestdelay)

@then('the server should not return immediately')
def step_impl(context):
    requesttime = context.requesttime
    ensure(requesttime).is_greater_than(context.requestdelay)

@when('I wait for "{timeinseconds}" seconds')
def step_impl(context, timeinseconds):
    time.sleep(int(timeinseconds))
     
@when('I store the current datetime')
def step_impl(context):
    context.utcdatetime = datetime.utcnow().isoformat()

@when('I pick a startTime from the job list')
def step_impl(context):
    parsed = et.fromstring(str(context.response.text))
    elementlist = parsed.findall('.//'+str(get_UwsName("jobref")), namespaces=parsed.nsmap)
    if len(elementlist) < 2:
        raise NotImplementedError("Job list contains only %d jobs. Cannot test using this step." % len(elementlist))
    # also cannot test this, if there are no start times!!
    # Problem: there is not even any kind of ordering in the job list that I could assume,
    # so just search for the first two jobs that have a startTime

    i = 0
    job_startTimes = []
    while len(job_startTimes) < 2:
        startTime = None
        while startTime is None and i < len(elementlist):
            jobref = elementlist[-i] # use -i here, sicne I expect descending ordering, if any
            link = jobref.get(get_XlinkName("href"))
            absolutelink = get_absolutelink(context, link)
            response = requests.get(
                absolutelink,
                headers=context.headers,
                auth=context.auth
            )
            parsed = et.fromstring(str(response.text))

            startTime = parsed.find(get_UwsName("startTime"), namespaces=parsed.nsmap).text
            i = i + 1

        if startTime is not None:
            # convert startTime to UTC, in case it has a timezone attached:
            date = dateutil.parser.parse(startTime)
            if date.utcoffset() is not None:
                utz = pytz.timezone('UTC')
                date = date.astimezone(utz).replace(tzinfo=None)
                date = date.isoformat()
            job_startTimes.append(date)
        else:
            raise NotImplementedError("Cannot find enough jobs with a startTime, thus cannot test Scenarios using this. %r %r" % (link, startTime))

    # store the smallest startTime of these to ensure that I will get at 
    # least one result returned when filtering by this startTime
    context.startTime_filter = min(job_startTimes)


@when('I apply the AFTER filter with the stored startTime')
def step_impl(context):
    context.execute_steps(u'''
        When I make a GET request to "?AFTER={startTime}"
        '''.format(startTime=context.startTime_filter)
    )
    #raise NotImplementedError("context.utcdatetime: %s " % context.utcdatetime)


    # but then ... need to make sure that these jobs actually have startTimes! Otherwise they do not count!
    # ... could ensure this with LAST, but do not want this ...

