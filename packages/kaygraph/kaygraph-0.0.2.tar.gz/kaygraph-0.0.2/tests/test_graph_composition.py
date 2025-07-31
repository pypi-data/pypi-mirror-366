# tests/test_graph_composition.py
import unittest
import asyncio # Keep import, might be needed if other tests use it indirectly
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from kaygraph import Node, Graph

# --- Existing Nodes ---
class NumberNode(Node):
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] = self.number
    # post implicitly returns None

class AddNode(Node):
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] += self.number
    # post implicitly returns None

class MultiplyNode(Node):
    def __init__(self, number):
        super().__init__()
        self.number = number
    def prep(self, shared_storage):
        shared_storage['current'] *= self.number
    # post implicitly returns None

# --- New Nodes for Action Propagation Test ---
class SignalNode(Node):
    """A node that returns a specific signal string from its post method."""
    def __init__(self, signal="default_signal"):
        super().__init__()
        self.signal = signal
    # No prep needed usually if just signaling
    def post(self, shared_storage, prep_result, exec_result):
        # Store the signal in shared storage for verification
        shared_storage['last_signal_emitted'] = self.signal
        return self.signal # Return the specific action string

class PathNode(Node):
    """A node to indicate which path was taken in the outer graph."""
    def __init__(self, path_id):
        super().__init__()
        self.path_id = path_id
    def prep(self, shared_storage):
        shared_storage['path_taken'] = self.path_id
    # post implicitly returns None

# --- Test Class ---
class TestGraphComposition(unittest.TestCase):

    # --- Existing Tests (Unchanged) ---
    def test_graph_as_node(self):
        """
        1) Create a Graph (f1) starting with NumberNode(5), then AddNode(10), then MultiplyNode(2).
        2) Create a second Graph (f2) whose start is f1.
        3) Create a wrapper Graph (f3) that contains f2 to ensure proper execution.
        Expected final result in shared_storage['current']: (5 + 10) * 2 = 30.
        """
        shared_storage = {}
        f1 = Graph(start=NumberNode(5))
        f1 >> AddNode(10) >> MultiplyNode(2)
        f2 = Graph(start=f1)
        f3 = Graph(start=f2)
        f3.run(shared_storage)
        self.assertEqual(shared_storage['current'], 30)

    def test_nested_graph(self):
        """
        Demonstrates nested graphs with proper wrapping:
        inner_graph: NumberNode(5) -> AddNode(3)
        middle_graph: starts with inner_graph -> MultiplyNode(4)
        wrapper_graph: contains middle_graph to ensure proper execution
        Expected final result: (5 + 3) * 4 = 32.
        """
        shared_storage = {}
        inner_graph = Graph(start=NumberNode(5))
        inner_graph >> AddNode(3)
        middle_graph = Graph(start=inner_graph)
        middle_graph >> MultiplyNode(4)
        wrapper_graph = Graph(start=middle_graph)
        wrapper_graph.run(shared_storage)
        self.assertEqual(shared_storage['current'], 32)

    def test_graph_chaining_graphs(self):
        """
        Demonstrates chaining two graphs with proper wrapping:
        graph1: NumberNode(10) -> AddNode(10) # final = 20
        graph2: MultiplyNode(2) # final = 40
        wrapper_graph: contains both graph1 and graph2 to ensure proper execution
        Expected final result: (10 + 10) * 2 = 40.
        """
        shared_storage = {}
        numbernode = NumberNode(10)
        numbernode >> AddNode(10)
        graph1 = Graph(start=numbernode)
        graph2 = Graph(start=MultiplyNode(2))
        graph1 >> graph2 # Default transition based on graph1 returning None
        wrapper_graph = Graph(start=graph1)
        wrapper_graph.run(shared_storage)
        self.assertEqual(shared_storage['current'], 40)

    def test_composition_with_action_propagation(self):
        """
        Test that an outer graph can branch based on the action returned
        by the last node's post() within an inner graph.
        """
        shared_storage = {}

        # 1. Define an inner graph that ends with a node returning a specific action
        inner_start_node = NumberNode(100)       # current = 100, post -> None
        inner_end_node = SignalNode("inner_done") # post -> "inner_done"
        inner_start_node >> inner_end_node
        # Inner graph will execute start->end, and the Graph's execution will return "inner_done"
        inner_graph = Graph(start=inner_start_node)

        # 2. Define target nodes for the outer graph branches
        path_a_node = PathNode("A") # post -> None
        path_b_node = PathNode("B") # post -> None

        # 3. Define the outer graph starting with the inner graph
        outer_graph = Graph()
        outer_graph.start(inner_graph) # Use the start() method

        # 4. Define branches FROM the inner_graph object based on its returned action
        inner_graph - "inner_done" >> path_b_node  # This path should be taken
        inner_graph - "other_action" >> path_a_node # This path should NOT be taken

        # 5. Run the outer graph and capture the last action
        # Execution: inner_start -> inner_end -> path_b
        last_action_outer = outer_graph.run(shared_storage)

        # 6. Assert the results
        # Check state after inner graph execution
        self.assertEqual(shared_storage.get('current'), 100)
        self.assertEqual(shared_storage.get('last_signal_emitted'), "inner_done")
        # Check that the correct outer path was taken
        self.assertEqual(shared_storage.get('path_taken'), "B")
        # Check the action returned by the outer graph. The last node executed was
        # path_b_node, which returns None from its post method.
        self.assertIsNone(last_action_outer)

if __name__ == '__main__':
    unittest.main()
