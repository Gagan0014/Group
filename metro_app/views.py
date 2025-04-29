# metro_app/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Station, MetroLine, Route
from .serializers import (
    StationSerializer, MetroLineSerializer, 
    RouteSerializer, RouteRequestSerializer
)
from .services.route_planner import RouteCalculator

class StationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'results': []})
            
        stations = Station.objects.filter(name__icontains=query)[:10]
        serializer = self.get_serializer(stations, many=True)
        return Response({'results': serializer.data})

class MetroLineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MetroLine.objects.all()
    serializer_class = MetroLineSerializer
    
    @action(detail=True, methods=['get'])
    def stations(self, request, pk=None):
        line = self.get_object()
        stations = line.stations.all()
        serializer = StationSerializer(stations, many=True)
        return Response(serializer.data)

class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    
    @action(detail=False, methods=['post'])
    def plan(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        source_id = serializer.validated_data['source']
        destination_id = serializer.validated_data['destination']
        priority = serializer.validated_data.get('priority', 'time')
        
        # Find source and destination stations
        try:
            source_station=Station.objects.get(id=source_id)
            destination_station=Station.objects.get(id=destination_id)
        except Station.DoesNotExist:
            return Response(
                {'error': 'Source or destination station not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Calculate route
        route_calculator = RouteCalculator()
        source_station=Station.objects.get(id=source_id)
        destination_station=Station.objects.get(id=destination_id)
        route = route_calculator.find_shortest_route(source_id, destination_id, priority)
        
        if not route:
            return Response(
                {'error': 'Could not find a route between these stations'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        route_serializer = RouteSerializer(route)
        return Response(route_serializer.data)