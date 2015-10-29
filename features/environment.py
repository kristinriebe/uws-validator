#from behave_http.environment import before_scenario
from purl import URL

def before_all(context):
	userdata = context.config.userdata
	context.server = URL(userdata.get("server","someserver"))
	context.username = userdata.get("username","testuser")
	context.password = userdata.get("password","testpassword")

def before_scenario(context, scenario):
    # clear context.headers
    context.headers = {}

    # clear authentication information before each scenario
    context.auth = None
