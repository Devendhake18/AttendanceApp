import requests

# URL of the server
server_url = 'http://192.168.1.3:5000'  # Replace with the actual server IP address

# File to be uploaded
file_path = r"C:\Users\deven\Downloads\CN_Experiment3.pdf"

def upload_image(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f)}
            response = requests.post(f'{server_url}/upload', files=files)
            print(response.json())
    except Exception as e:
        print(f"An error occurred during file upload: {e}")

def check_and_transfer():
    try:
        response = requests.get(f'{server_url}/check_and_transfer')
        print("Raw response content:", response.text)  # Print raw response content for debugging
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(json_response)
            except requests.exceptions.JSONDecodeError:
                print("Response is not valid JSON")
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.ConnectionError as e:
        print(f"Connection error occurred: {e}")

if __name__ == "__main__":
    upload_image(file_path)
    check_and_transfer()
