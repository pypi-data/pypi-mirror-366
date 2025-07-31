# KayGraph Hello World

The simplest possible KayGraph application to get you started.

## What it does

- Creates two nodes: HelloNode and GoodbyeNode
- Connects them in sequence
- Demonstrates basic shared state usage
- Shows how data flows through the graph

## How to run

```bash
python main.py
```

## Key Concepts

1. **Node Creation**: Inherit from `Node` class
2. **Three Methods**: 
   - `prep()`: Read from shared state
   - `exec()`: Process data
   - `post()`: Write to shared state
3. **Graph Connection**: Use `>>` operator
4. **Shared State**: Dictionary passed through nodes

## Output

```
KayGraph Hello World
==============================

Running for: World
--------------------
Hello, World!
Goodbye, World! Have a great day!
Final state: {'name': 'World', 'greeting': 'Hello, World!', 'farewell': 'Goodbye, World! Have a great day!'}
```

Perfect starting point for learning KayGraph!