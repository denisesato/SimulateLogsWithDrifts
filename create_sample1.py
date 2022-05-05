from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
import os
import pandas as pd


def create_sample_event_log1(output_folder, filename):
    eventlog1 = [
        [1, 'a', '2002-04-21 10:00:00'],
        [2, 'a', '2002-04-21 10:20:00'],
        [1, 'b', '2002-04-21 11:00:00'],
        [2, 'c', '2002-04-21 11:00:00'],
        [1, 'd', '2002-04-21 11:20:00'],
        [3, 'a', '2002-04-21 11:20:00'],
        [2, 'd', '2002-04-21 13:40:00'],
        [3, 'd', '2002-04-21 15:00:00'],
    ]
    df = pd.DataFrame(eventlog1, columns=['Case id', 'Activity', 'Timestamp'])
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    df.to_csv(os.path.join(output_folder, filename), index=False)


def create_sample_event_log2(output_folder, filename):
    eventlog2 = [
        [1, 'a', '2002-04-21 10:00:00'],
        [2, 'a', '2002-04-21 10:20:00'],
        [1, 'b', '2002-04-21 11:00:00'],
        [2, 'c', '2002-04-21 11:00:00'],
        [1, 'd', '2002-04-21 11:20:00'],
        [2, 'd', '2002-04-21 13:40:00'],
    ]
    df = pd.DataFrame(eventlog2, columns=['Case id', 'Activity', 'Timestamp'])
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    df.to_csv(os.path.join(output_folder, filename), index=False)


def discover_model(folder, filename, output_filename):
    complete_filename = os.path.join(folder, filename)
    log_csv = pd.read_csv(complete_filename, sep=',')
    log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
    log_csv = log_csv.sort_values('Timestamp')
    parameters = {log_converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY: 'Case id'}
    event_log = log_converter.apply(log_csv, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)
    # for trace in event_log:
    #     for ev in trace:
    #         print(f'[{trace.attributes["concept:name"]}] - {ev}')

    parameters = {inductive_miner.Variants.IM.value.Parameters.ACTIVITY_KEY: 'Activity'}
    net, im, fm = inductive_miner.apply(event_log, parameters=parameters)
    gviz = pn_visualizer.apply(net, im, fm)
    model_filename = os.path.join(folder, f'{output_filename}.png')
    pn_visualizer.save(gviz, model_filename)
    pn_filename = os.path.join(folder, f'{output_filename}.pnml')
    pnml_exporter.apply(net, im, pn_filename, final_marking=fm)
    return net, im, fm


if __name__ == '__main__':
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
