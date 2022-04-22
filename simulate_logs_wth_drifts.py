import os
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.obj import EventLog
from datetime import datetime


def generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, intervals, out_folder, out_filename):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    eventlog = []
    base_model = True
    timestamp = 10000000
    case_id = 1
    for i in intervals:
        if base_model:
            eventlog.extend(simulator.apply(net1, im1, fm1, variant=simulator.Variants.BASIC_PLAYOUT,
                                            parameters={
                                                simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: i,
                                                simulator.Variants.BASIC_PLAYOUT.value.Parameters.INITIAL_TIMESTAMP:
                                                    timestamp,
                                                simulator.Variants.BASIC_PLAYOUT.value.Parameters.INITIAL_CASE_ID: case_id}))
            # get the timestamp of the last event
            last_event = eventlog[-1][-1]
            last_datetime = last_event['time:timestamp']
            last_timestamp = datetime.timestamp(last_datetime)
            timestamp = last_timestamp + 1
            # increment the case id
            case_id = case_id + i
        else:
            eventlog.extend(simulator.apply(net2, im2, fm2, variant=simulator.Variants.BASIC_PLAYOUT,
                                            parameters={
                                                simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: i,
                                                simulator.Variants.BASIC_PLAYOUT.value.Parameters.INITIAL_TIMESTAMP:
                                                    timestamp,
                                                simulator.Variants.BASIC_PLAYOUT.value.Parameters.INITIAL_CASE_ID:
                                                    case_id}
                                            ))
            # get the timestamp of the last event
            last_event = eventlog[-1][-1]
            last_datetime = last_event['time:timestamp']
            last_timestamp = datetime.timestamp(last_datetime)
            timestamp = last_timestamp + 1
            # increment the case id
            case_id = case_id + i
        base_model = not base_model

    eventlog = EventLog(eventlog)
    xes_exporter.apply(eventlog, os.path.join(out_folder, f'{out_filename}.xes'))


if __name__ == '__main__':
    folder = os.path.join('data', 'output')
    net1, im1, fm1 = pnml_importer.apply(os.path.join(folder, 'model1.pnml'))
    net2, im2, fm2 = pnml_importer.apply(os.path.join(folder, 'model2.pnml'))
    intervals = [10, 10, 10, 10]
    drift_folder = os.path.join('data', 'output', 'drift')
    generate_log_with_drifts(net1, im1, fm1, net2, im2, fm2, intervals, drift_folder, 'drift_log1')
