from flask import Flask, request, jsonify, send_file
import os
import requests
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

# Azure Blob Storage configuration
connect_str = "DefaultEndpointsProtocol=https;AccountName=jfngo;AccountKey=hT9ePXALJj5/uOA2p/6s/1ZhL5n0K6e3Wl0plTbtCm6smaTSI4cZ8BuHtbiwJXeS6SF82domDRz++ASt3PVOcQ==;EndpointSuffix=core.windows.net"
container_name = "file-transfer"

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
        blob_client.upload_blob(file, overwrite=True)  # Added overwrite=True to handle duplicate uploads
        return jsonify({"message": "File uploaded successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<file_name>', methods=['GET'])
def download_file(file_name, download_path="C://Users//Public//Downloads//"):
    # download_path = request.args.get('download_path')
    if not download_path:
        return jsonify({"error": "Download path not provided"}), 400

    try:
        # Download file from Azure Blob Storage
        blob_client = container_client.get_blob_client(file_name)
        download_file_path = os.path.join(download_path, file_name)
        
        # Create the directory if it does not exist
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        # Return the file to the client
        #blob_client.delete_blob()
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
    
def delete_blob(blob_name):
    """Deletes a blob from the container."""
    try:
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
        return True
    except Exception as e:
        print(f"An error occurred while deleting blob {blob_name}: {e}")
        return False

@app.route('/delete/<file_name>', methods=['DELETE'])
def delete_file(file_name):
    try:
        delete_success = delete_blob(file_name)
        if delete_success:
            return jsonify({"message": f"File {file_name} deleted successfully"}), 200
        else:
            return jsonify({"error": f"Failed to delete file {file_name}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_and_transfer', methods=['GET'])
def check_and_transfer():
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
    for blob_name in blobs:
        blob_client = container_client.get_blob_client(blob_name)
        download_file_path = os.path.join(download_path, blob_name)
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

    return jsonify({"message": "Files transferred successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
