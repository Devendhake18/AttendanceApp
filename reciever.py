from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    file.save(f'D:/CODDING STUFF/Sem 5/JF_NGO_APP/trail{file.filename}')
    
    return jsonify({"message": "File uploaded successfully"}), 201

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Target PC is online"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
