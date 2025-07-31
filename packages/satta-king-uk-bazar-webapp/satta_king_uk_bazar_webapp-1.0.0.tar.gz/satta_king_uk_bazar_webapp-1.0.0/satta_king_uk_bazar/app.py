import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, url_for
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "satta-king-uk-bazar-secret-key-2025")

# Load game data
def load_games_data():
    try:
        with open('data/games.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Games data file not found")
        return {"live_games": [], "next_games": [], "rest_games": []}

def load_monthly_results():
    try:
        with open('data/monthly_results.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Monthly results data file not found")
        return {}

@app.route('/')
def index():
    """Main page showing all game results"""
    games_data = load_games_data()
    current_date = datetime.now().strftime("%B %d, %Y")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y")
    
    return render_template('index.html', 
                         games_data=games_data,
                         current_date=current_date,
                         yesterday_date=yesterday_date)

@app.route('/game/<game_id>')
def game_chart(game_id):
    """Individual game chart page"""
    games_data = load_games_data()
    current_date = datetime.now().strftime("%B %d, %Y %H:%M")
    
    # Find the game in all categories
    game = None
    for category in ['live_games', 'next_games', 'rest_games']:
        for g in games_data.get(category, []):
            if g['id'] == game_id:
                game = g
                break
        if game:
            break
    
    if not game:
        return "Game not found", 404
    
    return render_template('game_chart.html', game=game, current_date=current_date)

@app.route('/monthly-chart')
def monthly_chart():
    """Monthly results chart page"""
    monthly_data = load_monthly_results()
    current_month = datetime.now().strftime("%B %Y")
    
    return render_template('monthly_chart.html', 
                         monthly_data=monthly_data,
                         current_month=current_month)

@app.route('/api/games')
def api_games():
    """API endpoint for games data"""
    return jsonify(load_games_data())

@app.route('/api/monthly-results')
def api_monthly_results():
    """API endpoint for monthly results"""
    return jsonify(load_monthly_results())

@app.route('/sitemap.xml')
def sitemap():
    """Generate dynamic sitemap"""
    host_components = request.host.split(':')
    host = host_components[0]
    
    pages = []
    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()
    
    # Main pages
    pages.append({
        'loc': url_for('index', _external=True),
        'lastmod': ten_days_ago,
        'changefreq': 'daily',
        'priority': '1.0'
    })
    
    pages.append({
        'loc': url_for('monthly_chart', _external=True),
        'lastmod': ten_days_ago,
        'changefreq': 'daily', 
        'priority': '0.8'
    })
    
    # Game pages
    games_data = load_games_data()
    for category in ['live_games', 'next_games', 'rest_games']:
        for game in games_data.get(category, []):
            pages.append({
                'loc': url_for('game_chart', game_id=game['id'], _external=True),
                'lastmod': ten_days_ago,
                'changefreq': 'daily',
                'priority': '0.7'
            })
    
    sitemap_xml = render_template('sitemap.xml', pages=pages, host=host)
    response = app.response_class(sitemap_xml, mimetype='application/xml')
    return response

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt"""
    return app.send_static_file('robots.txt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
