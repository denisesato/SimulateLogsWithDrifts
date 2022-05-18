from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.objects.log.util import interval_lifecycle
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from pm4py.objects.conversion.process_tree import converter
from pm4py.objects.bpmn.layout import layouter
from pm4py.objects.log.obj import EventLog
from pm4py import discover_process_tree_inductive
import os


def extract_process_models(path, logname, pattern, interval, number_of_processes):
    output_path = 'data//output//models'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    filename = os.path.join(path, logname)
    original_log = xes_importer.apply(filename, variant=variant, parameters=parameters)
    # convert to interval log, if no interval log is provided as input this line has no effect
    log = interval_lifecycle.to_interval(original_log)

    for i in range(0, number_of_processes):
        # extract sub-log
        initial = i * interval
        sublog = EventLog(log[initial:initial + interval])
        net, initial_marking, final_marking = inductive_miner.apply(sublog)
        # net, initial_marking, final_marking = heuristics_miner.apply(log, parameters={
        #     heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.99})

        model_name = f'{pattern}{i + 1}'

        # bpmn_graph = converter.apply(tree, variant=converter.Variants.TO_BPMN)
        # gviz = bpmn_visualizer.apply(bpmn_graph)
        # bpmn_visualizer.save(gviz, os.path.join(output_path, f'{model_name}_bpmn.png'))

        pnml_exporter.apply(net, initial_marking, os.path.join(output_path, f'{model_name}.pnml'),
                            final_marking=final_marking)
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        pn_visualizer.save(gviz, os.path.join(output_path, f'{model_name}.png'))


def get_new_model_cb():
    path = 'data/output/models'
    pn_filename = 'cb2.pnml'
    net1, im1, fm1 = pnml_importer.apply(os.path.join(path, pn_filename))
    gviz = pn_visualizer.apply(net1, im1, fm1)
    pn_visualizer.save(gviz, os.path.join(path, f'cb2_atualizado.png'))


if __name__ == '__main__':
    input_folder = 'data/input/logs/Controlflow/dataset1'

    lognames5000 = [
        'cb5k.xes',
        'cd5k.xes',
        'cf5k.xes',
        'cm5k.xes',
        'cp5k.xes',
        'fr5k.xes',
        'IOR5k.xes',
        'IRO5k.xes',
        'lp2.5k.xes',  # this event log is configured with 5,000 traces with a drift each 500 traces
        'OIR5k.xes',
        'ORI5k.xes',
        'pl5k.xes',
        'pm5k.xes',
        're2.5k.xes',  # this event log is configured with 5,000 traces with a drift each 500 traces
        'RIO5k.xes',
        'ROI5k.xes',
        'rp5k.xes',
        'sw5k.xes',
    ]

    patterns = [
        'cb',
        'cd',
        'cf',
        'cm',
        'cp',
        'fr',
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

    for l, pt in zip(lognames5000, patterns):
        extract_process_models(input_folder, l, pt, 500, 2)

    get_new_model_cb()