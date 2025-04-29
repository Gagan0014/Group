import json
import os
from django.core.management.base import BaseCommand
from metro_app.models import MetroLine, Station, Connection

class Command(BaseCommand):
    help = 'Load Delhi Metro data from JSON file'

    def handle(self, *args, **options):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Connection.objects.all().delete()
        Station.objects.all().delete()
        MetroLine.objects.all().delete()
        
        # Load data from JSON file
        data_file = os.path.join('metro_app', 'data', 'metro_data.json')
        self.stdout.write(f'Loading data from {data_file}...')
        
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            # Create lines
            line_map = {}
            for line_data in data['lines']:
                line = MetroLine.objects.create(
                    name=line_data['name'],
                    color=line_data['color'],
                    code=line_data['code']
                )
                line_map[line.code] = line
                self.stdout.write(f'Created line: {line.name}')
            
            # Create stations
            station_map = {}
            for station_data in data['stations']:
                station = Station.objects.create(
                    name=station_data['name'],
                    code=station_data['code'],
                    latitude=station_data['latitude'],
                    longitude=station_data['longitude'],
                    is_interchange=station_data['is_interchange']
                )
                
                # Add lines to station
                for line_code in station_data['lines']:
                    station.lines.add(line_map[line_code])
                
                station_map[station.code] = station
                self.stdout.write(f'Created station: {station.name}')
            
            # Create connections
            for conn_data in data['connections']:
                Connection.objects.create(
                    from_station=station_map[conn_data['from_station']],
                    to_station=station_map[conn_data['to_station']],
                    line=line_map[conn_data['line']],
                    distance=conn_data['distance'],
                    travel_time=conn_data['travel_time']
                )
                self.stdout.write(f'Created connection: {conn_data["from_station"]} to {conn_data["to_station"]}')
            
            self.stdout.write(self.style.SUCCESS('Successfully loaded Delhi Metro data'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))