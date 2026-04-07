from graph import Graph, Connection, Zone, ZoneType
import heapq

class Dijkstra:

    def __init__(self):
        self._count: int = 0


    # start, end custom from drone position
    def path(self, graph: Graph) -> list[Zone]:
        start = graph.get_start()
        end = graph.get_end()

        pq = [(0, self._count, start.name, [start])]
        visited = {} # name - cost

        while pq:
            current_cost, _,  current_name,path = heapq.heappop(pq)

            if current_name == end.name:
                return path

            if current_name in visited and visited[current_name] <= current_cost:
                continue
            visited[current_name] = current_cost

            current_zone = graph.get_zone_by_name(current_name)
            for conn in graph.get_current_connections(current_zone):
                adj = graph.get_zone_by_name(conn.zone_b)

                cost_enter = 0
                match adj.zone_type:
                    case ZoneType.BLOCKED:
                        continue
                    case ZoneType.PRIORITY:
                        if len(adj.drones) < adj.max_drones:
                            cost_enter = 1
                    case ZoneType.RESTRICTED:
                        cost_enter = 2
                    case _:
                        cost_enter = 1
                new_cost = current_cost + cost_enter
                self._count += 1
                heapq.heappush(pq, (new_cost, self._count,  adj.name, path + [adj]))
        return []