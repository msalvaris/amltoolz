import logging
from time import sleep

import pandas as pd

import amltoolz.run
from amltoolz.collection import Collection
from amltoolz.run import Run, extract_details_from


def runs_to_df(experiment):
    run_list = list(experiment.get_runs())
    return pd.DataFrame([extract_details_from(run) for run in run_list])


def select_run_from(experiment, run_id=None, run_num=None):
    if run_id is not None:
        for run in experiment.get_runs():
            if run["runId"] == run_id:
                return run
    else:
        run_list = list(experiment.get_runs())
        return run_list[run_num]


def monitor(experiment, watch=False, interval=5):
    logger = logging.getLogger(__name__)
    try:
        if watch:
            logger.info(
                f"Monitoring experiment {experiment.name} | PRESS CTRL+C TO STOP"
            )
        while True:
            print(runs_to_df(experiment))
            if watch is False:
                break
            sleep(interval)
    except KeyboardInterrupt:
        logger.info("Stopping monitoring")


def _get_runs(aml_experiment):
    return {run.id: Run(run.id, run) for run in aml_experiment.get_runs()}


class Experiment(object):
    def __init__(self, id, aml_experiment):
        self._id = id
        self.aml_experiment = aml_experiment
        self.runs = Collection(lambda: _get_runs(self.aml_experiment))

    def __repr__(self):
        return f"Experiment {self._id}"

    def runs_to_df(self):
        run_iter = map(lambda x:getattr(x, 'aml_run'), self.runs)
        return amltoolz.run.runs_to_df(run_iter)
