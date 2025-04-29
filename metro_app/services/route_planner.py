# metro_app/services/route_planner.py
import heapq
from collections import defaultdict
from metro_app.models import Station, Connection, Route, RouteStep, MetroLine

class RouteCalculator:
    def __init__(self):
        self.graph = defaultdict(list)
        self._build_graph()
    
    def _build_graph(self):
        """Build a graph representation from the database connections"""
        connections = Connection.objects.select_related('from_station', 'to_station', 'line').all()
        
        for conn in connections:
            # Add connection to graph (from -> to)
            self.graph[conn.from_station.id].append({
                'station': conn.to_station,
                'line': conn.line,
                'distance': conn.distance,
                'time': conn.travel_time
            })
    
    def find_shortest_route(self, source_id, destination_id, priority='time'):
        """
        Find shortest route between two stations using Dijkstra's algorithm
        priority: 'time' or 'distance' or 'interchanges'
        """
        if source_id == destination_id:
            return None
        
        # Initialize 
        distances = {station_id: float('infinity') for station_id in self.graph}
        distances[source_id] = 0
        previous = {}
        previous_lines = {}
        interchanges = {station_id: 0 for station_id in self.graph}
        queue = [(0, source_id)]
        
        while queue:
            current_distance, current_station_id = heapq.heappop(queue)
            
            # If we've reached our destination
            if current_station_id == destination_id:
                break
                
            # If we've found a worse path
            if current_distance > distances[current_station_id]:
                continue
                
            # Check each neighbor
            for neighbor in self.graph[current_station_id]:
                neighbor_station = neighbor['station']
                line = neighbor['line']
                
                # Calculate cost based on priority
                if priority == 'time':
                    weight = neighbor['time']
                elif priority == 'distance':
                    weight = neighbor['distance']
                else:  # interchanges
                    weight = 1
                
                # Calculate interchanges
                interchange_count = interchanges[current_station_id]
                if current_station_id in previous_lines and previous_lines[current_station_id] != line.id:
                    interchange_count += 1
                
                distance = distances[current_station_id] + weight
                
                if distance < distances[neighbor_station.id]:
                    distances[neighbor_station.id] = distance
                    previous[neighbor_station.id] = (current_station_id, line.id)
                    previous_lines[neighbor_station.id] = line.id
                    interchanges[neighbor_station.id] = interchange_count
                    heapq.heappush(queue, (distance, neighbor_station.id))
        
        # Build the route
        if destination_id not in previous:
            return None
            
        route_stations = []
        route_lines = []
        current = destination_id
        
        while current != source_id:
            route_stations.append(current)
            prev_station, line_id = previous[current]
            route_lines.append(line_id)
            current = prev_station
            
        route_stations.append(source_id)
        
        # Reverse to get start -> end order
        route_stations.reverse()
        route_lines.reverse()
        
        # Create route model objects
        source = Station.objects.get(id=source_id)
        destination = Station.objects.get(id=destination_id)
        
        # Count actual interchanges
        interchange_count = 0
        prev_line = None
        for line in route_lines:
            if prev_line is not None and line != prev_line:
                interchange_count += 1
            prev_line = line
        
        # Create route
        route = Route.objects.create(
            source=source,
            destination=destination,
            total_distance=self._calculate_total_distance(route_stations, route_lines),
            total_time=self._calculate_total_time(route_stations, route_lines),
            interchanges=interchange_count
        )
        
        # Create route steps
        self._create_route_steps(route, route_stations, route_lines)
        
        return route
    
    def _calculate_total_distance(self, station_ids, line_ids):
        """Calculate the total distance of the route"""
        total = 0
        for i in range(len(station_ids) - 1):
            conn = Connection.objects.get(
                from_station_id=station_ids[i],
                to_station_id=station_ids[i+1],
                line_id=line_ids[i]
            )
            total += conn.distance
        return total
    
    def _calculate_total_time(self, station_ids, line_ids):
        """Calculate the total time of the route"""
        total = 0
        for i in range(len(station_ids) - 1):
            conn = Connection.objects.get(
                from_station_id=station_ids[i],
                to_station_id=station_ids[i+1],
                line_id=line_ids[i]
            )
            total += conn.travel_time
        return total
    
    def _create_route_steps(self, route, station_ids, line_ids):
        """Create RouteStep objects for each segment of the route"""
        prev_line = None
        
        for i in range(len(station_ids) - 1):
            from_station = Station.objects.get(id=station_ids[i])
            to_station = Station.objects.get(id=station_ids[i+1])
            line = MetroLine.objects.get(id=line_ids[i])
            conn = Connection.objects.get(
                from_station=from_station,
                to_station=to_station,
                line=line
            )
            
            # Determine if this is an interchange
            is_interchange = prev_line is not None and prev_line != line.id
            
            RouteStep.objects.create(
                route=route,
                step_number=i+1,
                from_station=from_station,
                to_station=to_station,
                line=line,
                distance=conn.distance,
                time=conn.travel_time,
                is_interchange=is_interchange
            )
            
            prev_line = line.id