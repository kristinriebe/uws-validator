from purl import URL
from lxml import etree as et
import requests


# from behave-http, slightly adjusted:
def append_path(url, path):
    target = URL(path)
    if target.path():
        url = url.add_path_segment(target.path())
    if target.query():
        url = url.query(target.query())

    #raise NotImplementedError("target2: %r %r %r" % (target, target.query, url))

    return url.as_string()
## end


def get_UwsName(element):
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwselement = et.QName(uws_1_namespace, element)
    return uwselement

def get_XlinkName(element):
    xlink_namespace = "http://www.w3.org/1999/xlink"
    xlinkelement = et.QName(xlink_namespace, element)
    return xlinkelement

def get_dict_from_paramtable(table):
    dictionary = {}
    for row in table:
        dictionary[ row[0] ] = row[1]
    return dictionary

def delete_job(context, jobId):
    url = append_path(context.server, jobId)

    # check phase of job that shall be deleted;
    # if still executing, abort it first (needed at least for Daiquiri implementation)
    response = requests.get(
            append_path(context.server, jobId+'/phase'),
            headers=context.headers,
            auth=context.auth
    )
    if response.text == "EXECUTING":
        # need to abort first:
        response = requests.post(
            append_path(context.server, jobId+'/phase?PHASE=ABORT'),
            headers=context.headers,
            auth=context.auth
        )

    try:
        response = requests.delete(
            url,
            headers=context.headers,
            auth=context.auth
        )
    except:
        print("Cannot delete job with id %s" % jobId)
        raise
    if response.status_code != 200:
        print ("Job deletion was not successful: %s, %s" % (jobId, response.text))


def get_joblink(context, link, refId):
    # Check, if the link is absolute,
    # if not: prepend the server name and base url.
    # Also check, if link is None (it's an optional attribute),
    # then use the refId for the job instead.
    #
    # This is needed, because most services (DaCHS, UWS library, Daiquiri, TAO)
    # return the full path as href-element in UWS xml response for a job,
    # but others (CADC) just return a relative link (the jobId).

    if link is None:
        link = refId

    if "://" not in link:
        # this is a relative path
        link = append_path(context.server, link)

    return link
