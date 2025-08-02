import json
import os

def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    """Save configuration to config.json"""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def define_pars(census_api_key, main_year, geos, commute_states, use_pums):
    """Update pars in config and save to file"""
    # Load current config
    config = load_config()
    
    # Define pars
    config['census_api_key'] = census_api_key
    config['main_year'] = main_year
    config['geos'] = geos
    config['commute_states'] = commute_states
    config['use_pums'] = use_pums
    
    # Save updated config
    save_config(config)
    
    return config

def get_pars():
    """Get current parameters from config"""
    config = load_config()
    return {
        'census_api_key': config.get('census_api_key'),
        'main_year': config.get('main_year'),
        'geos': config.get('geos'),
        'commute_states': config.get('commute_states'),
        'use_pums': config.get('use_pums')
    }

# Example usage:
# To update main_year to a different value:
# define_pars("api_key", 2022, ["24029"], ["24"], ["24"])

# To get current parameters:
# params = get_pars()
# current_year = params['main_year']
