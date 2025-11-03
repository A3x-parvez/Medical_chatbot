from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from retriever import MedicalRetriever
import config
import os

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize medical retriever safely
retriever = None
try:
    retriever = MedicalRetriever()
    print("✅ Medical retriever initialized successfully")
except Exception as e:
    print(f"❌ Error initializing retriever: {str(e)}")

# Serve frontend
@app.route('/')
def index():
    """Serve main HTML page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve CSS, JS, and other static frontend files"""
    return send_from_directory(app.static_folder, path)

# Chat route
@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided', 'success': False}), 400

        query = data['query']
        temperature = data.get('temperature', config.DEFAULT_TEMPERATURE)

        if not retriever:
            return jsonify({'error': 'Retriever not initialized', 'success': False}), 500

        # response = retriever.get_answer(query, temperature)
        # return jsonify({'response': response, 'success': True})
        result = retriever.get_answer(query, temperature)
        if isinstance(result, dict) and "response" in result:
            result = result["response"]
        print(f"✅ Response generated successfully")
        print(f"Response: {result}")
        return jsonify({"response": result, "success": True})

    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500


if __name__ == '__main__':
    print(f"\n🚀 Starting server at: http://{config.FLASK_HOST}:{config.FLASK_PORT}\n")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=True
    )
