"""Fixed, transparent offline walkthrough. No AI/image analysis is simulated."""

QUESTION = "Explain breadth-first search for this graph. Start at A and visit neighbours alphabetically."
EXPLANATION = """### What the sample shows
An undirected graph with edges **A–B, A–C, B–D, B–E, C–F**.

### The idea
Breadth-first search (BFS) visits nearby vertices first. A **queue** remembers which vertex to explore next: first in, first out.

### Walk through it
| Remove from queue | Add unvisited neighbours | Queue afterwards |
|---|---|---|
| A | B, C | B, C |
| B | D, E | C, D, E |
| C | F | D, E, F |
| D | None | E, F |
| E | None | F |
| F | None | Empty |

The visit order is **A → B → C → D → E → F**. Mark each vertex visited when you add it to the queue so that cycles cannot cause repeated work.

### Remember
With an adjacency list, BFS takes **O(V + E)** time and **O(V)** extra space. It finds shortest paths by edge count in an **unweighted** graph.

**Quick check:** Why should you mark a vertex when it is enqueued, instead of waiting until it is removed?
"""
HINT = """### One hint
Start with A in a queue. Remove A, then add its unvisited neighbours B and C in alphabetical order.

**Your turn:** Which vertex leaves the queue next? What will the queue contain after you add that vertex's unvisited neighbours?
"""
PRACTICE = """### Test yourself
1. Which data structure gives BFS its level-by-level behaviour?
2. In the sample graph, how many edges are in the shortest path from A to E?
3. Does ordinary BFS guarantee the least-cost path when edges have different weights?

### Answer key
1. A FIFO queue.
2. Two edges: A → B → E.
3. No. Its shortest-path guarantee applies to unweighted graphs (or equal edge weights).
"""
PACK = """## Breadth-first search
### Key concepts
- Explore an unweighted graph one level at a time using a FIFO queue.
- Mark nodes visited on enqueue to avoid duplicates.
- With adjacency lists: O(V + E) time; O(V) additional space.

### Worked example
Edges: A–B, A–C, B–D, B–E, C–F. From A with alphabetical neighbours, BFS visits A, B, C, D, E, F. The shortest route from A to E is A → B → E (two edges).

### Common mistakes
- Using a stack instead of a queue.
- Forgetting the visited set when the graph contains cycles.
- Claiming BFS finds the cheapest route with unequal edge weights.

### Recall questions
1. What does FIFO mean?
2. What is the queue after removing B in this example?
3. What extra step visits a disconnected graph fully?

### Answer key
1. First in, first out.
2. C, D, E.
3. Start BFS again from each still-unvisited vertex.

### Unresolved questions
None in this fixed example. Try implementing BFS using collections.deque next.
"""
