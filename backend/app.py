from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from retriever import MedicalRetriever
from ollama_client import list_models
import config
import os

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)



# Initialize medical retriever safely (allow selecting defaults from config)
retriever = None
try:
    # MedicalRetriever now expects only llm_model (embedding is fixed in config)
    retriever = MedicalRetriever(llm_model=config.LLM_MODEL_NAME)
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

# Models endpoints
def _is_embedding_model(name: str) -> bool:
    if not name:
        return False
    n = name.lower()
    # Exclude explicit known embedding model from config and any model with 'embed' or 'embedding' in the name
    if n == (config.EMBED_MODEL_NAME or "").lower():
        return True
    if 'embed' in n or 'embedding' in n:
        return True
    return False


@app.route('/models', methods=['GET'])
def get_models():
    """Return available generative models (filter out embedding models).

    Simpler behavior: call Ollama live and return an empty list on error so the UI can display a friendly message
    instead of surfacing a server error.
    """
    try:
        # Directly call Ollama just like debug_models does
        url = config.OLLAMA_BASE_URL.rstrip("/") + "/api/tags"
        import requests
        r = requests.get(url, timeout=5)
        
        if r.status_code != 200:
            print(f"⚠️ Ollama /api/tags returned {r.status_code}")
            return jsonify({"models": [], "state": {}, "success": True})
        
        try:
            data = r.json()
        except ValueError:
            print("⚠️ Ollama /api/tags response not JSON")
            return jsonify({"models": [], "state": {}, "success": True})
        
        # Extract model names from Ollama response
        raw_models = []
        if isinstance(data, dict) and "models" in data:
            for item in data["models"]:
                if isinstance(item, dict) and "name" in item:
                    raw_models.append(item["name"])
        
        print(f"📋 Raw models from Ollama: {raw_models}")
        
        # Filter out embedding models
        models = [m for m in raw_models if not _is_embedding_model(m)]
        print(f"✅ Filtered models (embedding excluded): {models}")
        
        state = retriever.get_state() if retriever else {}
        return jsonify({
            "models": models,
            "state": state,
            "success": True
        })
    except Exception as e:
        print(f"❌ Error in get_models: {e}")
        return jsonify({"models": [], "state": {}, "success": True})


@app.route('/debug_models', methods=['GET'])
def debug_models():
    """Diagnostic endpoint: return raw status and body from Ollama `/api/tags` endpoint."""
    try:
        url = config.OLLAMA_BASE_URL.rstrip("/") + "/api/tags"
        import requests
        r = requests.get(url, timeout=5)
        result = {"status_code": r.status_code}
        try:
            result["json"] = r.json()
        except Exception:
            result["text"] = r.text[:2000]
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route('/models', methods=['POST'])
def set_models():
    """Set the LLM model at runtime (embeddings remain a single configured model).

    Simpler behavior: accept a single string for 'llm_model' and try to apply it directly. If applying fails,
    return a clear error. We no longer try to validate against cached lists first.
    """
    try:
        data = request.get_json() or {}
        new_llm = data.get('llm_model')

        if not retriever:
            return jsonify({'error': 'Retriever not initialized', 'success': False}), 500

        if not isinstance(new_llm, str):
            return jsonify({'error': 'llm_model must be a string', 'success': False}), 400

        # Attempt to apply the model directly; retriever.update_llm will raise if invalid
        try:
            retriever.update_llm(new_llm)
        except Exception as e_apply:
            print(f"❌ Failed to apply LLM '{new_llm}': {e_apply}")
            return jsonify({'error': f"Failed to apply model: {str(e_apply)}", 'success': False}), 400

        config.LLM_MODEL_NAME = new_llm
        config.SELECTED_LLM_MODELS = [new_llm]

        state = retriever.get_state()
        return jsonify({'state': state, 'success': True})

    except Exception as e:
        print(f"❌ Error setting models: {e}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500


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
