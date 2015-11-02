#from behave_http.environment import before_scenario
from purl import URL

def before_all(context):
    userdata = context.config.userdata
    context.server = URL(userdata.get("server","someserver"))
    context.base_url = userdata.get("base_url","somebaseurl")
    context.username = userdata.get("username","")
    context.password = userdata.get("password","")

def before_scenario(context, scenario):
    # clear context.headers
    context.headers = {}

    # clear authentication information before each scenario
    context.auth = None
