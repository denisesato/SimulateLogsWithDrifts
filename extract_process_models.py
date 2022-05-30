from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.objects.log.util import interval_lifecycle
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from pm4py.objects.conversion.process_tree import converter
from pm4py.objects.bpmn.layout import layouter
from pm4py.objects.log.obj import EventLog
from pm4py import discover_process_tree_inductive
import os
import uuid
from lxml import etree


def extract_process_models(path, logname, pattern, interval, number_of_processes):
    output_path = 'data/input/models'
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
    path = 'data/input/models'
    pn_filename = 'cb2.pnml'
    net1, im1, fm1 = pnml_importer.apply(os.path.join(path, pn_filename))
    gviz = pn_visualizer.apply(net1, im1, fm1)
    pn_visualizer.save(gviz, os.path.join(path, f'cb2_atualizado.png'))


def create_models_with_duplicated_activities():
    #####################################################################
    # cp pattern
    #####################################################################
    net = PetriNet("cp")

    # creating source
    source = PetriNet.Place("source")

    # create sink places (define the number)
    number_of_sink_places = 3
    sink_places = []
    for i in range(number_of_sink_places):
        sink_places.append(PetriNet.Place(f"sink{i + 1}"))

    # create the other places (define the number)
    number_of_places = 18
    places = []
    for i in range(number_of_places):
        places.append(PetriNet.Place(f"p{i + 1}"))

    # add the source, sink and other places to the Petri Net
    net.places.add(source)
    for sp in sink_places:
        net.places.add(sp)
    for p in places:
        net.places.add(p)

    # Create transitions
    transitions = [PetriNet.Transition("t1", "Loan application received"),
                   PetriNet.Transition("t2", "Check application form completeness"),
                   PetriNet.Transition("t3", "Return application back to applicant"),
                   PetriNet.Transition("t4", "Receive updated application"),
                   PetriNet.Transition("t5", "Check credit history"),
                   PetriNet.Transition("t6", "Assess loan risk"),
                   PetriNet.Transition("t7", "Appraise property"),
                   PetriNet.Transition("t8", "Assess eligibility"),
                   PetriNet.Transition("t9", "Reject application"),
                   PetriNet.Transition("t10", "Loan application reject"),
                   PetriNet.Transition("t11", "Prepare acceptance pack"),
                   PetriNet.Transition("t12", "Check if home insurance quote is requested"),
                   PetriNet.Transition("t13", "Send home insurance quote"),
                   PetriNet.Transition("t14", "Send acceptance pack"),
                   PetriNet.Transition("t15", "Verify repayment agreement"),
                   PetriNet.Transition("t16", "Check credit history"),
                   PetriNet.Transition("t17", "Assess loan risk"),
                   PetriNet.Transition("t18", "Cancel application"),
                   PetriNet.Transition("t19", "Loan application canceled"),
                   PetriNet.Transition("t20", "Approve application"),
                   PetriNet.Transition("t21", "Loan application approved")
                   ]
    # Create silent transitions
    silent_transitions = [PetriNet.Transition("st1", None)]

    # Add the transitions to the Petri Net
    for t in transitions:
        net.transitions.add(t)
    for st in silent_transitions:
        net.transitions.add(st)

    # Add arcs
    i = -1  # for using the index as the name of the transition
    petri_utils.add_arc_from_to(source, transitions[i + 1], net)
    petri_utils.add_arc_from_to(transitions[i + 1], places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 1], transitions[i + 2], net)
    petri_utils.add_arc_from_to(transitions[i + 2], places[i + 2], net)
    petri_utils.add_arc_from_to(places[i + 2], transitions[i + 3], net)
    petri_utils.add_arc_from_to(transitions[i + 3], places[i + 3], net)
    petri_utils.add_arc_from_to(places[i + 3], transitions[i + 4], net)
    petri_utils.add_arc_from_to(transitions[i + 4], places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 2], silent_transitions[i + 1], net)
    petri_utils.add_arc_from_to(silent_transitions[i + 1], places[i + 4], net)
    petri_utils.add_arc_from_to(places[i + 4], transitions[i + 5], net)
    petri_utils.add_arc_from_to(transitions[i + 5], places[i + 5], net)
    petri_utils.add_arc_from_to(places[i + 5], transitions[i + 6], net)
    petri_utils.add_arc_from_to(transitions[i + 6], places[i + 6], net)
    petri_utils.add_arc_from_to(places[i + 6], transitions[i + 8], net)
    petri_utils.add_arc_from_to(silent_transitions[i + 1], places[i + 7], net)
    petri_utils.add_arc_from_to(places[i + 7], transitions[i + 7], net)
    petri_utils.add_arc_from_to(transitions[i + 7], places[i + 8], net)
    petri_utils.add_arc_from_to(places[i + 8], transitions[i + 8], net)
    petri_utils.add_arc_from_to(transitions[i + 8], places[i + 9], net)
    petri_utils.add_arc_from_to(places[i + 9], transitions[i + 9], net)
    petri_utils.add_arc_from_to(transitions[i + 9], places[i + 10], net)
    petri_utils.add_arc_from_to(places[i + 10], transitions[i + 10], net)
    petri_utils.add_arc_from_to(transitions[i + 10], sink_places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 9], transitions[i + 11], net)
    petri_utils.add_arc_from_to(transitions[i + 11], places[i + 11], net)
    petri_utils.add_arc_from_to(places[i + 11], transitions[i + 12], net)
    petri_utils.add_arc_from_to(transitions[i + 12], places[i + 12], net)
    petri_utils.add_arc_from_to(places[i + 12], transitions[i + 13], net)
    petri_utils.add_arc_from_to(transitions[i + 13], places[i + 13], net)
    petri_utils.add_arc_from_to(places[i + 12], transitions[i + 14], net)
    petri_utils.add_arc_from_to(transitions[i + 14], places[i + 13], net)
    petri_utils.add_arc_from_to(places[i + 13], transitions[i + 15], net)
    petri_utils.add_arc_from_to(transitions[i + 15], places[i + 14], net)
    petri_utils.add_arc_from_to(places[i + 14], transitions[i + 16], net)
    petri_utils.add_arc_from_to(transitions[i + 16], places[i + 15], net)
    petri_utils.add_arc_from_to(places[i + 15], transitions[i + 17], net)
    petri_utils.add_arc_from_to(transitions[i + 17], places[i + 16], net)
    petri_utils.add_arc_from_to(places[i + 16], transitions[i + 18], net)
    petri_utils.add_arc_from_to(transitions[i + 18], places[i + 17], net)
    petri_utils.add_arc_from_to(places[i + 17], transitions[i + 19], net)
    petri_utils.add_arc_from_to(transitions[i + 19], sink_places[i + 2], net)
    petri_utils.add_arc_from_to(places[i + 16], transitions[i + 20], net)
    petri_utils.add_arc_from_to(transitions[i + 20], places[i + 18], net)
    petri_utils.add_arc_from_to(places[i + 18], transitions[i + 21], net)
    petri_utils.add_arc_from_to(transitions[i + 21], sink_places[i + 3], net)

    # Adding tokens
    initial_marking = Marking()
    initial_marking[source] = 1
    final_marking = Marking()
    for sp in sink_places:
        final_marking[sp] = 1

    path = 'data/input/models'
    name = 'cp'
    pnml_exporter.apply(net, initial_marking, os.path.join(path, f'{name}.pnml'), final_marking=final_marking)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, os.path.join(path, f'{name}.png'))

    #####################################################################
    # RIO pattern
    #####################################################################
    net = PetriNet("RIO")

    # creating source
    source = PetriNet.Place("source")

    # create sink places (define the number)
    number_of_sink_places = 3
    sink_places = []
    for i in range(number_of_sink_places):
        sink_places.append(PetriNet.Place(f"sink{i + 1}"))

    # create the other places (define the number)
    number_of_places = 18
    places = []
    for i in range(number_of_places):
        places.append(PetriNet.Place(f"p{i + 1}"))

    # add the source, sink and other places to the Petri Net
    net.places.add(source)
    for sp in sink_places:
        net.places.add(sp)
    for p in places:
        net.places.add(p)

    # Create transitions
    transitions = [PetriNet.Transition("t1", "Loan application received"),
                   PetriNet.Transition("t2", "Check application form completeness"),
                   PetriNet.Transition("t3", "Return application back to applicant"),
                   PetriNet.Transition("t4", "Receive updated application"),
                   PetriNet.Transition("t5", "Check credit history"),
                   PetriNet.Transition("t6", "Assess loan risk"),
                   PetriNet.Transition("t7", "Appraise property"),
                   PetriNet.Transition("t8", "Assess eligibility"),
                   PetriNet.Transition("t9", "Reject application"),
                   PetriNet.Transition("t10", "Loan application reject"),
                   PetriNet.Transition("t11", "Prepare acceptance pack"),
                   PetriNet.Transition("t12", "Check if home insurance quote is requested"),
                   PetriNet.Transition("t13", "Send home insurance quote"),
                   PetriNet.Transition("t14", "Prepare acceptance pack"),
                   PetriNet.Transition("t15", "Check if home insurance quote is requested"),
                   PetriNet.Transition("t16", "Send acceptance pack"),
                   PetriNet.Transition("t17", "Verify repayment agreement"),
                   PetriNet.Transition("t18", "Cancel application"),
                   PetriNet.Transition("t19", "Loan application canceled"),
                   PetriNet.Transition("t20", "Approve application"),
                   PetriNet.Transition("t21", "Loan application approved")
                   ]
    # Create silent transitions
    silent_transitions = [PetriNet.Transition("st1", None)]

    # Add the transitions to the Petri Net
    for t in transitions:
        net.transitions.add(t)
    for st in silent_transitions:
        net.transitions.add(st)

    # Add arcs
    i = -1  # for using the index as the name of the transition
    petri_utils.add_arc_from_to(source, transitions[i + 1], net)
    petri_utils.add_arc_from_to(transitions[i + 1], places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 1], transitions[i + 2], net)
    petri_utils.add_arc_from_to(transitions[i + 2], places[i + 2], net)
    petri_utils.add_arc_from_to(places[i + 2], transitions[i + 3], net)
    petri_utils.add_arc_from_to(transitions[i + 3], places[i + 3], net)
    petri_utils.add_arc_from_to(places[i + 3], transitions[i + 4], net)
    petri_utils.add_arc_from_to(transitions[i + 4], places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 2], silent_transitions[i + 1], net)
    petri_utils.add_arc_from_to(silent_transitions[i + 1], places[i + 4], net)
    petri_utils.add_arc_from_to(places[i + 4], transitions[i + 5], net)
    petri_utils.add_arc_from_to(transitions[i + 5], places[i + 5], net)
    petri_utils.add_arc_from_to(places[i + 5], transitions[i + 6], net)
    petri_utils.add_arc_from_to(transitions[i + 6], places[i + 6], net)
    petri_utils.add_arc_from_to(places[i + 6], transitions[i + 8], net)
    petri_utils.add_arc_from_to(silent_transitions[i + 1], places[i + 7], net)
    petri_utils.add_arc_from_to(places[i + 7], transitions[i + 7], net)
    petri_utils.add_arc_from_to(transitions[i + 7], places[i + 8], net)
    petri_utils.add_arc_from_to(places[i + 8], transitions[i + 8], net)
    petri_utils.add_arc_from_to(transitions[i + 8], places[i + 9], net)
    petri_utils.add_arc_from_to(places[i + 9], transitions[i + 9], net)
    petri_utils.add_arc_from_to(transitions[i + 9], places[i + 10], net)
    petri_utils.add_arc_from_to(places[i + 10], transitions[i + 10], net)
    petri_utils.add_arc_from_to(transitions[i + 10], sink_places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 9], transitions[i + 11], net)
    petri_utils.add_arc_from_to(transitions[i + 11], places[i + 11], net)
    petri_utils.add_arc_from_to(places[i + 11], transitions[i + 12], net)
    petri_utils.add_arc_from_to(transitions[i + 12], places[i + 12], net)
    petri_utils.add_arc_from_to(places[i + 12], transitions[i + 13], net)
    petri_utils.add_arc_from_to(transitions[i + 13], places[i + 13], net)
    petri_utils.add_arc_from_to(places[i + 13], transitions[i + 14], net)
    petri_utils.add_arc_from_to(transitions[i + 14], places[i + 14], net)
    petri_utils.add_arc_from_to(places[i + 14], transitions[i + 15], net)
    petri_utils.add_arc_from_to(transitions[i + 15], places[i + 15], net)
    petri_utils.add_arc_from_to(places[i + 12], transitions[i + 16], net)
    petri_utils.add_arc_from_to(transitions[i + 16], places[i + 15], net)
    petri_utils.add_arc_from_to(places[i + 15], transitions[i + 17], net)
    petri_utils.add_arc_from_to(transitions[i + 17], places[i + 16], net)
    petri_utils.add_arc_from_to(places[i + 16], transitions[i + 18], net)
    petri_utils.add_arc_from_to(transitions[i + 18], places[i + 17], net)
    petri_utils.add_arc_from_to(places[i + 17], transitions[i + 19], net)
    petri_utils.add_arc_from_to(transitions[i + 19], sink_places[i + 2], net)
    petri_utils.add_arc_from_to(places[i + 16], transitions[i + 20], net)
    petri_utils.add_arc_from_to(transitions[i + 20], places[i + 18], net)
    petri_utils.add_arc_from_to(places[i + 18], transitions[i + 21], net)
    petri_utils.add_arc_from_to(transitions[i + 21], sink_places[i + 3], net)

    # Adding tokens
    initial_marking = Marking()
    initial_marking[source] = 1
    final_marking = Marking()
    for sp in sink_places:
        final_marking[sp] = 1

    path = 'data/input/models'
    name = 'RIO'
    pnml_exporter.apply(net, initial_marking, os.path.join(path, f'{name}.pnml'), final_marking=final_marking)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, os.path.join(path, f'{name}.png'))

    #####################################################################
    # IRO pattern
    #####################################################################
    net = PetriNet("IRO")

    # creating source
    source = PetriNet.Place("source")

    # create sink places (define the number)
    number_of_sink_places = 3
    sink_places = []
    for i in range(number_of_sink_places):
        sink_places.append(PetriNet.Place(f"sink{i + 1}"))

    # create the other places (define the number)
    number_of_places = 21
    places = []
    for i in range(number_of_places):
        places.append(PetriNet.Place(f"p{i + 1}"))

    # add the source, sink and other places to the Petri Net
    net.places.add(source)
    for sp in sink_places:
        net.places.add(sp)
    for p in places:
        net.places.add(p)

    # Create transitions
    transitions = [PetriNet.Transition("t1", "Loan application received"),
                   PetriNet.Transition("t2", "Check application form completeness"),
                   PetriNet.Transition("t3", "Return application back to applicant"),
                   PetriNet.Transition("t4", "Receive updated application"),
                   PetriNet.Transition("t5", "Check credit history"),
                   PetriNet.Transition("t6", "Assess loan risk"),
                   PetriNet.Transition("t7", "Appraise property"),
                   PetriNet.Transition("t8", "Assess eligibility"),
                   PetriNet.Transition("t9", "Reject application"),
                   PetriNet.Transition("t10", "Loan application reject"),
                   PetriNet.Transition("t11", "Prepare acceptance pack"),
                   PetriNet.Transition("t12", "Check if home insurance quote is requested"),
                   PetriNet.Transition("t13", "Send home insurance quote"),
                   PetriNet.Transition("t14", "Send acceptance pack"),
                   PetriNet.Transition("t15", "Verify repayment agreement"),
                   PetriNet.Transition("t16", "Cancel application"),
                   PetriNet.Transition("t17", "Loan application canceled"),
                   PetriNet.Transition("t18", "Approve application"),
                   PetriNet.Transition("t19", "Verify repayment agreement"),
                   PetriNet.Transition("t20", "Prepare acceptance pack"),
                   PetriNet.Transition("t21", "Added activity"),
                   PetriNet.Transition("t22", "Loan application approved")
                   ]
    # Create silent transitions
    number_of_silent_transitions = 3
    silent_transitions = []
    for i in range(number_of_silent_transitions):
        silent_transitions.append(PetriNet.Transition(f"st{i + 1}", None))

    # Add the transitions to the Petri Net
    for t in transitions:
        net.transitions.add(t)
    for st in silent_transitions:
        net.transitions.add(st)

    # Add arcs
    i = -1  # for using the index as the name of the transition
    petri_utils.add_arc_from_to(source, transitions[i + 1], net)
    petri_utils.add_arc_from_to(transitions[i + 1], places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 1], transitions[i + 2], net)
    petri_utils.add_arc_from_to(transitions[i + 2], places[i + 2], net)
    petri_utils.add_arc_from_to(places[i + 2], transitions[i + 3], net)
    petri_utils.add_arc_from_to(transitions[i + 3], places[i + 3], net)
    petri_utils.add_arc_from_to(places[i + 3], transitions[i + 4], net)
    petri_utils.add_arc_from_to(transitions[i + 4], places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 2], silent_transitions[i + 1], net)
    petri_utils.add_arc_from_to(silent_transitions[i + 1], places[i + 4], net)
    petri_utils.add_arc_from_to(places[i + 4], transitions[i + 5], net)
    petri_utils.add_arc_from_to(transitions[i + 5], places[i + 5], net)
    petri_utils.add_arc_from_to(places[i + 5], transitions[i + 6], net)
    petri_utils.add_arc_from_to(transitions[i + 6], places[i + 6], net)
    petri_utils.add_arc_from_to(places[i + 6], transitions[i + 8], net)
    petri_utils.add_arc_from_to(silent_transitions[i + 1], places[i + 7], net)
    petri_utils.add_arc_from_to(places[i + 7], transitions[i + 7], net)
    petri_utils.add_arc_from_to(transitions[i + 7], places[i + 8], net)
    petri_utils.add_arc_from_to(places[i + 8], transitions[i + 8], net)
    petri_utils.add_arc_from_to(transitions[i + 8], places[i + 9], net)
    petri_utils.add_arc_from_to(places[i + 9], transitions[i + 9], net)
    petri_utils.add_arc_from_to(transitions[i + 9], places[i + 10], net)
    petri_utils.add_arc_from_to(places[i + 10], transitions[i + 10], net)
    petri_utils.add_arc_from_to(transitions[i + 10], sink_places[i + 1], net)
    petri_utils.add_arc_from_to(places[i + 9], transitions[i + 11], net)
    petri_utils.add_arc_from_to(transitions[i + 11], places[i + 11], net)
    petri_utils.add_arc_from_to(places[i + 11], transitions[i + 12], net)
    petri_utils.add_arc_from_to(transitions[i + 12], places[i + 12], net)
    petri_utils.add_arc_from_to(places[i + 12], transitions[i + 13], net)
    petri_utils.add_arc_from_to(transitions[i + 13], places[i + 13], net)
    petri_utils.add_arc_from_to(places[i + 12], transitions[i + 14], net)
    petri_utils.add_arc_from_to(transitions[i + 14], places[i + 13], net)
    petri_utils.add_arc_from_to(places[i + 13], transitions[i + 15], net)
    petri_utils.add_arc_from_to(transitions[i + 15], places[i + 14], net)
    petri_utils.add_arc_from_to(places[i + 14], transitions[i + 16], net)
    petri_utils.add_arc_from_to(transitions[i + 16], places[i + 15], net)
    petri_utils.add_arc_from_to(places[i + 15], transitions[i + 17], net)
    petri_utils.add_arc_from_to(transitions[i + 17], sink_places[i + 2], net)
    petri_utils.add_arc_from_to(places[i + 14], silent_transitions[i + 2], net)
    petri_utils.add_arc_from_to(silent_transitions[i + 2], places[i + 16], net)
    petri_utils.add_arc_from_to(places[i + 16], transitions[i + 18], net)
    petri_utils.add_arc_from_to(transitions[i + 18], places[i + 17], net)
    petri_utils.add_arc_from_to(places[i + 17], transitions[i + 19], net)
    petri_utils.add_arc_from_to(transitions[i + 19], places[i + 18], net)
    petri_utils.add_arc_from_to(places[i + 18], transitions[i + 21], net)
    petri_utils.add_arc_from_to(transitions[i + 18], places[i + 19], net)
    petri_utils.add_arc_from_to(places[i + 19], transitions[i + 20], net)
    petri_utils.add_arc_from_to(transitions[i + 20], places[i + 20], net)
    petri_utils.add_arc_from_to(places[i + 20], transitions[i + 21], net)
    petri_utils.add_arc_from_to(transitions[i + 21], places[i + 21], net)
    petri_utils.add_arc_from_to(places[i + 21], silent_transitions[i + 3], net)
    petri_utils.add_arc_from_to(silent_transitions[i + 3], places[i + 16], net)
    petri_utils.add_arc_from_to(places[i + 21], transitions[i + 22], net)
    petri_utils.add_arc_from_to(transitions[i + 22], sink_places[i + 3], net)

    # Adding tokens
    initial_marking = Marking()
    initial_marking[source] = 1
    final_marking = Marking()
    for sp in sink_places:
        final_marking[sp] = 1

    path = 'data/input/models'
    name = 'IRO'
    pnml_exporter.apply(net, initial_marking, os.path.join(path, f'{name}.pnml'), final_marking=final_marking)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    pn_visualizer.save(gviz, os.path.join(path, f'{name}.png'))


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

    # for extracting the models by applying the Inductive Miner in the
    # event logs available, using the original dataset
    # for l, pt in zip(lognames5000, patterns):
    #     extract_process_models(input_folder, l, pt, 500, 2)

    # read the fixed model cb (I have fixed by editing the .pnml file)
    # and save the petri net for verification
    # get_new_model_cb()

    # create the petri nets for the change patterns
    # not correctly extracted by using the Inductive Miner
    # because the models contain duplicated activities
    create_models_with_duplicated_activities()
