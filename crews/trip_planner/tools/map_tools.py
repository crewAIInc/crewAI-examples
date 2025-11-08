import os
import requests
from datetime import datetime
from crewai_tools import tool


@tool("Get City Coordinates")
def get_city_coordinates(city_name: str) -> dict:
    """
    Get the latitude and longitude coordinates of a city using Google Maps Geocoding API.

    Args:
        city_name: The name of the city to geocode
        
    Returns:
        A dictionary containing the coordinates and formatted address:
        {
            'lat': latitude,
            'lng': longitude,
            'formatted_address': full address,
            'place_name': original place name
        }
    """
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        return {
            'error': 'GOOGLE_MAPS_API_KEY environment variable not set',
            'place_name': place_name
        }
    
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': place_name,
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'OK' and len(data['results']) > 0:
            result = data['results'][0]
            location = result['geometry']['location']
            
            return {
                'lat': location['lat'],
                'lng': location['lng'],
                'formatted_address': result['formatted_address'],
                'place_name': place_name
            }
        else:
            return {
                'error': f"Could not find coordinates for '{place_name}'. Status: {data['status']}",
                'place_name': place_name
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'error': f'API request failed: {str(e)}',
            'place_name': place_name
        }


@tool("Get Travel Time Between Cities")
def get_travel_time(origin: str, destination: str, mode: str = "transit") -> dict:
    """
    Get travel time between two locations using Google Maps Distance Matrix API.
    Supports public transport including planes (via transit mode).
    
    Args:
        origin: Starting location (city, address, or place name)
        destination: Destination location (city, address, or place name)
        mode: Travel mode - 'transit' (default, includes public transport),
              'driving', 'walking', or 'bicycling'
        
    Returns:
        A dictionary containing travel information:
        {
            'origin': origin address,
            'destination': destination address,
            'distance': distance in km,
            'duration': travel time in hours and minutes,
            'duration_minutes': total travel time in minutes,
            'mode': travel mode used
        }
    """
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        return {
            'error': 'GOOGLE_MAPS_API_KEY environment variable not set',
            'origin': origin,
            'destination': destination
        }
    
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': origin,
        'destinations': destination,
        'mode': mode,
        'key': api_key
    }
    
    # For transit mode, add departure time (now) to get real-time schedules
    if mode == 'transit':
        params['departure_time'] = 'now'
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'OK':
            row = data['rows'][0]
            element = row['elements'][0]
            
            if element['status'] == 'OK':
                distance_meters = element['distance']['value']
                duration_seconds = element['duration']['value']
                
                distance_km = distance_meters / 1000
                duration_minutes = duration_seconds / 60
                hours = int(duration_minutes // 60)
                minutes = int(duration_minutes % 60)
                
                duration_text = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                
                return {
                    'origin': data['origin_addresses'][0],
                    'destination': data['destination_addresses'][0],
                    'distance': f"{distance_km:.2f} km",
                    'distance_km': round(distance_km, 2),
                    'duration': duration_text,
                    'duration_minutes': int(duration_minutes),
                    'mode': mode
                }
            else:
                return {
                    'error': f"No route found between '{origin}' and '{destination}' using {mode} mode. Status: {element['status']}",
                    'origin': origin,
                    'destination': destination,
                    'mode': mode
                }
        else:
            return {
                'error': f'API request failed. Status: {data["status"]}',
                'origin': origin,
                'destination': destination
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'error': f'API request failed: {str(e)}',
            'origin': origin,
            'destination': destination
        }
