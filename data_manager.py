import os
import json
import pandas as pd
from datetime import datetime, timedelta

# Import all data fetching functions
from films import fetch_films_data
from people import fetch_people_data
from planets import fetch_planets_data
from species import fetch_species_data
from vehicles import fetch_vehicles_data
from starships import fetch_starships_data

DATA_DIR = "data"
CACHE_DURATION = timedelta(days=7)  # Cache data for 7 days

def ensure_data_dir():
    """Ensure the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_data(data, filename):
    """Save data to a JSON file."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump({'timestamp': datetime.now().isoformat(), 'data': data}, f)

def load_data(filename):
    """Load data from a JSON file if it exists and is not expired."""
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            cached = json.load(f)
            cache_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cache_time < CACHE_DURATION:
                return cached['data']
    return None

def get_or_fetch_data(fetch_func, filename):
    """Get data from cache or fetch it if needed."""
    ensure_data_dir()
    data = load_data(filename)
    if data is None:
        data = fetch_func()
        save_data(data, filename)
    return data

# Functions to get each type of data
def get_films_data():
    return get_or_fetch_data(fetch_films_data, 'films.json')

def get_people_data():
    return get_or_fetch_data(fetch_people_data, 'people.json')

def get_planets_data():
    return get_or_fetch_data(fetch_planets_data, 'planets.json')

def get_species_data():
    return get_or_fetch_data(fetch_species_data, 'species.json')

def get_vehicles_data():
    return get_or_fetch_data(fetch_vehicles_data, 'vehicles.json')

def get_starships_data():
    return get_or_fetch_data(fetch_starships_data, 'starships.json')

# Function to fetch all data at once
def fetch_all_data():
    """Fetch and cache all data."""
    print("Fetching films data...")
    get_films_data()
    print("Fetching people data...")
    get_people_data()
    print("Fetching planets data...")
    get_planets_data()
    print("Fetching species data...")
    get_species_data()
    print("Fetching vehicles data...")
    get_vehicles_data()
    print("Fetching starships data...")
    get_starships_data()
    print("All data fetched and cached!")
