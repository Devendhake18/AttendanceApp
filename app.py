from flask import Flask, request, send_file, jsonify
from azure.storage.blob import BlobServiceClient
from io import BytesIO

app = Flask(__name__)

# Azure Blob Storage configuration
connect_str = "DefaultEndpointsProtocol=https;AccountName=janvhifoundation;AccountKey=JQJvNGJt8WGKMbloya263awqkqwcxT9GbHAeGTyRgXETfOApifCxyOMqCP0JBGpeSP1nAAq1YIi8+ASt9w9WFQ==;EndpointSuffix=core.windows.net"
container_name = "file-transfer"

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)
        blob_client.upload_blob(file, overwrite=True)
        return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_image(filename):
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
        download_stream = blob_client.download_blob()
        return send_file(BytesIO(download_stream.readall()), download_name=filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list_blobs', methods=['GET'])
def list_blobs():
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()
        blobs = [blob.name for blob in blob_list]
        return jsonify({"blobs": blobs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
