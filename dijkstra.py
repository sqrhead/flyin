import heapq

from graph import Graph, ZoneType

class Dijkstra:

    def __init__(self):
        self._count: int = 0

    def path(self, graph: Graph, table: dict) -> list[tuple[any, int]]:
        start = graph.get_start()
        end = graph.get_end()

        pq = [(0.0, self._count, start.name, 0, [(start, 0)])]
        visited: dict[tuple[str, int], float] = {} 

        while pq:
            cost, _, name, turn, schedule = heapq.heappop(pq)

            if name == end.name:
                return schedule
            if visited.get((name, turn), float('inf')) <= cost:
                continue
            visited[(name, turn)] = cost

            zone = graph.get_zone_by_name(name)
            if table.get((name, turn + 1), 0) < zone.max_drones:
                self._count += 1
                heapq.heappush(pq, (cost + 1.0, self._count, name, turn + 1, schedule + [(zone, turn + 1)]))
            
            for conn in graph.get_current_connections(zone):
                adj = graph.get_zone_by_name(conn.zone_b)
                if adj.zone_type == ZoneType.BLOCKED: continue

                is_restricted = (adj.zone_type == ZoneType.RESTRICTED)
                move_cost = 2 if is_restricted else 1
                arrival_turn = turn + move_cost

                if table.get((adj.name, arrival_turn), 0) < adj.max_drones:
                    new_schedule = list(schedule)
                    if is_restricted:
                        link_id = f"{name}-{adj.name}"
                        if table.get((link_id, turn + 1), 0) >= conn.max_link_capacity:
                            continue
                        new_schedule.append((link_id, turn + 1))
                    new_schedule.append((adj, arrival_turn))

                    weight = 0.9 if adj.zone_type == ZoneType.PRIORITY else float(move_cost)
                    self._count += 1
                    heapq.heappush(pq, (cost + weight, self._count, adj.name, arrival_turn, new_schedule))

        return []