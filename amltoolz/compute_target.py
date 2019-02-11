class ComputeTarget(object):
    def __init__(self, id, aml_compute_target):
        self._id = id
        self.aml_compute_target = aml_compute_target

    def __repr__(self):
        return f"Compute Target {self._id}"
