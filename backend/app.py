from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Add the backend directory to sys.path so we can import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.api import api_bp

def create_app():
    # In production, Flask will serve the built React files from frontend/dist
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')
    app = Flask(__name__, static_folder=dist_dir, static_url_path='/')
    CORS(app) # Enable CORS for frontend integration
    
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Catch-all route to serve the React app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
            
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting IndiaGrid AI Backend on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
