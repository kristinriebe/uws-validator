from purl import URL

# from behave-http:
def append_path(url, path):
    target = URL(path)
    if target:
        url = url.add_path_segment(target.path())
    if target.query():
        url = url.query(target.query())
    return url.as_string()
## end