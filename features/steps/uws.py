class Job(object):
    """
    Class for a UWS job with all its elements and attributes
    """
    def __init__(self):
        self.jobId = None
        self.phase = None

    def set_jobId(self, id):
        self.jobId = id

    def get_jobId(self):
        return self.jobId

    def get_phase(self):
        return self.phase


class Jobref(object):
    """
    Class for jobref-elements that are returned in the job list
    """
    def __init__(self):
        self.id = None
        self.href = None
        self.phase = None

    def get_jobId(self):
        pass
#        return id