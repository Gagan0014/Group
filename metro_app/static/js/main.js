// main.js
document.addEventListener('DOMContentLoaded', function() {
    // Constants and variables
    const sourceInput = document.getElementById('source');
    const destinationInput = document.getElementById('destination');
    const sourceSuggestions = document.getElementById('source-suggestions');
    const destinationSuggestions = document.getElementById('destination-suggestions');
    const routeForm = document.getElementById('route-form');
    const routeResults = document.getElementById('route-results');
    const routeSteps = document.getElementById('route-steps');
    
    // Selected stations
    let selectedSourceId = null;
    let selectedDestinationId = null;
    
    // Delhi Metro Line Colors
    const lineColors = {
        'red': '#E91E63',
        'yellow': '#FFC107',
        'blue': '#2196F3',
        'green': '#4CAF50',
        'violet': '#9C27B0',
        'orange': '#FF9800',
        'magenta': '#E91E63',
        'pink': '#F48FB1',
        'grey': '#9E9E9E',
        'rapid': '#00BCD4',
        'airport': '#FF5722'
    };
    
    // Event listeners
    sourceInput.addEventListener('input', debounce(function() {
        if (this.value.length >= 2) {
            fetchStationSuggestions(this.value, sourceSuggestions, 'source');
        } else {
            sourceSuggestions.style.display = 'none';
        }
    }, 300));
    
    destinationInput.addEventListener('input', debounce(function() {
        if (this.value.length >= 2) {
            fetchStationSuggestions(this.value, destinationSuggestions, 'destination');
        } else {
            destinationSuggestions.style.display = 'none';
        }
    }, 300));
    
    routeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (selectedSourceId && selectedDestinationId) {
            findRoute();
        } else {
            alert('Please select both source and destination stations');
        }
    });
    
    // Functions
    function debounce(func, delay) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), delay);
        };
    }
    
    function fetchStationSuggestions(query, container, type) {
        fetch(`/api/stations/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displayStationSuggestions(data.results, container, type);
            })
            .catch(error => console.error('Error fetching stations:', error));
    }
    
    function displayStationSuggestions(stations, container, type) {
        container.innerHTML = '';
        
        if (stations.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        stations.forEach(station => {
            const div = document.createElement('div');
            div.className = 'station-suggestion';
            div.textContent = station.name;
            
            // Add line indicators
            if (station.lines && station.lines.length > 0) {
                const lineIndicators = document.createElement('div');
                lineIndicators.className = 'line-indicators';
                
                station.lines.forEach(line => {
                    const indicator = document.createElement('span');
                    indicator.className = 'line-dot';
                    indicator.style.backgroundColor = lineColors[line.color.toLowerCase()] || '#333';
                    lineIndicators.appendChild(indicator);
                });
                
                div.appendChild(lineIndicators);
            }
            
            div.addEventListener('click', () => {
                if (type === 'source') {
                    sourceInput.value = station.name;
                    selectedSourceId = station.id;
                } else {
                    destinationInput.value = station.name;
                    selectedDestinationId = station.id;
                }
                container.style.display = 'none';
            });
            
            container.appendChild(div);
        });
        
        container.style.display = 'block';
    }
    
    function findRoute() {
        const priority = document.getElementById('priority').value;
        
        // Show loading state
        routeResults.style.display = 'none';
        
        fetch('/api/routes/plan/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                source: selectedSourceId,
                destination: selectedDestinationId,
                priority: priority
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
       .then(data => {
            displayRouteResults(data);
        })
       /* .catch(error => {
            console.error('Error finding route:', error);
            alert('Could not find a route. Please try again.');
        });*/
    }
    
    function displayRouteResults(route) {
        // Update summary
        document.getElementById('total-time').textContent = `${route.total_time} min`;
        document.getElementById('total-distance').textContent = `${route.total_distance.toFixed(1)} km`;
        document.getElementById('interchanges').textContent = route.interchanges;
        
        // Calculate fare (simplified version)
        const fare = calculateFare(route.total_distance);
        document.getElementById('fare').textContent = `₹ ${fare}`;
        
        // Clear previous route steps
        routeSteps.innerHTML = '';
        
        // Add start station
        const startStation = document.createElement('div');
        startStation.className = 'route-step';
        startStation.style.borderLeftColor = lineColors[route.steps[0].line.color.toLowerCase()] || '#333';
        
        const startHeader = document.createElement('div');
        startHeader.className = 'step-header';
        
        const startName = document.createElement('div');
        startName.className = 'step-station';
        startName.textContent = route.source.name;
        
        startHeader.appendChild(startName);
        startStation.appendChild(startHeader);
        
        const startLine = document.createElement('div');
        startLine.className = 'step-details';
        startLine.innerHTML = `<span class="line-indicator" style="background-color: ${lineColors[route.steps[0].line.color.toLowerCase()] || '#333'}"></span>
                              Board ${route.steps[0].line.name} Line towards ${route.steps[0].to_station.name}`;
        
        startStation.appendChild(startLine);
        routeSteps.appendChild(startStation);
        
        // Process route steps
        let currentLine = route.steps[0].line.id;
        
        for (let i = 0; i < route.steps.length; i++) {
            const step = route.steps[i];
            
            // Only show interchange stations or destination
            if (step.is_interchange || i === route.steps.length - 1) {
                const stepElement = document.createElement('div');
                stepElement.className = 'route-step';
                stepElement.style.borderLeftColor = lineColors[step.line.color.toLowerCase()] || '#333';
                
                const stepHeader = document.createElement('div');
                stepHeader.className = 'step-header';
                
                const stationName = document.createElement('div');
                stationName.className = 'step-station';
                stationName.textContent = step.to_station.name;
                
                const stepTime = document.createElement('div');
                stepTime.className = 'step-time';
                stepTime.textContent = `${step.time} min`;
                
                stepHeader.appendChild(stationName);
                stepHeader.appendChild(stepTime);
                stepElement.appendChild(stepHeader);
                
                // If this is an interchange
                if (step.is_interchange && i < route.steps.length - 1) {
                    const interchangeInfo = document.createElement('div');
                    interchangeInfo.className = 'step-details';
                    interchangeInfo.innerHTML = `<span class="interchange-indicator">Change</span> Transfer to ${route.steps[i+1].line.name} Line towards ${route.steps[route.steps.length-1].to_station.name}`;
                    stepElement.appendChild(interchangeInfo);
                    
                    // Update current line
                    currentLine = route.steps[i+1].line.id;
                }
                
                // If this is the destination
                if (i === route.steps.length - 1) {
                    const destInfo = document.createElement('div');
                    destInfo.className = 'step-details';
                    destInfo.textContent = 'Arrive at destination';
                    stepElement.appendChild(destInfo);
                }
                
                routeSteps.appendChild(stepElement);
            }
        }
        
        // Show route results
        routeResults.style.display = 'block';
        
        // Scroll to results
        routeResults.scrollIntoView({ behavior: 'smooth' });
        
        // Update map
       /* updateMap(route);*/
    }
    
    function calculateFare(distance) {
        // Simplified Delhi Metro fare calculation
        if (distance <= 2) return 10;
        if (distance <= 5) return 20;
        if (distance <= 12) return 30;
        if (distance <= 21) return 40;
        if (distance <= 32) return 50;
        return 60;
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});