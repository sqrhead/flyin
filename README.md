

# flyin

## external modules
- arcade (graphic library)

## to learn
- graph adjacency list
- dijkstra
- multi agent pathfinding, *time-expanded graph pathfinding, cooperative pathfinding for agents
- max flow min cut algo, ford-fulkerson algo
-- code patterns:
---- strategy for swapping pathfinding algo
---- chain of responsability
---- builder for graph construction

# End this shit in the next 7 days

# Resources
-  Regex
-- https://regexone.com/

###########################
import re

class DroneMapParser:
    def __init__(self):
        self.map_data = {"nb_drones": None, "hubs": {}, "connections": []}
        self.line_count = 0
        
        # Regex patterns for different line types
        self.HUB_PATTERN = re.compile(r'^(?P<kind>start_hub|end_hub|hub)\s*:\s*(?P<name>\S+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)(?:\s+\[(?P<meta>.*)\])?')
        self.CONN_PATTERN = re.compile(r'^connection\s*:\s*(?P<src>\S+)-(?P<dst>\S+)(?:\s+\[(?P<meta>.*)\])?')

    def _parse_meta(self, meta_str):
        if not meta_str: return {}
        # Constraints: Metadata must be syntactically valid 
        attrs = {k: v for k, v in re.findall(r'(\w+)=([\w-]+)', meta_str)}
        
        # Constraints: Capacity values must be positive integers 
        if 'max_drones' in attrs:
            attrs['max_drones'] = int(attrs['max_drones'])
            if attrs['max_drones'] < 1:
                raise ValueError(f"max_drones must be positive")
        return attrs

    def parse_line(self, line):
        self.line_count += 1
        # Strip comments and external source markers [cite: 1, 2, 3]
        line = re.sub(r'\', '', line).split('#')[0].strip()
        if not line: return

        # Rule: First line must define number of drones 
        if self.map_data["nb_drones"] is None:
            if not line.startswith("nb_drones"):
                raise SyntaxError(f"Line {self.line_count}: Expected 'nb_drones' as first definition")
            self.map_data["nb_drones"] = int(line.split(':')[1].strip())
            return

        # Handle Hubs
        hub_match = self.HUB_PATTERN.match(line)
        if hub_match:
            data = hub_match.groupdict()
            name = data['name']
            if name in self.map_data["hubs"]:
                raise SyntaxError(f"Line {self.line_count}: Hub '{name}' already defined")
            
            self.map_data["hubs"][name] = {
                "type": data['kind'],
                "coords": (int(data['x']), int(data['y'])),
                "meta": self._parse_meta(data['meta'])
            }
            return

        # Handle Connections
        conn_match = self.CONN_PATTERN.match(line)
        if conn_match:
            src, dst = conn_match.group('src'), conn_match.group('dst')
            # Rule: Connections must link only previous declared zones 
            if src not in self.map_data["hubs"] or dst not in self.map_data["hubs"]:
                raise SyntaxError(f"Line {self.line_count}: Reference to undefined hub in connection {src}-{dst}")
            
            self.map_data["connections"].append({"from": src, "to": dst, "meta": self._parse_meta(conn_match.group('meta'))})
            return

        raise SyntaxError(f"Line {self.line_count}: Unrecognized syntax")

    def validate_final(self):
        # Final Constraint: One start hub and one end hub 
        hub_types = [h['type'] for h in self.map_data["hubs"].values()]
        if hub_types.count('start_hub') != 1 or hub_types.count('end_hub') != 1:
            raise SyntaxError("Map must contain exactly one start_hub and one end_hub")
