from purl import URL
from lxml import etree as et

# from behave-http:
def append_path(url, path):
    target = URL(path)
    if target:
        url = url.add_path_segment(target.path())
    if target.query():
        url = url.query(target.query())
    return url.as_string()
## end


def get_UWSName(element):
    uws_1_namespace = "http://www.ivoa.net/xml/UWS/v1.0"
    uwselement = et.QName(uws_1_namespace, element)
    return uwselement

