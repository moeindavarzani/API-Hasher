from flask import Flask, render_template, request, jsonify, url_for
import hashlib

app = Flask(__name__)

def calculate_sha256_hash(input_string):
    """
    Calculates the SHA-256 hash of a given input string.

    Args:
        input_string (str): The string to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.
             Returns None if the input is not a string (this function
             primarily expects type validation to occur before calling).
    """
    if not isinstance(input_string, str):
        return None 
    encoded_text = input_string.encode('utf-8') # Input string must be encoded to bytes for hashing
    hasher = hashlib.sha256()
    hasher.update(encoded_text)
    return hasher.hexdigest()

@app.route('/', methods=['GET', 'POST'])
def index_page():
    """
    Renders the main HTML page for UI interaction and handles form submissions for hashing.

    On a GET request, it displays the form for text input.
    On a POST request, it processes the submitted text, calculates its SHA-256 hash,
    and re-renders the page displaying the original text, the calculated hash,
    or an error message if the input text is invalid (e.g., empty).

    Returns:
        str: The rendered HTML template ('index.html') populated with
             context variables including original_text, hashed_value, and error_message.
    """
    hashed_value = None
    original_text = None
    error_message = None

    if request.method == 'POST':
        original_text = request.form.get('inputText', '')
        if not original_text.strip(): # Validate that input text is not empty or just whitespace
            error_message = "Input text cannot be empty."
        else:
            hashed_value = calculate_sha256_hash(original_text)
            if hashed_value is None: 
                 # This path is unlikely if original_text is a valid string from the form.
                 # It primarily safeguards against unexpected issues in calculate_sha256_hash
                 # if it were called with a non-string type from another part of the code.
                 error_message = "Error calculating hash for the provided input."
                
    return render_template('index.html', 
                           original_text=original_text, 
                           hashed_value=hashed_value,
                           error_message=error_message)

@app.route('/api/hash', methods=['POST'])
def api_hash():
    """
    Provides a RESTful API endpoint for generating SHA-256 hashes.

    The endpoint expects a POST request with a JSON payload. The 'Content-Type'
    header must be 'application/json'. The JSON payload must contain a 'text'
    field, which holds the string to be hashed.

    Returns:
        flask.Response: A JSON response.
            - On success (HTTP 200): Contains 'original_text' and 'hashed_value'.
            - On client error (HTTP 400): Contains an 'error' message detailing the issue
              (e.g., wrong content type, malformed JSON, missing 'text' field,
              invalid 'text' field type, or empty 'text' field).
            - On server error (HTTP 500): Contains an 'error' message if an unexpected
              issue occurs during hash calculation.
    """
    if not request.is_json:
        return jsonify({"error": "Request content type must be application/json"}), 400

    data = request.get_json(silent=True) # Use silent=True to handle malformed JSON gracefully
    if data is None: # Check if JSON data is missing or could not be parsed
        return jsonify({"error": "Invalid or missing JSON data in request body"}), 400

    text_to_hash = data.get('text')

    if text_to_hash is None: 
        return jsonify({"error": "Missing 'text' field in JSON data"}), 400
    
    if not isinstance(text_to_hash, str):
        return jsonify({"error": "'text' field must be a string"}), 400

    if not text_to_hash.strip(): # Validate that 'text' field is not empty or just whitespace
        return jsonify({"error": "'text' field cannot be empty or consist only of whitespace"}), 400

    hashed_value = calculate_sha256_hash(text_to_hash)
    
    if hashed_value is None:
        # This indicates an unexpected internal issue if text_to_hash passed all previous type and content checks.
        return jsonify({"error": "Internal server error: Could not calculate hash"}), 500 

    return jsonify({
        "original_text": text_to_hash,
        "hashed_value": hashed_value
    }), 200

if __name__ == '__main__':
    app.run(debug=True)