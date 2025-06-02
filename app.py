from flask import Flask, render_template, request, jsonify
import json
from difflib import get_close_matches
import random

app = Flask(__name__)

def load_travel_data():
    try:
        with open('data/travel_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('travel_data', [])
    except FileNotFoundError:
        print("Error: The travel data file was not found.")
        return []
    except json.JSONDecodeError:
        print("Error: The travel data file contains invalid JSON.")
        return []
    except Exception as e:
        print(f"Unexpected error loading travel data: {e}")
        return []

travel_data = load_travel_data()

def find_best_match(user_input, possibilities):
    """Find the closest matching country or city name with improved matching"""
    words = user_input.lower().split()
    for word in words:
        matches = get_close_matches(word, possibilities, n=1, cutoff=0.6)
        if matches:
            return matches[0]
    return None

def get_location_specific_response(user_input, location_info, is_city=False):
    """Generate detailed responses for specific locations"""
    location_type = "city" if is_city else "country"
    name = location_info['city'] if is_city else location_info['country']
    
    # Define response templates
    responses = {
        'attractions': f"🌟 Top attractions in {name}:\n• " + "\n• ".join(location_info.get('top_attractions', ['Various interesting sites'])),
        'food': f"🍴 Must-try local dishes in {name}:\n• " + "\n• ".join(location_info.get('native_cuisine', ['Delicious local cuisine'])),
        'hotels': f"🏩 Recommended accommodations in {name}:\n• " + "\n• ".join(location_info.get('notable_hotels', ['Various quality hotels'])),
        'transport': f"🚆 Getting around {name}:\n" + location_info.get('transportation_highlights', 'Various transportation options available'),
        'time': f"📅 Best time to visit {name}: {location_info.get('best_time_to_visit', 'Year-round')}",
        'safety': f"⚠️ Safety in {name}:\n" + location_info.get('safety_tips', 'Standard travel precautions recommended'),
        'default_city': (
            f"📍 {name}, {location_info['country']} Overview:\n"
            f"• Attractions: {', '.join(location_info.get('top_attractions', ['Cultural sites']))}\n"
            f"• Cuisine: {', '.join(location_info.get('native_cuisine', ['Local specialties']))}\n"
            f"• Best Visit Time: {location_info.get('best_time_to_visit', 'Year-round')}"
        ),
        'default_country': (
            f"🌏 {name} Travel Guide:\n"
            f"• Major Cities: {', '.join(set(item['city'] for item in travel_data if item['country'] == name))}\n"
            f"• Best Visit Time: {location_info.get('best_time_to_visit', 'Year-round')}\n"
            f"• Local Cuisine: {', '.join(set(cuisine for item in travel_data if item['country'] == name for cuisine in item.get('native_cuisine', [])))}"
        )
    }

    # Check for specific question types
    if any(word in user_input for word in ['attraction', 'place', 'see', 'visit', 'do']):
        return responses['attractions']
    elif any(word in user_input for word in ['food', 'eat', 'cuisine', 'dish', 'meal']):
        return responses['food']
    elif any(word in user_input for word in ['hotel', 'stay', 'accommodation', 'sleep']):
        return responses['hotels']
    elif any(word in user_input for word in ['transport', 'get around', 'travel', 'metro', 'bus']):
        return responses['transport']
    elif any(word in user_input for word in ['time', 'when', 'month', 'season', 'weather']):
        return responses['time']
    elif any(word in user_input for word in ['safe', 'safety', 'danger']):
        return responses['safety']
    else:
        return responses[f'default_{location_type}']

def get_general_response(user_input):
    """Handle general queries and fallback responses"""
    greetings = [
        "Hello! I'm your travel assistant. Where would you like to go?",
        "Hi there! Ready to plan your next adventure?",
        "Welcome! Ask me about travel destinations worldwide."
    ]
    
    help_responses = [
        "I can help with:\n✈️ Countries\n🏙️ Cities\n🏛️ Attractions\n🍜 Food\n🏨 Hotels\n🚆 Transportation",
        "Try asking about:\n• Places to visit\n• Local cuisine\n• Best travel times\n• Where to stay",
        "Need travel advice? Ask about:\n- Specific destinations\n- Things to do\n- What to eat\n- Getting around"
    ]
    
    unknown_responses = [
        "I specialize in travel information. Try asking about a specific destination.",
        "I'd love to help with your travel questions. Could you be more specific?",
        "For travel advice, try mentioning a country or city you're interested in."
    ]
    
    if any(word in user_input for word in ['hello', 'hi', 'hey']):
        return random.choice(greetings)
    elif 'help' in user_input:
        return random.choice(help_responses)
    else:
        return random.choice(unknown_responses)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get', methods=['POST'])
def get_response():
    try:
        user_input = request.json['message'].strip()
        if not user_input:
            return jsonify({'reply': "Please type a message."})
    except (TypeError, KeyError):
        return jsonify({'reply': "Sorry, there was an error processing your request."})
    
    # Extract all possible locations
    all_countries = list(set(item['country'] for item in travel_data))
    all_cities = list(set(item['city'] for item in travel_data))
    
    # Find best matches
    country_match = find_best_match(user_input, all_countries)
    city_match = find_best_match(user_input, all_cities) if not country_match else None
    
    # Get location info
    country_info = next((item for item in travel_data if item['country'] == country_match), None) if country_match else None
    city_info = next((item for item in travel_data if item['city'] == city_match), None) if city_match else None
    
    # Generate response
    if country_info:
        response = get_location_specific_response(user_input, country_info, is_city=False)
    elif city_info:
        response = get_location_specific_response(user_input, city_info, is_city=True)
    else:
        # Try to detect if user mentioned a location but we didn't match it
        possible_locations = [word.title() for word in user_input.split() 
                            if word.title() in all_countries + all_cities]
        if possible_locations:
            response = f"I don't have information about {possible_locations[0]}. Try another destination."
        else:
            response = get_general_response(user_input)
    
    return jsonify({'reply': response})

if __name__ == '__main__':
    app.run(debug=True)