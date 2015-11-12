#from behave_http.environment import before_scenario
from purl import URL
from steps.utils import delete_job
import json
import os.path

def before_all(context):

    userdata = context.config.userdata

    # load userdata from json config file, if exists,
    # see http://pythonhosted.org//behave/new_and_noteworthy_v1.2.5.html#index-7
    configfile = userdata.get("configfile", "userconfig.json")

    if os.path.exists(configfile):
        assert configfile.endswith(".json")
        more_userdata = json.load(open(configfile))
        context.config.update_userdata(more_userdata)
        # NOTE: Reapplies userdata_defines from command-line, too.

    # assign values of userdata to context-variables
    context.server = URL(userdata.get("server","someserver"))
    context.base_url = userdata.get("base_url","somebaseurl")
    context.username = userdata.get("username","")
    context.password = userdata.get("password","")

    jobparams = userdata.get("job_parameters","")
    if isinstance(jobparams, str):
        context.job_parameters = json.loads(jobparams)
    else:
        context.job_parameters = jobparams

    context.requestdelay = float(userdata.get("requestdelay","2")) # estimated time in seconds that it takes for a job request, due to latency in server response; ideal case would be 0 sec.; used as allowed deviation from WAIT-times

    # define lists to hold ids of created and removed jobs (for debugging):
    context.created_jobs = []
    context.removed_jobs = []

    context.config.setup_logging()

def before_scenario(context, scenario):
    # clear context.headers
    context.headers = {}

    # clear authentication information before each scenario
    context.auth = None


def after_scenario(context, scenario):
    # If there were any jobs created, then delete them now.
    # Ids of created jobs are stored in array context.created_jobs

    if context.created_jobs:
        jobs = list(context.created_jobs)
        for jobId in jobs:
            #delete_job(context, jobId)
            context.removed_jobs.append(jobId)
            context.created_jobs.remove(jobId)

def after_feature(context, feature):
    print("Clean-up: removing the created test jobs")
    if len(context.removed_jobs) > 0:
        print("The removed jobIds are: %r" % context.removed_jobs)
    if len(context.created_jobs) > 0:
        print("Remaining created jobIds: %r" % context.created_jobs)
    # Note: this also works across features!def after_feature(context, feature):



def after_all(context):
    if len(context.removed_jobs) > 0:
        print("The removed jobIds are: %r" % context.removed_jobs)
    if len(context.created_jobs) > 0:
        print("Remaining created jobIds: %r" % context.created_jobs)
    # Note: this also works across features!