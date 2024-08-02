from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import requests
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Flask(__name__)

# Azure Blob Storage configuration
connect_str = "DefaultEndpointsProtocol=https;AccountName=jfngo;AccountKey=hT9ePXALJj5/uOA2p/6s/1ZhL5n0K6e3Wl0plTbtCm6smaTSI4cZ8BuHtbiwJXeS6SF82domDRz++ASt3PVOcQ==;EndpointSuffix=core.windows.net"
container_name = "file-transfer"

blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

# Directory where files are stored locally (for download and list files)
DOWNLOADS_DIRECTORY = r"C:\\"

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    try:
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(file, overwrite=True)  # Added overwrite=True to handle duplicate uploads
        return jsonify({"message": "File uploaded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/file-transfer/<file_name>', methods=['GET'])
def download_file(file_name):
    try:
        # Download file from Azure Blob Storage
        blob_client = container_client.get_blob_client(file_name)
        download_file_path = os.path.join(DOWNLOADS_DIRECTORY, file_name)
        
        # Create the directory if it does not exist
        if not os.path.exists(DOWNLOADS_DIRECTORY):
            os.makedirs(DOWNLOADS_DIRECTORY)
        
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        # Return the file to the client
        return send_file(download_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    try:
        blobs = [blob.name for blob in container_client.list_blobs()]
        return jsonify({"files": blobs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_and_transfer', methods=['GET'])
def check_and_transfer():
    try:
        target_pc_url = "https://jfngo.azurewebsites.net"  # Your Azure Web App URL

        # Check if target PC (Azure Web App) is online using HTTP request
        try:
            response = requests.get(target_pc_url)
            target_online = response.status_code == 200
        except requests.RequestException:
            target_online = False

        if not target_online:
            return jsonify({"message": "Target PC is offline"}), 200

        # If target PC is online, transfer files
        blobs = [blob.name for blob in container_client.list_blobs()]
        if not os.path.exists(DOWNLOADS_DIRECTORY):
            os.makedirs(DOWNLOADS_DIRECTORY)
        for blob_name in blobs:
            blob_client = container_client.get_blob_client(blob_name)
            download_file_path = os.path.join(DOWNLOADS_DIRECTORY, blob_name)
            with open(download_file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

        return jsonify({"message": "Files transferred successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error occurred", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
