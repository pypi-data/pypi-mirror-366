__version__ = "0.0.2"

import asyncio, warnings, copy, time
import logging
from typing import Any, TypeVar, Generic, Iterable
from concurrent.futures import ThreadPoolExecutor

T_Shared = dict[str, Any]
T_Params = dict[str, Any]
T_Action = str | None
T_PrepRes = TypeVar("T_PrepRes")
T_ExecRes = TypeVar("T_ExecRes")

class BaseNode(Generic[T_PrepRes, T_ExecRes]):
    """
    The fundamental building block of a KayGraph graph. A node represents a single
    step in a process, encapsulating logic for preparing data, executing a task,
    and post-processing results.

    Each node can be connected to other nodes to form a graph, defining the graph of
    execution.
    """
    def __init__(self, node_id: str | None = None):
        """Initializes a new instance of a BaseNode."""
        self.node_id = node_id or f"{self.__class__.__name__}_{id(self)}"
        self.params: T_Params = {}
        self.successors: dict[str, "BaseNode"] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._execution_context: dict[str, Any] = {}

    def set_params(self, params: T_Params):
        """
        Sets the parameters for this node. Parameters are typically used for
        configuration or to pass identifiers needed for the node's task.

        Args:
            params: A dictionary of parameters.
        """
        if not isinstance(params, dict):
            raise TypeError(f"Parameters must be a dictionary, got {type(params)}")
        self.params = params.copy()  # Defensive copy

    def get_context(self, key: str, default: Any = None) -> Any:
        """Gets execution context value for this node."""
        return self._execution_context.get(key, default)

    def set_context(self, key: str, value: Any):
        """Sets execution context value for this node."""
        self._execution_context[key] = value

    def before_prep(self, shared: T_Shared):
        """Hook called before prep(). Override for custom pre-processing."""
        pass

    def after_exec(self, shared: T_Shared, prep_res: T_PrepRes, exec_res: T_ExecRes):
        """Hook called after exec() but before post(). Override for custom logic."""
        pass

    def on_error(self, shared: T_Shared, error: Exception) -> bool:
        """Hook called when execution fails. Return True to suppress the error."""
        return False

    def __enter__(self):
        """Context manager entry. Override setup_resources() for custom setup."""
        self.setup_resources()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit. Override cleanup_resources() for custom cleanup."""
        self.cleanup_resources()
        return False

    def setup_resources(self):
        """Override to setup resources when entering context manager."""
        pass

    def cleanup_resources(self):
        """Override to cleanup resources when exiting context manager."""
        pass
    def next(self, node: "BaseNode", action: str = "default") -> "BaseNode":
        """
        Defines the next node in the graph for a given action.

        Args:
            node: The successor node.
            action: The action string that triggers the transition to the successor.
                    Defaults to "default".

        Returns:
            The successor node, allowing for chaining of `next()` calls.
        """
        if action in self.successors:
            warnings.warn(f"Node {self.node_id}: Overwriting successor for action '{action}'. "
                         f"Previous: {self.successors[action].__class__.__name__}, "
                         f"New: {node.__class__.__name__}")
        self.successors[action] = node; return node
    def prep(self, shared: T_Shared) -> T_PrepRes:
        """
        Prepares the data required for the node's execution. This method reads from
        the shared data store. It should not modify the shared store.

        Args:
            shared: The shared data store for the graph.

        Returns:
            The data prepared for the `exec` method.
        """
        pass
    def exec(self, prep_res: T_PrepRes) -> T_ExecRes:
        """
        Executes the core logic of the node. This method should be self-contained
        and rely only on the input from `prep`. It should not access the shared store.

        Args:
            prep_res: The result from the `prep` method.

        Returns:
            The result of the execution.
        """
        pass
    def post(self, shared: T_Shared, prep_res: T_PrepRes, exec_res: T_ExecRes) -> T_Action:
        """
        Post-processes the execution result. This method is responsible for writing
        results back to the shared data store and determining the next action for graph
        control.

        Args:
            shared: The shared data store for the graph.
            prep_res: The result from the `prep` method.
            exec_res: The result from the `exec` method.

        Returns:
            An optional action string that determines which successor node to execute next.
            If None or "default" is returned, the default transition is taken.
        """
        pass
    def _exec(self, prep_res: T_PrepRes) -> T_ExecRes: return self.exec(prep_res)
    def _run(self, shared: T_Shared) -> T_Action:
        self.logger.info(f"Node {self.node_id}: Starting execution with params: {self.params}")
        self.set_context("start_time", time.time())

        try:
            self.before_prep(shared)
            prep_res = self.prep(shared)
            self.logger.debug(f"Node {self.node_id}: prep() returned: {prep_res}")
            exec_res = self._exec(prep_res)
            self.logger.debug(f"Node {self.node_id}: exec() returned: {exec_res}")
            self.after_exec(shared, prep_res, exec_res)
            action = self.post(shared, prep_res, exec_res)

            execution_time = time.time() - self.get_context("start_time", 0)
            self.set_context("last_execution_time", execution_time)
            self.logger.info(f"Node {self.node_id}: Completed in {execution_time:.3f}s with action: '{action}'")
            return action
        except Exception as e:
            execution_time = time.time() - self.get_context("start_time", 0)
            self.logger.error(f"Node {self.node_id}: Failed after {execution_time:.3f}s: {e}")

            if self.on_error(shared, e):
                self.logger.info(f"Node {self.node_id}: Error suppressed by on_error hook")
                return None
            raise
    def run(self, shared: T_Shared) -> T_Action:
        """
        Runs the node's complete lifecycle (prep -> exec -> post) as a standalone execution.

        Note:
            This method does not trigger graph to successors. To run a full graph,
            use `Graph.run()`.

        Args:
            shared: The shared data store.

        Returns:
            The action string returned by the `post` method.
        """
        if self.successors:
            warnings.warn(f"Node {self.node_id}: Has {len(self.successors)} successors but won't execute them. Use Graph for graph execution.")
        return self._run(shared)
    def __rshift__(self, other: "BaseNode") -> "BaseNode":
        """Syntactic sugar for `next(other, "default")`. Allows `>>` operator."""
        return self.next(other)
    def __sub__(self, action: str) -> "_ConditionalTransition":
        """Syntactic sugar for conditional transitions. Allows `node - "action"`."""
        if isinstance(action, str): return _ConditionalTransition(self, action)
        raise TypeError("Action must be a string")

class _ConditionalTransition:
    """A helper class to enable the `node - "action" >> other_node` syntax."""
    def __init__(self, src: BaseNode, action: str): self.src, self.action = src, action
    def __rshift__(self, tgt: BaseNode) -> BaseNode:
        """Completes the conditional transition using the `>>` operator."""
        return self.src.next(tgt, self.action)

class Node(BaseNode[T_PrepRes, T_ExecRes]):
    """
    A standard node with added fault tolerance features like retries and fallbacks.
    """
    def __init__(self, max_retries: int = 1, wait: int = 0, node_id: str | None = None):
        """
        Initializes a new instance of a Node.

        Args:
            max_retries: The maximum number of times to retry the `exec` method upon
                         failure. Defaults to 1 (no retries).
            wait: The number of seconds to wait between retries. Defaults to 0.
            node_id: Optional identifier for this node.
        """
        super().__init__(node_id=node_id)
        self.max_retries,self.wait=max_retries,wait
        self.cur_retry = 0

    def exec_fallback(self, prep_res: T_PrepRes, exc: Exception) -> T_ExecRes:
        """
        A fallback method called when `exec` fails on all retry attempts.
        The default implementation re-raises the exception. Override this to
        provide graceful error handling.

        Args:
            prep_res: The result from the `prep` method.
            exc: The exception that caused the failure.

        Returns:
            A fallback execution result.
        """
        raise exc
    def _exec(self, prep_res: T_PrepRes) -> T_ExecRes:
        for self.cur_retry in range(self.max_retries):
            try:
                if self.cur_retry > 0: self.logger.info(f"Retrying execution (attempt {self.cur_retry + 1}/{self.max_retries})...")
                return self.exec(prep_res)
            except Exception as e:
                self.logger.warning(f"Execution failed on attempt {self.cur_retry + 1}: {e}")
                if self.cur_retry == self.max_retries - 1:
                    self.logger.error("Max retries reached. Calling fallback.")
                    return self.exec_fallback(prep_res, e)
                if self.wait > 0:
                    self.logger.info(f"Waiting for {self.wait} seconds before next retry.")
                    time.sleep(self.wait)
        raise RuntimeError("Execution loop finished unexpectedly.")

class BatchNode(Node):
    """
    A node that processes an iterable of items. The `exec` method is called for
    each item in the iterable returned by `prep`.
    """
    def exec(self, item: Any) -> Any:
        """
        Executes the core logic for a single item from the batch.

        Args:
            item: A single item from the iterable returned by `prep`.

        Returns:
            The result of the execution for the item.
        """
        pass
    def _exec(self, items: Iterable) -> list[Any]:
        return [super(BatchNode,self)._exec(i) for i in (items or [])]

class ParallelBatchNode(BatchNode):
    """
    A `BatchNode` that executes tasks for all items in parallel using a thread pool.
    Ideal for I/O-bound tasks.
    """
    def __init__(self, max_workers: int | None = None, *args, **kwargs):
        """
        Initializes a new instance of ParallelBatchNode.

        Args:
            max_workers: The maximum number of threads to use for parallel execution.
                         If None, it defaults to the number of processors on the
                         machine, multiplied by 5.
        """
        super().__init__(*args, **kwargs)
        self.max_workers = max_workers

    def _exec(self, items: Iterable) -> list[Any]:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(super(BatchNode, self)._exec, items or []))

class Graph(BaseNode):
    """
    Orchestrates the execution of a graph of nodes. A Graph is itself a node,
    allowing for the creation of nested graphs.
    """
    def __init__(self, start: BaseNode | None = None):
        """
        Initializes a new instance of a Graph.

        Args:
            start: The entry point node for the graph.
        """
        super().__init__()
        self.start_node=start
    def start(self, start: BaseNode) -> BaseNode:
        """
        Sets the start node of the graph.

        Args:
            start: The node to start the graph with.

        Returns:
            The start node.
        """
        self.start_node=start; return start
    def get_next_node(self, curr: BaseNode, action: T_Action) -> BaseNode | None:
        """
        Determines the next node to execute based on the current node and the
        last action.

        Args:
            curr: The current node.
            action: The action returned by the current node's `post` method.

        Returns:
            The next node to execute, or None if the graph should end.
        """
        next_node=curr.successors.get(action or "default")
        if not next_node and curr.successors:
            available_actions = list(curr.successors.keys())
            warnings.warn(f"Graph ends: '{action}' not found in {available_actions}", UserWarning)
            self.logger.warning(f"Graph execution terminated: Node {curr.node_id} returned action '{action}' "
                              f"but only has successors for {available_actions}. "
                              f"Graph execution will end here.")
        return next_node
    def _orch(self, shared: T_Shared, params: T_Params | None = None) -> T_Action:
        current_node = copy.copy(self.start_node)
        node_params = params or {**self.params}
        last_action: T_Action = None
        while current_node:
            self.logger.info(f"Graph transition to node: {current_node.node_id} ({current_node.__class__.__name__})")
            current_node.set_params(node_params)
            last_action = current_node._run(shared)
            current_node = copy.copy(self.get_next_node(current_node, last_action))
        self.logger.info(f"Graph {self.node_id}: Execution completed with final action: '{last_action}'")
        return last_action
    def _run(self, shared: T_Shared) -> T_Action:
        prep_res=self.prep(shared); last_action=self._orch(shared); return self.post(shared,prep_res,last_action)
    def post(self, shared: T_Shared, prep_res: Any, exec_res: Any) -> Any: return exec_res

class BatchGraph(Graph):
    """
    A graph that runs its sub-graph multiple times, once for each item of parameters
    returned by its `prep` method. Useful for batch processing of files, data entries, etc.
    """
    def _run(self, shared: T_Shared) -> T_Action:
        prep_results=self.prep(shared) or []
        for params_item in prep_results: self._orch(shared,{**self.params,**params_item})
        return self.post(shared,prep_results,None)

class AsyncNode(Node[T_PrepRes, T_ExecRes]):
    """
    A node designed for asynchronous operations. The `prep`, `exec`, and `post`
    methods are replaced with their `_async` counterparts.
    """
    async def prep_async(self, shared: T_Shared) -> T_PrepRes:
        """Asynchronous version of `prep`."""
        pass
    async def exec_async(self, prep_res: T_PrepRes) -> T_ExecRes:
        """Asynchronous version of `exec`."""
        pass
    async def exec_fallback_async(self, prep_res: T_PrepRes, exc: Exception) -> T_ExecRes:
        """Asynchronous version of `exec_fallback`."""
        raise exc
    async def post_async(self, shared: T_Shared, prep_res: T_PrepRes, exec_res: T_ExecRes) -> T_Action:
        """Asynchronous version of `post`."""
        pass
    async def _exec(self, prep_res: T_PrepRes) -> T_ExecRes:
        for self.cur_retry in range(self.max_retries):
            try:
                if self.cur_retry > 0: self.logger.info(f"Retrying async execution (attempt {self.cur_retry + 1}/{self.max_retries})...")
                return await self.exec_async(prep_res)
            except Exception as e:
                self.logger.warning(f"Async execution failed on attempt {self.cur_retry + 1}: {e}")
                if self.cur_retry == self.max_retries - 1:
                    self.logger.error("Max retries reached. Calling async fallback.")
                    return await self.exec_fallback_async(prep_res, e)
                if self.wait > 0:
                    self.logger.info(f"Waiting for {self.wait} seconds before next async retry.")
                    await asyncio.sleep(self.wait)
        raise RuntimeError("Async execution loop finished unexpectedly.")
    async def run_async(self, shared: T_Shared) -> T_Action:
        """
        Runs the async node's complete lifecycle (prep_async -> exec_async -> post_async)
        as a standalone execution.

        Args:
            shared: The shared data store.

        Returns:
            The action string returned by the `post_async` method.
        """
        if self.successors: warnings.warn("Node won't run successors. Use AsyncGraph.")
        return await self._run_async(shared)
    async def _run_async(self, shared: T_Shared) -> T_Action:
        self.logger.info(f"Running async with params: {self.params}")
        prep_res = await self.prep_async(shared)
        self.logger.debug(f"prep_async() returned: {prep_res}")
        exec_res = await self._exec(prep_res)
        self.logger.debug(f"exec_async() returned: {exec_res}")
        action = await self.post_async(shared, prep_res, exec_res)
        self.logger.info(f"Finished async with action: '{action}'")
        return action
    def _run(self, shared: T_Shared): raise RuntimeError("Use run_async for AsyncNode.")

class AsyncBatchNode(AsyncNode, BatchNode):
    """
    An async node that processes an iterable of items sequentially. `exec_async` is
    awaited for each item.
    """
    async def _exec(self, items: Iterable) -> list[Any]:
        return [await super(AsyncBatchNode,self)._exec(i) for i in items]

class AsyncParallelBatchNode(AsyncNode, BatchNode):
    """
    An async `BatchNode` that executes `exec_async` for all items concurrently using
    `asyncio.gather`. Ideal for I/O-bound tasks that can be run in parallel.
    """
    async def _exec(self, items: Iterable) -> list[Any]:
        return await asyncio.gather(*(super(AsyncParallelBatchNode,self)._exec(i) for i in items))

class AsyncGraph(Graph, AsyncNode):
    """
    A graph that orchestrates asynchronous and synchronous nodes. It can manage
    transitions between `AsyncNode` and regular `Node` instances.
    """
    async def _orch_async(self, shared: T_Shared, params: T_Params | None = None) -> T_Action:
        current_node = copy.copy(self.start_node)
        node_params = params or {**self.params}
        last_action: T_Action = None
        while current_node:
            self.logger.info(f"AsyncGraph transition to node: {current_node.__class__.__name__}")
            current_node.set_params(node_params)
            if isinstance(current_node, AsyncNode):
                last_action = await current_node._run_async(shared)
            else:
                last_action = current_node._run(shared)
            current_node = copy.copy(self.get_next_node(current_node, last_action))
        self.logger.info("AsyncGraph finished.")
        return last_action
    async def _run_async(self, shared: T_Shared) -> T_Action:
        prep_res = await self.prep_async(shared)
        last_action = await self._orch_async(shared)
        return await self.post_async(shared, prep_res, last_action)
    async def post_async(self, shared: T_Shared, prep_res: Any, exec_res: Any) -> Any: return exec_res

class AsyncBatchGraph(AsyncGraph, BatchGraph):
    """
    An `AsyncGraph` that runs its sub-graph multiple times sequentially, once for each
    item of parameters returned by its `prep_async` method.
    """
    async def _run_async(self, shared: T_Shared) -> T_Action:
        prep_results = await self.prep_async(shared) or []
        for params_item in prep_results: await self._orch_async(shared,{**self.params,**params_item})
        return await self.post_async(shared,prep_results,None)

class AsyncParallelBatchGraph(AsyncGraph, BatchGraph):
    """
    An `AsyncGraph` that runs its sub-graph for all parameter sets concurrently
    using `asyncio.gather`.
    """
    async def _run_async(self, shared: T_Shared) -> T_Action:
        prep_results = await self.prep_async(shared) or []
        await asyncio.gather(*(self._orch_async(shared,{**self.params,**params_item}) for params_item in prep_results))
        return await self.post_async(shared,prep_results,None)

class ValidatedNode(Node):
    """
    A node with optional input/output validation capabilities.
    Override validate_input() and validate_output() to add validation logic.
    """
    def validate_input(self, prep_res: T_PrepRes) -> T_PrepRes:
        """Override to add input validation. Return prep_res or raise."""
        return prep_res

    def validate_output(self, exec_res: T_ExecRes) -> T_ExecRes:
        """Override to add output validation. Return exec_res or raise."""
        return exec_res

    def _exec(self, prep_res: T_PrepRes) -> T_ExecRes:
        validated_input = self.validate_input(prep_res)
        result = super()._exec(validated_input)
        return self.validate_output(result)

class MetricsNode(Node):
    """
    A node with optional execution metrics collection.
    Set collect_metrics=True to enable timing and retry tracking.
    """
    def __init__(self, collect_metrics: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collect_metrics = collect_metrics
        self.metrics = {"execution_times": [], "retry_counts": [], "success_count": 0, "error_count": 0}

    def _run(self, shared: T_Shared) -> T_Action:
        if not self.collect_metrics:
            return super()._run(shared)

        start_time = time.time()
        try:
            result = super()._run(shared)
            self.metrics["success_count"] += 1
            return result
        except Exception as e:
            self.metrics["error_count"] += 1
            raise
        finally:
            self.metrics["execution_times"].append(time.time() - start_time)
            self.metrics["retry_counts"].append(getattr(self, 'cur_retry', 0))

    def get_stats(self) -> dict[str, Any]:
        """Returns comprehensive execution statistics."""
        if not self.metrics["execution_times"]:
            return {"status": "no_executions"}

        times = self.metrics["execution_times"]
        return {
            "total_executions": len(times),
            "success_rate": self.metrics["success_count"] / len(times) if times else 0,
            "avg_execution_time": sum(times) / len(times),
            "min_execution_time": min(times),
            "max_execution_time": max(times),
            "total_retries": sum(self.metrics["retry_counts"])
        }
