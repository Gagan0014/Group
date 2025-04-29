# metro_app/models.py
from django.db import models
from django.core.validators import MinValueValidator

class MetroLine(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name

class Station(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    lines = models.ManyToManyField(MetroLine, related_name='stations')
    is_interchange = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Connection(models.Model):
    from_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='outgoing_connections')
    to_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='incoming_connections')
    line = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    distance = models.FloatField(validators=[MinValueValidator(0.0)])  # in kilometers
    travel_time = models.IntegerField(validators=[MinValueValidator(0)])  # in minutes
    
    class Meta:
        unique_together = ('from_station', 'to_station', 'line')
    
    def __str__(self):
        return f"{self.from_station} to {self.to_station} via {self.line}"

class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='routes_from')
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='routes_to')
    total_distance = models.FloatField(validators=[MinValueValidator(0.0)])
    total_time = models.IntegerField(validators=[MinValueValidator(0)])
    interchanges = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Route from {self.source} to {self.destination}"

class RouteStep(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField()
    from_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='route_steps_from')
    to_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='route_steps_to')
    line = models.ForeignKey(MetroLine, on_delete=models.CASCADE)
    distance = models.FloatField(validators=[MinValueValidator(0.0)])
    time = models.IntegerField(validators=[MinValueValidator(0)])
    is_interchange = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['route', 'step_number']
    
    def __str__(self):
        return f"Step {self.step_number}: {self.from_station} to {self.to_station}"