#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_geocoding_api():
    """Test Google Maps Geocoding API directly"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    print("=" * 60)
    print("Testing Google Maps Geocoding API")
    print("=" * 60)
    
    if not api_key:
        print("❌ ERROR: GOOGLE_MAPS_API_KEY environment variable not set")
        print("\nPlease add to your .env file:")
        print("GOOGLE_MAPS_API_KEY=your_api_key_here")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...")
    
    # Test with a simple location
    test_location = "Dubai, UAE"
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': test_location,
        'key': api_key
    }
    
    print(f"\nTesting location: {test_location}")
    print(f"Request URL: {url}")
    print(f"Parameters: address={test_location}, key={api_key[:10]}...\n")
    
    try:
        response = requests.get(url, params=params)
        print(f"Response Status Code: {response.status_code}")
        data = response.json()
        
        print(f"API Status: {data.get('status')}")
        
        if data['status'] == 'REQUEST_DENIED':
            print("\n❌ REQUEST_DENIED")
            print(f"Error message: {data.get('error_message', 'No error message provided')}")
            print("\nPossible causes:")
            print("1. API key is invalid")
            print("2. Geocoding API is not enabled in Google Cloud Console")
            print("3. API key restrictions prevent this request")
            print("\nTo fix:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. Enable 'Geocoding API' and 'Distance Matrix API'")
            print("3. Create/verify your API key")
            print("4. Update GOOGLE_MAPS_API_KEY in your .env file")
            return False
        
        elif data['status'] == 'OK' and len(data['results']) > 0:
            result = data['results'][0]
            location = result['geometry']['location']
            print("\n✓ SUCCESS!")
            print(f"Formatted Address: {result['formatted_address']}")
            print(f"Coordinates: {location['lat']}, {location['lng']}")
            return True
        
        else:
            print(f"\n❌ Unexpected status: {data['status']}")
            return False
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        return False


def test_distance_matrix_api():
    """Test Google Maps Distance Matrix API directly"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    print("\n" + "=" * 60)
    print("Testing Google Maps Distance Matrix API")
    print("=" * 60)
    
    if not api_key:
        print("❌ ERROR: GOOGLE_MAPS_API_KEY not set")
        return False
    
    origin = "Vienna, Austria"
    destination = "Dubai, UAE"
    
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': origin,
        'destinations': destination,
        'mode': 'transit',
        'key': api_key
    }
    
    print(f"\nTesting route: {origin} → {destination}")
    print(f"Request URL: {url}")
    print(f"Mode: transit\n")
    
    try:
        response = requests.get(url, params=params)
        print(f"Response Status Code: {response.status_code}")
        data = response.json()
        
        print(f"API Status: {data.get('status')}")
        
        if data['status'] == 'REQUEST_DENIED':
            print("\n❌ REQUEST_DENIED")
            print(f"Error message: {data.get('error_message', 'No error message provided')}")
            print("\nPlease enable 'Distance Matrix API' in Google Cloud Console")
            return False
        
        elif data['status'] == 'OK':
            row = data['rows'][0]
            element = row['elements'][0]
            
            if element['status'] == 'OK':
                distance = element['distance']['text']
                duration = element['duration']['text']
                print("\n✓ SUCCESS!")
                print(f"Distance: {distance}")
                print(f"Duration: {duration}")
                return True
            else:
                print(f"\n⚠️  Element status: {element['status']}")
                print("Note: Transit mode might not be available for this route")
                return False
        
        else:
            print(f"\n❌ Unexpected status: {data['status']}")
            return False
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        return False


def test_crewai_tools():
    """Test the CrewAI tools"""
    print("\n" + "=" * 60)
    print("Testing CrewAI Map Tools")
    print("=" * 60)
    
    try:
        
        from tools.map_tools import MapTools
        
        # Test get_city_coordinates
        print("\nTesting MapTools.get_city_coordinates()...")
        result = MapTools.get_city_coordinates("Dubai, UAE")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        else:
            print(f"✓ SUCCESS!")
            print(f"Coordinates: {result.get('lat')}, {result.get('lng')}")
            print(f"Address: {result.get('formatted_address')}")
        
        # Test get_travel_time
        print("\nTesting MapTools.get_travel_time()...")
        result = MapTools.get_travel_time("Vienna, Austria", "Dubai, UAE", "transit")
        
        if 'error' in result:
            print(f"⚠️  Note: {result['error']}")
        else:
            print(f"✓ SUCCESS!")
            print(f"Distance: {result.get('distance')}")
            print(f"Duration: {result.get('duration')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Google Maps API Testing Suite\n")
    
    # Run tests
    geocoding_ok = test_geocoding_api()
    distance_ok = test_distance_matrix_api()
    tools_ok = test_crewai_tools()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Geocoding API: {'✓ PASS' if geocoding_ok else '❌ FAIL'}")
    print(f"Distance Matrix API: {'✓ PASS' if distance_ok else '❌ FAIL'}")
    print(f"CrewAI Tools: {'✓ PASS' if tools_ok else '❌ FAIL'}")
    print("=" * 60)
