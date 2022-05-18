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


if __name__ == '__main__':
    # folder = os.path.join('data', 'output')
    # drift_folder = os.path.join('data', 'output', 'drift')
    # net1, im1, fm1 = pnml_importer.apply(os.path.join(folder, 'model1.pnml'))
    # net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, 'model2.pnml'))
    # intervals = [10, 10, 10, 10]
    # generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, intervals, drift_folder, 'drift_log_10')
    # intervals = [20, 20]
    # generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, intervals, drift_folder, 'log_2drifts_intervalo20')
    folder = 'data/output/models'
    drift_folder = 'data/output/drift/dataset2'
    patterns = [
        'cb',
        'cd',
        'cf',
        'cm',
        # 'cp', not used because the original model have duplicated activities
        # 'fr', not used because it does not affect the model structure
        'IOR',
        # 'IRO', not used because the original model have duplicated activities
        'lp',
        'OIR',
        'ORI',
        'pl',
        'pm',
        're',
        # 'RIO', not used because the original model have duplicated activities
        'ROI',
        'rp',
        'sw',
    ]

    intervals = [
        [250, 500, 750, 1000, 500], # 3,000 traces (4 drifts)
        [250, 500, 750, 1000, 750, 500, 250, 500], # 4,500 traces (7 drifts)
        [250, 500, 750, 1000, 750, 500, 250, 500, 750, 1000, 750, 500, 250, 250],  # 8,000 traces (13 drifts)
    ]

    size = [
        '3k', '4.5k', '8k'
    ]

    for p in patterns:
        for i, s in zip(intervals, size):
            net1, im1, fm1 = pnml_importer.apply(os.path.join(folder, f'{p}1.pnml'))
            net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, f'{p}2.pnml'))
            generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, i, drift_folder, f'{p}{s}')
