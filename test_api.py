#!/usr/bin/env python
"""
Lagos State Property Portal API Test Script

This script provides a simple way to test the API endpoints of the Lagos State Property Portal.
It uses the requests library to make HTTP requests to the API endpoints.

Usage:
    python test_api.py
"""

import requests
import json
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

# Store the JWT token
token = None

def print_response(response):
    """Print the response in a formatted way"""
    print("\nStatus Code:", response.status_code)
    try:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Response (not JSON):", response.text)

def register_user():
    """Register a new user"""
    print("\n=== Registering a new user ===")
    url = f"{BASE_URL}/auth/register"
    data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "securepassword",
        "role": "buyer_renter"
    }
    response = requests.post(url, json=data)
    print_response(response)
    return response

def login_user():
    """Login a user and get JWT token"""
    global token
    print("\n=== Logging in a user ===")
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "testuser@example.com",
        "password": "securepassword"
    }
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 200:
        token = response.json().get("token")
        print(f"Token: {token[:10]}...")
    return response

def get_profile():
    """Get user profile"""
    print("\n=== Getting user profile ===")
    url = f"{BASE_URL}/auth/profile"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print_response(response)
    return response

def list_properties():
    """List properties with filters"""
    print("\n=== Listing properties ===")
    url = f"{BASE_URL}/properties"
    params = {
        "location": "Lekki",
        "price_min": 10000000,
        "price_max": 50000000,
        "type": "residential",
        "amenities[]": ["Swimming Pool", "Security"]
    }
    response = requests.get(url, params=params)
    print_response(response)
    return response

def get_property_details(property_id=1):
    """Get property details"""
    print(f"\n=== Getting property details for ID {property_id} ===")
    url = f"{BASE_URL}/properties/{property_id}"
    response = requests.get(url)
    print_response(response)
    return response

def create_property():
    """Create a new property listing"""
    print("\n=== Creating a property listing ===")
    url = f"{BASE_URL}/properties"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": "Test Property",
        "description": "A test property listing",
        "price": 20000000,
        "type": "residential",
        "location": "Lekki Phase 1, Lagos",
        "amenities": ["Swimming Pool", "24/7 Electricity", "Security"],
        "images": [],
        "documents": []
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response)
    return response

def add_to_favorites(property_id=1):
    """Add a property to favorites"""
    print(f"\n=== Adding property ID {property_id} to favorites ===")
    url = f"{BASE_URL}/favorites"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"property_id": property_id}
    response = requests.post(url, json=data, headers=headers)
    print_response(response)
    return response

def list_favorites():
    """List user favorites"""
    print("\n=== Listing user favorites ===")
    url = f"{BASE_URL}/favorites"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print_response(response)
    return response

def create_lead(property_id=1):
    """Create a new lead"""
    print(f"\n=== Creating a lead for property ID {property_id} ===")
    url = f"{BASE_URL}/leads"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "property_id": property_id,
        "message": "I'm interested in this property. Can I schedule a viewing?"
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response)
    return response

def initiate_payment(property_id=1):
    """Initiate a payment"""
    print(f"\n=== Initiating payment for property ID {property_id} ===")
    url = f"{BASE_URL}/payments/initiate"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "property_id": property_id,
        "amount": 50000,
        "type": "rent"
    }
    response = requests.post(url, json=data, headers=headers)
    print_response(response)
    return response

def run_tests():
    """Run all tests"""
    try:
        # Authentication tests
        register_user()
        login_user()
        if token:
            get_profile()
            
            # Property tests
            list_properties()
            get_property_details()
            create_property()
            
            # Favorites tests
            add_to_favorites()
            list_favorites()
            
            # Leads tests
            create_lead()
            
            # Payment tests
            initiate_payment()
            
            print("\n=== All tests completed ===")
        else:
            print("\nError: Could not obtain authentication token. Skipping authenticated tests.")
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to the API at {BASE_URL}")
        print("Make sure the server is running and the URL is correct.")
    except Exception as e:
        print(f"\nError: {str(e)}")

def main():
    """Main function"""
    print("Lagos State Property Portal API Test Script")
    print(f"API Base URL: {BASE_URL}")
    print("\nRunning tests...")
    run_tests()

if __name__ == "__main__":
    main()