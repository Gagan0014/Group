# metro_app/serializers.py
from rest_framework import serializers
from .models import Station, MetroLine, Route, RouteStep

class MetroLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetroLine
        fields = ['id', 'name', 'color', 'code']

class StationSerializer(serializers.ModelSerializer):
    lines = MetroLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Station
        fields = ['id', 'name', 'code', 'latitude', 'longitude', 'lines', 'is_interchange']

class RouteStepSerializer(serializers.ModelSerializer):
    from_station = StationSerializer(read_only=True)
    to_station = StationSerializer(read_only=True)
    line = MetroLineSerializer(read_only=True)
    
    class Meta:
        model = RouteStep
        fields = ['step_number', 'from_station', 'to_station', 'line', 'distance', 'time', 'is_interchange']

class RouteSerializer(serializers.ModelSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)
    steps = RouteStepSerializer(many=True, read_only=True)
    
    class Meta:
        model = Route
        fields = ['id', 'source', 'destination', 'total_distance', 'total_time', 'interchanges', 'steps', 'created_at']

class RouteRequestSerializer(serializers.Serializer):
    source = serializers.IntegerField()
    destination = serializers.IntegerField()
    priority = serializers.ChoiceField(choices=['time', 'distance', 'interchanges'], default='time')