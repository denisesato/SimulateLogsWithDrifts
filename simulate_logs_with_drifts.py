import os
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.obj import EventLog
from datetime import datetime


def simulate_log(net1, im1, fm1, i, timestamp, case_id):
    eventlog = simulator.apply(net1, im1, fm1, variant=simulator.Variants.BASIC_PLAYOUT,
                               parameters={
                                   simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: i,
                                   simulator.Variants.BASIC_PLAYOUT.value.Parameters.INITIAL_TIMESTAMP:
                                       timestamp,
                                   simulator.Variants.BASIC_PLAYOUT.value.Parameters.INITIAL_CASE_ID: case_id})
    # get the timestamp of the last event
    last_event = eventlog[-1][-1]
    last_datetime = last_event['time:timestamp']
    last_timestamp = datetime.timestamp(last_datetime)
    timestamp = last_timestamp + 1
    # increment the case id
    case_id = case_id + i
    return eventlog, timestamp, case_id


def generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, intervals, out_folder, out_filename):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    eventlog = []
    base_model = True
    timestamp = 10000000
    case_id = 1
    for i in intervals:
        if base_model:
            new_log, timestamp, case_id = simulate_log(net1, im1, fm1, i, timestamp, case_id)
            eventlog.extend(new_log)
        else:
            new_log, timestamp, case_id = simulate_log(net2, im2, fm2, i, timestamp, case_id)
            eventlog.extend(new_log)
        base_model = not base_model

    eventlog = EventLog(eventlog)
    xes_exporter.apply(eventlog, os.path.join(out_folder, f'{out_filename}.xes'))


def generate_dataset2():
    folder = 'data/output/models'
    drift_folder = 'data/output/drift/dataset2'
    patterns = [
        'cb',
        'cd',
        'cf',
        'cm',
        'cp',
        # 'fr', not used because it does not affect the model structure
        'IOR',
        'IRO',
        'lp',
        'OIR',
        'ORI',
        'pl',
        'pm',
        're',
        'RIO',
        'ROI',
        'rp',
        'sw',
    ]

    intervals = [
        [250, 500, 750, 1000, 500],  # 3,000 traces (4 drifts)
        [250, 500, 750, 1000, 750, 500, 250, 500],  # 4,500 traces (7 drifts)
        [250, 500, 750, 1000, 750, 500, 250, 500, 750, 1000, 750, 500, 250, 250],  # 8,000 traces (13 drifts)
    ]

    size = [
        '3k', '4.5k', '8k'
    ]

    base_model_name = 'base.pnml'
    for p in patterns:
        for i, s in zip(intervals, size):
            net1, im1, fm1 = pnml_importer.apply(os.path.join(folder, base_model_name))
            net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, f'{p}.pnml'))
            generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, i, drift_folder, f'{p}{s}')


def generate_sample_logs():
    folder = os.path.join('data', 'output')
    drift_folder = os.path.join('data', 'output', 'drift')
    net1, im1, fm1 = pnml_importer.apply(os.path.join(folder, 'model1.pnml'))
    net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, 'model2.pnml'))
    intervals = [10, 10, 10, 10]
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, intervals, drift_folder, 'drift_log_10')
    intervals = [20, 20]
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, intervals, drift_folder, 'log_2drifts_intervalo20')


def generate_dataset1_eventlogs_with_problems_in_the_original():
    # The original dataset from the paper "Fast and Accurate Business Process Drift Detection, 2015"
    # Available for download at: https://data.4tu.nl/articles/dataset/Business_Process_Drift/12712436
    # Contain some event logs with do not follow exactly the configuration of drifts described
    # in the paper. In this situations, we created a new log using the simulation from Pm4Py
    #
    # Event logs that do not follow the configuration described in the paper:
    # cb10k.xes -> contain only one drift after 5000 traces
    # cd2.5k.xes -> contain 9 drifts after 250 traces, however the altered model is completely
    #               different from the base model (also different from the BPMN specification)
    # cd7.5k.xes -> same problem as the cd2.5k.xes, with 7500 traces and a drift after 750 traces
    # cm2.5k.xes -> contain 9 drifts after 25 traces, however the altered model is the one
    #               from cb instead of the defined in the BPM specification
    # cm7.5k.xes -> same problem as the cm2.5k.xes, with 7500 traces and a drift after 750 traces
    # lp2.5k.xes -> contain 5000 traces with a drift after 500 traces -> renamed to lp5k.xes
    # lp5k.xes -> contain 10000 traces with a drift after 1000 traces -> renamed to lp10k.xes
    # lp7.5k.xes -> contain 15000 traces with drifts not following the specification
    #               drifts at: 1000; 3500; 4000; 6500; 7000; 9500; 10000; 12500; 13000
    # lp10k.xes -> same problem as described for lp7.5k.xes -> also have 15000 traces
    # re2.5k.xes -> contain 5000 traces with a drift after 500 traces -> renamed to re5k.xes
    # re5k.xes -> contain 10000 traces with a drift after 1000 traces -> renamed to re10k.xes
    # re7.5k.xes -> contain 15000 traces with drifts not following the specification
    #               drifts at: 1000; 2000; 2500; 3500; 4000; 5000; 5500; 6500; 7000; 8000;
    #                          8500; 9500; 10000; 11000; 11500; 12500; 13000
    # re10k.xes -> contain 20000 traces with a drift after 2000 traces, and the log contain
    #              a loop (the same of the lp logs) instead of a re
    folder = 'data/output/models'
    drift_folder = 'data/output/drift/dataset1'
    net1, im1, fm1 = pnml_importer.apply(os.path.join(folder, 'base.pnml'))
    interval_250 = [250 for i in range(10)]
    interval_500 = [500 for i in range(10)]
    interval_750 = [750 for i in range(10)]
    interval_1000 = [1000 for i in range(10)]
    # cb10k.xes
    net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, f'cb.pnml'))
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_1000, drift_folder, f'cb10k')
    # cd2.5k.xes
    net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, f'cd.pnml'))
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_250, drift_folder, f'cd2.5k')
    # cd7.5k.xes
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_750, drift_folder, f'cd7.5k')
    # cm2.5k.xes
    net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, f'cm.pnml'))
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_250, drift_folder, f'cm2.5k')
    # cm7.5k.xes
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_750, drift_folder, f'cm7.5k')
    # lp2.5k.xes
    net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, f'lp.pnml'))
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_250, drift_folder, f'lp2.5k')
    # lp7.5k.xes
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_750, drift_folder, f'lp7.5k')
    # re2.5k.xes
    net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, f're.pnml'))
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_250, drift_folder, f're2.5k')
    # re7.5k.xes
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, interval_750, drift_folder, f're7.5k')


if __name__ == '__main__':
    # generate_sample_logs()
    generate_dataset2()
    generate_dataset1_eventlogs_with_problems_in_the_original()
