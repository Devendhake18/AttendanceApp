from flask import Flask, request, jsonify
import os
import socket
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = Flask(__name__)

# Azure Blob Storage configuration
connect_str = "DefaultEndpointsProtocol=https;AccountName=jfngo;AccountKey=hT9ePXALJj5/uOA2p/6s/1ZhL5n0K6e3Wl0plTbtCm6smaTSI4cZ8BuHtbiwJXeS6SF82domDRz++ASt3PVOcQ==;EndpointSuffix=core.windows.net"  # Replace with your Azure Storage connection string
container_name = "file-transfer"  # Replace with your container name

blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    try:
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(file)
        return jsonify({"message": "File uploaded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Target PC is online"}), 200

@app.route('/check_and_transfer', methods=['GET'])
def check_and_transfer():
    try:
        target_pc_ip = "http://192.168.1.3:5000"  # Replace with the actual IP address of the target PC
        target_pc_port = 5000

        # Check if target PC is online
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect((target_pc_ip, target_pc_port))
            s.close()
            target_online = True
        except socket.error:
            target_online = False

        if not target_online:
            return jsonify({"message": "Target PC is offline"}), 200

        # If target PC is online, transfer files
        blobs = [blob.name for blob in container_client.list_blobs()]
        for blob_name in blobs:
            blob_client = container_client.get_blob_client(blob_name)
            download_file_path = os.path.join("downloads", blob_name)
            with open(download_file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

        return jsonify({"message": "Files transferred successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error occurred", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
