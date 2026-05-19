# Fly-In - Drone Routing Simulation

*This project has been created as part of the 42 curriculum by fshelna.*

## Description

Fly-In is a drone routing simulation system that efficiently navigates multiple drones through a network of connected zones while minimizing total simulation turns. The system implements a time-aware pathfinding algorithm that handles complex constraints including zone capacity limits, restricted zones with multi-turn movement costs, priority zones, and connection capacity constraints.

The project consists of a parser for map file formats, a Dijkstra-based pathfinding algorithm with occupancy tracking, a simulation engine that coordinates multiple drones, and a graphical visualization using the Arcade library.

## Instructions

### Requirements

- Python 3.10 or later
- pip or uv for package management
- Dependencies: `arcade`, `flake8`, `mypy`

### Installation

```bash
# Install dependencies
make install

# Or manually:
pip install arcade flake8 mypy --break-system-packages
```

### Running the Simulation

```bash
# Run with default map
make run

# Run with custom map
python3 main.py maps/your_map.txt

# Clean temporary files
make clean

# Run linting and type checking
make lint
```

### Map File Format

Map files use a simple text format:

```
nb_drones: 5

start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: midpoint 5 5 [zone=restricted color=red max_drones=2]

connection: hub-midpoint
connection: midpoint-goal [max_link_capacity=2]
```

**Zone types:**
- `normal` - Standard zone (1 turn movement cost)
- `restricted` - Dangerous zone (2 turn movement cost, drone occupies the connection link)
- `priority` - Preferred zone (1 turn cost, prioritized by pathfinding algorithm)
- `blocked` - Inaccessible zone

**Metadata options:**
- `zone=<type>` - Zone type (default: normal)
- `color=<name>` - Visual color for rendering
- `max_drones=<n>` - Maximum simultaneous occupancy (default: 1)
- `max_link_capacity=<n>` - Connection capacity limit (default: 1)

### Output Format

The simulation outputs one line per turn, listing only drones that moved:

```
D1-midpoint
D1-goal D2-midpoint
D2-goal
```

Format: `D<ID>-<zone_name>` where ID starts at 1 (D1, D2, D3, etc.)

## Algorithm Design

### Pathfinding Strategy

The implementation uses a modified Dijkstra's algorithm with the following features:

**Time-Aware State Space:**
Each state is represented as `(zone_name, turn)` rather than just a zone, allowing the algorithm to reason about temporal conflicts between drones.

**Occupancy Table:**
A shared occupancy table tracks how many drones occupy each zone and connection link at each turn. This prevents conflicts and enforces capacity constraints.

**Cost Function:**
- Normal zones: cost = 1.0
- Restricted zones: cost = 2.0 (movement takes 2 turns)
- Priority zones: cost = 0.9 (slight preference)
- Waiting in place: cost = 1.0

**Capacity Enforcement:**
- Zone capacity (`max_drones`) is checked before allowing movement or waiting
- Connection capacity (`max_link_capacity`) is enforced for all connections
- Start and end zones have unlimited capacity (special case per spec)

**Sequential Planning:**
Drones are routed one at a time, with each subsequent drone planning around the paths of previously routed drones. This greedy approach is simple and works well for moderate drone counts.

### Complexity Analysis

- **Time Complexity:** O(D × (V + E) log V) where D = number of drones, V = zones, E = connections
- **Space Complexity:** O(D × V × T) where T = maximum simulation turns

For graphs with multiple disjoint paths, drones naturally distribute across available routes. The algorithm doesn't recalculate paths once committed, which saves computation but may miss optimizations that would be possible with global replanning.

### Performance Considerations

The current implementation:
- Uses a priority queue (heapq) for efficient state exploration
- Caches nothing - each drone performs a full search
- Memory grows with occupancy table size (zone-turn pairs)

**Potential optimizations:**
- Path caching for identical subproblems
- Cooperative A* with better heuristics
- Global flow optimization instead of sequential planning

## Visual Representation

The graphical interface displays:
- **Zones** as colored rectangles positioned based on their coordinates
- **Connections** as white lines between zones
- **Drones** as animated circles that move along their planned paths
- **Turn counter** showing current simulation turn
- **Color coding** for zone types and drone identification

Drones animate through the network in real-time, with distinct colors for each drone to track individual movements. The visualization updates at a configurable speed (default: 2 seconds per turn).

Press **SPACE** to restart the simulation from turn 0.

## Resources

### Technical References

- [Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) - Foundation for the pathfinding implementation
- [Time-Expanded Graphs](https://en.wikipedia.org/wiki/Time-expanded_graph) - Theoretical basis for time-aware routing
- [Python Arcade Documentation](https://api.arcade.academy/) - Graphics library for visualization
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/) - Documentation style guide
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/) - Type annotation reference

### AI Usage

AI tools were used for the following tasks:
- **Documentation & docstrings**: Writing comprehensive docstrings following PEP 257 standards for all classes and functions
- **Type hints & mypy compliance**: Adding complete type annotations and ensuring the codebase passes strict mypy type checking

All core algorithmic logic, pathfinding implementation, parser design, and simulation architecture were implemented manually. AI was used purely as a documentation aid and type annotation assistant, not for generating algorithmic or business logic code.

## Project Structure

```
.
├── main.py           # Entry point
├── graph.py          # Graph data structures (Zone, Connection, Graph)
├── parser.py         # Map file parser with validation
├── dijkstra.py       # Pathfinding algorithm
├── drone.py          # Drone data class
├── simulation.py     # Simulation coordinator
├── renderer.py       # Arcade graphical window
├── vars.py           # Color constants
├── Makefile          # Build automation
├── README.md         # This file
```

## Features

### Mandatory
- ✅ Parser with comprehensive error handling
- ✅ Pathfinding with capacity constraints
- ✅ Zone type support (normal, restricted, priority, blocked)
- ✅ Multi-drone coordination via occupancy table
- ✅ Correct output format (D1-zone per spec)
- ✅ Graphical visualization with Arcade
- ✅ Type hints and mypy compliance
- ✅ PEP 257 docstrings
- ✅ flake8 compliance

### Bonus
- Performance benchmarks (see Performance Benchmarks section)
- Command-line map file argument support
- Enhanced visual representation with animated drones

## Performance Benchmarks

Performance targets from the project specification:

### Easy Maps (< 10 turns)
- Linear path with 2 drones: Target ≤ 6 turns
- Simple fork with 3 drones: Target ≤ 6 turns
- Basic capacity with 4 drones: Target ≤ 8 turns

### Medium Maps (10-30 turns)
- Dead end trap with 5 drones: Target ≤ 15 turns
- Circular loop with 6 drones: Target ≤ 20 turns
- Priority puzzle with 4 drones: Target ≤ 12 turns

### Hard Maps (< 60 turns)
- Maze nightmare with 8 drones: Target ≤ 45 turns
- Capacity hell with 12 drones: Target ≤ 60 turns
- Ultimate challenge with 15 drones: Target ≤ 35 turns

### Challenger (Optional)
- The Impossible Dream with 25 drones: Reference record 43 turns

The sequential greedy approach performs well on maps with sufficient capacity and multiple paths, but may struggle on highly constrained maps where global optimization would help.

