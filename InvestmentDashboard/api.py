from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def root():
    return jsonify({
        "status": "healthy",
        "message": "Minimal API is running correctly!"
    })

@app.route("/api/test")
def test_endpoint():
    return jsonify({
        "message": "Minimal API test endpoint is reachable!"
    })

if __name__ == "__main__":
    # This part is for local testing, Zeabur will use Gunicorn
    app.run(debug=True, port=5001)