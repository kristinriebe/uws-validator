class Job(object):

    def __init__(self):
        self.jobId = None
        self.phase = None

    def set_jobId(self, id):
        self.jobId = id

    def get_jobId(self):
        return self.jobId

    def get_phase(self):
        return self.phase  