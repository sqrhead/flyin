import heapq
from typing import Any

from graph import Graph, Zone, ZoneType


class Dijkstra:

    def __init__(self) -> None:
        """Initialize the Dijkstra scheduler."""
        self._count: int = 0

    def path(
        self,
        graph: Graph,
        table: dict[tuple[str, int], int]
    ) -> list[tuple[Any, int]]:
        """Compute the optimal schedule for a single drone.

        Args:
            graph: The zone graph to navigate.
            table: Shared occupancy table mapping (name, turn) to drone count.
                   Updated externally after each drone's path is committed.

        Returns:
            A list of (zone_or_link, turn) tuples representing the drone's
            movement schedule from start to end. Returns an empty list if no
            path exists.
        """
        start: Zone = graph.get_start()
        end: Zone = graph.get_end()

        # Priority queue entries: (cost, tiebreak, zone_name, turn, schedule)
        pq: list[tuple[float, int, str, int, list[tuple[Any, int]]]] = [
            (0.0, self._count, start.name, 0, [(start, 0)])
        ]
        visited: dict[tuple[str, int], float] = {}

        while pq:
            cost, _, name, turn, schedule = heapq.heappop(pq)

            max_turns: int = len(graph.zones) * 2 + graph.nb_drones
            if turn >= max_turns:
                continue

            if name == end.name:
                return schedule

            if visited.get((name, turn), float("inf")) <= cost:
                continue
            visited[(name, turn)] = cost

            zone: Zone | None = graph.get_zone_by_name(name)
            if zone is None:
                continue

            current_count = table.get((name, turn + 1), 0)
            capacity_ok = (
                zone.is_start
                or zone.is_end
                or current_count < zone.max_drones
            )
            if capacity_ok:
                self._count += 1
                heapq.heappush(
                    pq,
                    (
                        cost + 1.0,
                        self._count,
                        name,
                        turn + 1,
                        schedule + [(zone, turn + 1)],
                    ),
                )

            for conn in graph.get_current_connections(zone):
                adj: Zone | None = graph.get_zone_by_name(conn.zone_b)
                if adj is None:
                    continue
                if adj.zone_type == ZoneType.BLOCKED:
                    continue

                is_restricted = adj.zone_type == ZoneType.RESTRICTED
                move_cost = 2 if is_restricted else 1
                arrival_turn = turn + move_cost

                dest_count = table.get((adj.name, arrival_turn), 0)
                dest_ok = adj.is_end or dest_count < adj.max_drones
                if not dest_ok:
                    continue

                new_schedule = list(schedule)

                link_id = f"{min(name, adj.name)}-{max(name, adj.name)}"
                link_turn = turn + 1
                if table.get(
                    (link_id, link_turn), 0
                        ) >= conn.max_link_capacity:
                    continue

                if is_restricted:
                    new_schedule.append((link_id, link_turn))
                new_schedule.append((adj, arrival_turn))

                weight = (
                    0.9
                    if adj.zone_type == ZoneType.PRIORITY
                    else float(move_cost)
                )
                self._count += 1
                heapq.heappush(
                    pq,
                    (
                        cost + weight,
                        self._count,
                        adj.name,
                        arrival_turn,
                        new_schedule,
                    ),
                )

        return []
