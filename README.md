# API-Hasher

API-Hasher is a simple web application built with Flask (Python) that provides a user interface and a RESTful API endpoint for generating SHA-256 hashes from text input.

## Features

*   **Web Interface:** A clean and responsive UI to manually input text and get its SHA-256 hash.
*   **API Endpoint:** A `/api/hash` endpoint for programmatic hash generation.
*   **SHA-256 Algorithm:** Uses the standard SHA-256 hashing algorithm.
*   **Responsive Design:** The web interface is designed to work on various screen sizes.
*   **Error Handling:** Provides basic error messages for both UI and API interactions.

### User Interface Preview

![API-Hasher User Interface Screenshot](docs/images/api_hasher_ui.png)

## Prerequisites

*   Python 3.7+
*   pip (Python package installer)

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/moeindavarzani/API-Hasher.git
cd API-Hasher
```

### 2. Create and Activate a Virtual Environment (Recommended)

It's highly recommended to use a virtual environment to manage project dependencies.

**On macOS and Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

With the virtual environment activated, install the required packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will start, typically on `http://127.0.0.1:5000/`. Open this URL in your web browser to access the UI.

## Web Interface Usage

1.  Navigate to `http://127.0.0.1:5000/` in your browser.
2.  Enter the text or code you want to hash into the text area.
3.  Click the "Calculate Hash" button.
4.  The original text (if provided) and its SHA-256 hash will be displayed.
5.  You can use the "Copy" button to copy the hash to your clipboard.

## API Usage

The application provides a RESTful API endpoint for generating hashes programmatically.

*   **Endpoint:** `/api/hash`
*   **Method:** `POST`
*   **Content-Type:** `application/json`

### Request Body

The request body must be a JSON object containing a `text` field:

```json
{
  "text": "Your string to hash"
}
```

### Example Request (using `curl`)

```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"hello world"}' http://127.0.0.1:5000/api/hash
```

### Success Response (200 OK)

If successful, the API will return a JSON object with the original text and its SHA-256 hash:

```json
{
  "original_text": "hello world",
  "hashed_value": "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
}
```

### Error Responses

*   **400 Bad Request:**
    *   If the request `Content-Type` is not `application/json`.
    *   If the JSON data is invalid or missing.
    *   If the `text` field is missing in the JSON data.
    *   If the `text` field is not a string.
    *   If the `text` field is empty or consists only of whitespace.
*   **500 Internal Server Error:**
    *   In case of an unexpected server-side error during hash calculation (rare).

## Project Structure

```
API-Hasher/
├── docs/
│   └── images/
│       └── api_hasher_ui.png
├── app.py              # Main Flask application file, includes API logic
├── static/             # Static files (CSS, JavaScript)
│   ├── script.js
│   └── style.css
├── templates/          # HTML templates
│   └── index.html
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── LICENSE             # Project license information
├── README.md           # This file
└── requirements.txt    # Project dependencies
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or find any issues, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.