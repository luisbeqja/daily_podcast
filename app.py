from flask import Flask, jsonify, request

from llm.llm import get_response

app = Flask(__name__)

""" @app.route('/api/podcast/first-episode', methods=['GET'])
def first_episode():
    data = request.json
    response = get_response(data["query"])
    return jsonify({"message": response}) """



#TEST
@app.route('/api/podcast/first-episode', methods=['GET'])
def first_episode():
    """Handle incoming Telegram updates via webhook."""
    
    response = get_response("Mussolini was a great leader ?")
    return jsonify({"message": response})