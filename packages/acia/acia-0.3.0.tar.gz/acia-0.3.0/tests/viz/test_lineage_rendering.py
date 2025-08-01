"""Module for testing visualization module for lineage rendering"""

import unittest
import networkx as nx

from acia.viz import hierarchy_pos_loop_multi, plot_lineage_tree

# Example usage (using previous forest creation and layout code)
def build_forest_example():
    G = nx.DiGraph()
    G.add_edge('A0', 'A1')
    G.add_edge('A1', 'A2')
    G.add_edge('A2', 'A3')
    G.add_edge('B0', 'B1')
    G.add_edge('B0', 'B2')
    G.add_edge('B1', 'B3')
    G.add_edge('B1', 'B4')
    G.add_edge('C0', 'C1')
    G.add_edge('C0', 'C2')
    G.add_edge('C0', 'C3')
    G.add_edge('C3', 'C4')
    G.add_edge('C4', 'C5')

    # Add y property (demo: last character as integer)
    for node in G.nodes():
        try:
            G.nodes[node]['y'] = int(node[-1])
        except:
            G.nodes[node]['y'] = 0
    return G


class TestLineageRendering(unittest.TestCase):
    """Testing scalebar and time overlay"""

    def test_formatting(self):
        # Build and plot the forest
        G = build_forest_example()
        roots = [n for n, d in G.in_degree() if d == 0]
        pos = hierarchy_pos_loop_multi(G, roots)
        plot_lineage_tree(G, pos, mode='vertical', draw_labels=True, title="Vertical with labels", y_attr="y")
        plot_lineage_tree(G, pos, mode='vertical', flip_vertical=True, draw_labels=True, title="Vertical with labels (flipped)")
        plot_lineage_tree(G, pos, mode='horizontal', draw_labels=True, title="Horizontal with labels")
        plot_lineage_tree(G, pos, mode='horizontal', flip_horizontal=True, draw_labels=True, title="Horizontal flipped with labels")

    def test_imbalance(self):
        # --- Build the imbalanced forest ---
        G = nx.DiGraph()
        # First tree: chain
        G.add_edge('R1', 'R1-1')
        G.add_edge('R1-1', 'R1-2')
        # Second tree: branch
        G.add_edge('R2', 'R2-1')
        G.add_edge('R2', 'R2-2')
        # Set custom timepoints
        G.nodes['R1']['y'] = 0
        G.nodes['R1-1']['y'] = 1
        G.nodes['R1-2']['y'] = 2
        G.nodes['R2']['y'] = 2
        G.nodes['R2-1']['y'] = 3
        G.nodes['R2-2']['y'] = 3

        roots = [n for n, d in G.in_degree() if d == 0]
        pos = hierarchy_pos_loop_multi(G, roots)
        plot_lineage_tree(
            G, pos, mode='vertical', draw_labels=True,
            title="Imbalanced forest with multiple roots at different y", y_attr='y'
        )



if __name__ == "__main__":
    unittest.main()
