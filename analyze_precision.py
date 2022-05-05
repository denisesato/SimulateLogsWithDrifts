import pandas as pd
import os
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.obj import EventLog
from pm4py.algo.discovery.footprints import algorithm as fp_discovery
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.conformance.footprints.util import evaluation

from create_sample1 import create_sample_event_log1, create_sample_event_log2, discover_model


def trace1_as_eventlog():
    trace1 = [
        [1, 'a', '2002-04-21 10:00:00'],
        [1, 'b', '2002-04-21 11:00:00'],
        [1, 'd', '2002-04-21 11:20:00'],
    ]
    return convert_trace_to_eventlog(trace1)


def trace2_as_eventlog():
    trace2 = [
        [2, 'a', '2002-04-21 10:20:00'],
        [2, 'c', '2002-04-21 11:00:00'],
        [2, 'd', '2002-04-21 13:40:00'],
    ]
    return convert_trace_to_eventlog(trace2)


def trace3_as_eventlog():
    trace3 = [
        [3, 'a', '2002-04-21 11:20:00'],
        [3, 'd', '2002-04-21 15:00:00'],
    ]
    return convert_trace_to_eventlog(trace3)


def convert_trace_to_eventlog(trace):
    df_trace = pd.DataFrame(trace, columns=['Case id', 'Activity', 'Timestamp'])
    log_from_df = dataframe_utils.convert_timestamp_columns_in_df(df_trace)
    log_from_df = log_from_df.sort_values('Timestamp')
    parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'Case id'}
    event_log = log_converter.apply(log_from_df, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)
    return event_log


def calculate_precision(net, im, fm, traces):
    parameters = {precision_evaluator.Variants.ETCONFORMANCE_TOKEN.value.Parameters.ACTIVITY_KEY: 'Activity'}
    for i, eventlog in enumerate(traces):
        precision = precision_evaluator.apply(eventlog, net, im, fm,
                                              variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN,
                                              parameters=parameters)
        print(f'Trace {i + 1} - {precision}')


def analyze_precisionETC():
    output_folder = os.path.join('data', 'output')

    # create 2 sample logs
    # first log {[a,b,d],[a.c.d],[a,d]}
    name_eventlog1 = 'sample_log1.csv'
    create_sample_event_log1(output_folder, name_eventlog1)
    # second log {[a,b,d],[a.c.d]}
    name_eventlog2 = 'sample_log2.csv'
    create_sample_event_log2(output_folder, name_eventlog2)
    # discover both models
    # first one is allows trace [a,d]
    net1, im1, fm1 = discover_model(output_folder, name_eventlog1, 'model1')
    # second do not allow trace [a,d]
    net2, im2, fm2 = discover_model(output_folder, name_eventlog2, 'model2')
    # get all the possible traces for model 1 as event log object
    traces_model1 = [
        trace1_as_eventlog(),
        trace2_as_eventlog(),
        trace3_as_eventlog()
    ]
    # get all the possible traces for model 2 as event log object
    traces_model2 = [
        trace1_as_eventlog(),
        trace2_as_eventlog(),
    ]

    # calculate precision of the first model (more general) using the three traces
    print("Precision of model 1 - using traces from model 1")
    calculate_precision(net1, im1, fm1, traces_model1)
    # calculate precision of the second model using the two allowed traces
    print("Precision of model 1 - using traces from model 2")
    calculate_precision(net1, im1, fm1, traces_model2)


def analyze_precisionFP():
    folder = os.path.join('data', 'output')
    # get the first model, the one that allows trace [a,d]
    net1, im1, fm1 = pnml_importer.apply(os.path.join(folder, 'model1.pnml'))
    # import the log with drift
    folder_logs = os.path.join(folder, 'drift')
    logname = 'drift_log_10.xes'
    filename = os.path.join(folder_logs, logname)
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(filename, variant=variant, parameters=parameters)

    first_log = EventLog(log[0:10])
    tree = inductive_miner.apply_tree(first_log)
    fp_log = fp_discovery.apply(first_log, variant=fp_discovery.Variants.ENTIRE_EVENT_LOG)
    fp_tree = fp_discovery.apply(tree, variant=fp_discovery.Variants.PROCESS_TREE)
    precision = evaluation.fp_precision(fp_log, fp_tree)
    print(f'Precision [0-10] - first model: {precision}')

    second_log = EventLog(log[10:20])
    fp_log = fp_discovery.apply(second_log, variant=fp_discovery.Variants.ENTIRE_EVENT_LOG)
    fp_tree = fp_discovery.apply(tree, variant=fp_discovery.Variants.PROCESS_TREE)
    precision = evaluation.fp_precision(fp_log, fp_tree)
    print(f'Precision [10-20] - first model: {precision}')


if __name__ == '__main__':
    # analyze_precisionETC()
    analyze_precisionFP()
