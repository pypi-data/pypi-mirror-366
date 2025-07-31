---
layout: default
title: "Graph"
parent: "Fundamentals"
nav_order: 2
---

# Graph

A **Graph** orchestrates a graph of Nodes. You can chain Nodes in a sequence or create branching depending on the **Actions** returned from each Node's `post()`.

## 1. Action-based Transitions

Each Node's `post()` returns an **Action** string. By default, if `post()` doesn't return anything, we treat that as `"default"`.

You define transitions with the syntax:

1. **Basic default transition**: `node_a >> node_b`
  This means if `node_a.post()` returns `"default"`, go to `node_b`.
  (Equivalent to `node_a - "default" >> node_b`)

2. **Named action transition**: `node_a - "action_name" >> node_b`
  This means if `node_a.post()` returns `"action_name"`, go to `node_b`.

It's possible to create loops, branching, or multi-step graphs.

## 2. Creating a Graph

A **Graph** begins with a **start** node. You call `Graph(start=some_node)` to specify the entry point. When you call `graph.run(shared)`, it executes the start node, looks at its returned Action from `post()`, follows the transition, and continues until there's no next node.

### Example: Simple Sequence

Here's a minimal graph of two nodes in a chain:

```python
node_a >> node_b
graph = Graph(start=node_a)
graph.run(shared)
```

- When you run the graph, it executes `node_a`.
- Suppose `node_a.post()` returns `"default"`.
- The graph then sees `"default"` Action is linked to `node_b` and runs `node_b`.
- `node_b.post()` returns `"default"` but we didn't define `node_b >> something_else`. So the graph ends there.

### Example: Branching & Looping

Here's a simple expense approval graph that demonstrates branching and looping. The `ReviewExpense` node can return three possible Actions:

- `"approved"`: expense is approved, move to payment processing
- `"needs_revision"`: expense needs changes, send back for revision
- `"rejected"`: expense is denied, finish the process

We can wire them like this:

```python
# Define the graph connections
review - "approved" >> payment        # If approved, process payment
review - "needs_revision" >> revise   # If needs changes, go to revision
review - "rejected" >> finish         # If rejected, finish the process

revise >> review   # After revision, go back for another review
payment >> finish  # After payment, finish the process

graph = Graph(start=review)
```

Let's see how it works:

1. If `review.post()` returns `"approved"`, the expense moves to the `payment` node
2. If `review.post()` returns `"needs_revision"`, it goes to the `revise` node, which then loops back to `review`
3. If `review.post()` returns `"rejected"`, it moves to the `finish` node and stops

```mermaid
graph TD
    review[Review Expense] -->|approved| payment[Process Payment]
    review -->|needs_revision| revise[Revise Report]
    review -->|rejected| finish[Finish Process]

    revise --> review
    payment --> finish
```

### Running Individual Nodes vs. Running a Graph

- `node.run(shared)`: Just runs that node alone (calls `prep->exec->post()`), returns an Action.
- `graph.run(shared)`: Executes from the start node, follows Actions to the next node, and so on until the graph can't continue.

> `node.run(shared)` **does not** proceed to the successor.
> This is mainly for debugging or testing a single node.
>
> Always use `graph.run(...)` in production to ensure the full pipeline runs correctly.
{: .warning }

## 3. Nested Graphs

A **Graph** can act like a Node, which enables powerful composition patterns. This means you can:

1. Use a Graph as a Node within another Graph's transitions.
2. Combine multiple smaller Graphs into a larger Graph for reuse.
3. Node `params` will be a merging of **all** parents' `params`.

### Graph's Node Methods

A **Graph** is also a **Node**, so it will run `prep()` and `post()`. However:

- It **won't** run `exec()`, as its main logic is to orchestrate its nodes.
- `post()` always receives `None` for `exec_res` and should instead get the graph execution results from the shared store.

### Basic Graph Nesting

Here's how to connect a graph to another node:

```python
# Create a sub-graph
node_a >> node_b
subgraph = Graph(start=node_a)

# Connect it to another node
subgraph >> node_c

# Create the parent graph
parent_graph = Graph(start=subgraph)
```

When `parent_graph.run()` executes:
1. It starts `subgraph`
2. `subgraph` runs through its nodes (`node_a->node_b`)
3. After `subgraph` completes, execution continues to `node_c`

### Example: Order Processing Pipeline

Here's a practical example that breaks down order processing into nested graphs:

```python
# Payment processing sub-graph
validate_payment >> process_payment >> payment_confirmation
payment_graph = Graph(start=validate_payment)

# Inventory sub-graph
check_stock >> reserve_items >> update_inventory
inventory_graph = Graph(start=check_stock)

# Shipping sub-graph
create_label >> assign_carrier >> schedule_pickup
shipping_graph = Graph(start=create_label)

# Connect the graphs into a main order pipeline
payment_graph >> inventory_graph >> shipping_graph

# Create the master graph
order_graph_graph = Graph(start=payment_graph)

# Run the entire pipeline
order_graph_graph.run(shared_data)
```

This creates a clean separation of concerns while maintaining a clear execution path:

```mermaid
graph LR
    subgraph order_graph_graph[Order Pipeline]
        subgraph paymentGraph["Payment Graph"]
            A[Validate Payment] --> B[Process Payment] --> C[Payment Confirmation]
        end

        subgraph inventoryGraph["Inventory Graph"]
            D[Check Stock] --> E[Reserve Items] --> F[Update Inventory]
        end

        subgraph shippingGraph["Shipping Graph"]
            G[Create Label] --> H[Assign Carrier] --> I[Schedule Pickup]
        end

        paymentGraph --> inventoryGraph
        inventoryGraph --> shippingGraph
    end
```

## 4. Enhanced Graph Features

### Graph Orchestration with Logging

KayGraph provides comprehensive logging for graph execution with detailed node transitions:

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create nodes with IDs for better tracking
review = ReviewExpense(node_id="expense_review")
payment = ProcessPayment(node_id="payment_processor") 
finish = FinishProcess(node_id="process_finalizer")

# Set up transitions
review - "approved" >> payment
payment >> finish

# Create graph with proper identification
expense_graph = Graph(start=review)
expense_graph.node_id = "expense_approval_graph"

# Run with automatic logging
result = expense_graph.run(shared)
```

**Sample Graph Log Output:**
```
2024-01-01 10:00:00 - Graph - INFO - Graph expense_approval_graph: Starting execution
2024-01-01 10:00:00 - Graph - INFO - Graph transition to node: expense_review (ReviewExpense)
2024-01-01 10:00:01 - ReviewExpense - INFO - Node expense_review: Starting execution with params: {}
2024-01-01 10:00:02 - ReviewExpense - INFO - Node expense_review: Completed in 1.250s with action: 'approved'
2024-01-01 10:00:02 - Graph - INFO - Graph transition to node: payment_processor (ProcessPayment)
2024-01-01 10:00:03 - ProcessPayment - INFO - Node payment_processor: Completed in 0.980s with action: 'default'
2024-01-01 10:00:03 - Graph - INFO - Graph expense_approval_graph: Execution completed with final action: 'default'
```

### Advanced Error Handling

KayGraph graphs provide enhanced error reporting with context about where failures occur:

```python
class RobustGraph(Graph):
    def get_next_node(self, curr, action):
        """Enhanced error reporting for missing transitions"""
        next_node = super().get_next_node(curr, action)
        
        if not next_node and curr.successors:
            # KayGraph automatically logs detailed error info
            available_actions = list(curr.successors.keys())
            self.logger.warning(
                f"Graph execution terminated: Node {curr.node_id} returned action '{action}' "
                f"but only has successors for {available_actions}. "
                f"Graph execution will end here."
            )
        
        return next_node
```

### Context Manager Support

Graphs support context managers for resource management across the entire execution:

```python
class DatabaseGraph(Graph):
    def setup_resources(self):
        """Setup graph-level resources"""
        self.connection_pool = create_database_pool()
        self.logger.info("Database connection pool created")
    
    def cleanup_resources(self):
        """Cleanup graph-level resources"""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.close()
            self.logger.info("Database connection pool closed")

# Usage with automatic resource management
with DatabaseGraph(start=data_node) as graph:
    result = graph.run(shared)  # Resources managed automatically
```
