from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/verify', methods=['POST'])
def fishab():
    # Simple test response
    return jsonify({"message": "fishab function called successfully!"})

if __name__ == '__main__':
    app.run(debug=True)