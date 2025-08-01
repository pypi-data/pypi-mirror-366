from .output import CTCTrackingHelper
from . import TrackingSource
import networkx as nx

def life_cycle_lineage(tr_source: TrackingSource):

    overlay = tr_source.overlay
    tr_graph = tr_source.tracking_graph

    # compute the life-cycles of individual cells
    life_cycles = CTCTrackingHelper.compute_life_cycles(tr_graph)
    # create lookup (cont id --> life cycle index)
    life_cycle_lookup = CTCTrackingHelper.create_life_cycle_lookup(
        life_cycles
    )
    contour_lookup = {cont.id: cont for cont in overlay}

    lc_graph = nx.DiGraph()

    lc_graph.add_nodes_from(range(len(life_cycles)))

    for i in range(len(life_cycles)):
        lc_graph.nodes[i]["cycle"] = life_cycles[i]

    for lc_id, lc in enumerate(life_cycles):
        start = lc[0]

        parents = tr_graph.predecessors(start)

        for parent in parents:
            parent_lc_id = life_cycle_lookup[parent]
            
            lc_graph.add_edge(parent_lc_id, lc_id)

    for node in lc_graph:
        lc = lc_graph.nodes[node]["cycle"]

        lc_graph.nodes[node]["start_frame"] = contour_lookup[lc[0]].frame
        lc_graph.nodes[node]["end_frame"] = contour_lookup[lc[-1]].frame

    return lc_graph
