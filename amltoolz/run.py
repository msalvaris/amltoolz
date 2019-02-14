import pandas as pd
from amltoolz.collection import Collection


def _translate_log_name(log_name):
    return log_name.split('/')[-1].strip('.txt')


def _get_logs(aml_run):
    log_dict = aml_run.get_details_with_logs().get("logFiles")
    return {_get_logs(k) for k, v in log_dict.items()}


class Run(object):
    def __init__(self, id, aml_run):
        self._id = id
        self.aml_run = aml_run
        self.logs = Collection(lambda: _get_logs(self.aml_run))

    def __repr__(self):
        details_dict = self.details()
        return (
            f"Run: {details_dict['runId']} "
            f"Status: {details_dict['status']} "
            f"Start Time: {details_dict['startTimeUtc']} "
            f"End Time: {details_dict['endTimeUtc']} "
        )

    def __str__(self):
        return self.__repr__()

    def details(
        self, selected_details=("runId", "status", "startTimeUtc", "endTimeUtc")
    ):
        return extract_details_from(self.aml_run, details=selected_details)


def runs_to_df(run_list):
    return pd.DataFrame([extract_details_from(run) for run in run_list])


def extract_details_from(
    run, details=("runId", "status", "startTimeUtc", "endTimeUtc")
):
    run_details = run.get_details()
    return {detail: run_details.get(detail, None) for detail in details}


def extract_logs_from(run):
    details = run.get_details_with_logs()
    return details["logFiles"]

