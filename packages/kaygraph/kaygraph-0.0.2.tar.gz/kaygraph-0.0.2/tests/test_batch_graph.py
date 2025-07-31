import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from kaygraph import Node, BatchGraph, Graph

class DataProcessNode(Node):
    def prep(self, shared_storage):
        key = self.params.get('key')
        data = shared_storage['input_data'][key]
        if 'results' not in shared_storage:
            shared_storage['results'] = {}
        shared_storage['results'][key] = data * 2

class ErrorProcessNode(Node):
    def prep(self, shared_storage):
        key = self.params.get('key')
        if key == 'error_key':
            raise ValueError(f"Error processing key: {key}")
        if 'results' not in shared_storage:
            shared_storage['results'] = {}
        shared_storage['results'][key] = True

class TestBatchGraph(unittest.TestCase):
    def setUp(self):
        self.process_node = DataProcessNode()

    def test_basic_batch_processing(self):
        """Test basic batch processing with multiple keys"""
        class SimpleTestBatchGraph(BatchGraph):
            def prep(self, shared_storage):
                return [{'key': k} for k in shared_storage['input_data'].keys()]

        shared_storage = {
            'input_data': {
                'a': 1,
                'b': 2,
                'c': 3
            }
        }

        graph = SimpleTestBatchGraph(start=self.process_node)
        graph.run(shared_storage)

        expected_results = {
            'a': 2,
            'b': 4,
            'c': 6
        }
        self.assertEqual(shared_storage['results'], expected_results)

    def test_empty_input(self):
        """Test batch processing with empty input dictionary"""
        class EmptyTestBatchGraph(BatchGraph):
            def prep(self, shared_storage):
                return [{'key': k} for k in shared_storage['input_data'].keys()]

        shared_storage = {
            'input_data': {}
        }

        graph = EmptyTestBatchGraph(start=self.process_node)
        graph.run(shared_storage)

        self.assertEqual(shared_storage.get('results', {}), {})

    def test_single_item(self):
        """Test batch processing with single item"""
        class SingleItemBatchGraph(BatchGraph):
            def prep(self, shared_storage):
                return [{'key': k} for k in shared_storage['input_data'].keys()]

        shared_storage = {
            'input_data': {
                'single': 5
            }
        }

        graph = SingleItemBatchGraph(start=self.process_node)
        graph.run(shared_storage)

        expected_results = {
            'single': 10
        }
        self.assertEqual(shared_storage['results'], expected_results)

    def test_error_handling(self):
        """Test error handling during batch processing"""
        class ErrorTestBatchGraph(BatchGraph):
            def prep(self, shared_storage):
                return [{'key': k} for k in shared_storage['input_data'].keys()]

        shared_storage = {
            'input_data': {
                'normal_key': 1,
                'error_key': 2,
                'another_key': 3
            }
        }

        graph = ErrorTestBatchGraph(start=ErrorProcessNode())

        with self.assertRaises(ValueError):
            graph.run(shared_storage)

    def test_nested_graph(self):
        """Test batch processing with nested graphs"""
        class InnerNode(Node):
            def exec(self, prep_result):
                key = self.params.get('key')
                if 'intermediate_results' not in shared_storage:
                    shared_storage['intermediate_results'] = {}
                shared_storage['intermediate_results'][key] = shared_storage['input_data'][key] + 1

        class OuterNode(Node):
            def exec(self, prep_result):
                key = self.params.get('key')
                if 'results' not in shared_storage:
                    shared_storage['results'] = {}
                shared_storage['results'][key] = shared_storage['intermediate_results'][key] * 2

        class NestedBatchGraph(BatchGraph):
            def prep(self, shared_storage):
                return [{'key': k} for k in shared_storage['input_data'].keys()]

        # Create inner graph
        inner_node = InnerNode()
        outer_node = OuterNode()
        inner_node >> outer_node

        shared_storage = {
            'input_data': {
                'x': 1,
                'y': 2
            }
        }

        graph = NestedBatchGraph(start=inner_node)
        graph.run(shared_storage)

        expected_results = {
            'x': 4,  # (1 + 1) * 2
            'y': 6   # (2 + 1) * 2
        }
        self.assertEqual(shared_storage['results'], expected_results)

    def test_custom_parameters(self):
        """Test batch processing with additional custom parameters"""
        class CustomParamNode(Node):
            def exec(self, prep_result):
                key = self.params.get('key')
                multiplier = self.params.get('multiplier', 1)
                if 'results' not in shared_storage:
                    shared_storage['results'] = {}
                shared_storage['results'][key] = shared_storage['input_data'][key] * multiplier

        class CustomParamBatchGraph(BatchGraph):
            def prep(self, shared_storage):
                return [{
                    'key': k,
                    'multiplier': i + 1
                } for i, k in enumerate(shared_storage['input_data'].keys())]

        shared_storage = {
            'input_data': {
                'a': 1,
                'b': 2,
                'c': 3
            }
        }

        graph = CustomParamBatchGraph(start=CustomParamNode())
        graph.run(shared_storage)

        expected_results = {
            'a': 1 * 1,  # first item, multiplier = 1
            'b': 2 * 2,  # second item, multiplier = 2
            'c': 3 * 3   # third item, multiplier = 3
        }
        self.assertEqual(shared_storage['results'], expected_results)

if __name__ == '__main__':
    unittest.main()
