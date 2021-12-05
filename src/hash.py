import hashlib
import requests
import json
import time

def requestWithErrorHandling(request_type):
    try:
        r = requests.request(request_type, url, headers=headers)
    except requests.exceptions.Timeout:
        print("Request timed out!")
    except requests.exceptions.TooManyRedirects:
        print("Invalid request URL!")
    except requests.exceptions.RequestException as e:
        print("Unexpected request behavior!")
        raise SystemExit(e)
    return r

filename = input("Enter file path: ")
api_key = ""
with open(filename,"rb") as file:
    file_bytes = file.read()
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
   
url = f"https://api.metadefender.com/v4/hash/{sha256_hash}"
headers = {
 "apikey": "{}".format(api_key)
}

response = requestWithErrorHandling("GET")
data = response.json()
# metadefender's hash not found code is 404003

if 'error' in data.keys() and data['error']['code'] == 404003:
    #file upload
    url = "https://api.metadefender.com/v4/file"
    headers = {
    "apikey": "{}".format(api_key),
    "Content-Type": "application/octet-stream"
    }
    with open(filename,"rb") as file:
        file_bytes = file.read()
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        payload = file_bytes

    response = requestWithErrorHandling("POST")
    data = response.json()
    
    #pull response from data id'
    waiting_time = 1
    while 'status' in data.keys() and data['status'] == "inqueue":
        time.sleep(waiting_time)
        url = "https://api.metadefender.com/v4/file/{}".format(data['data_id'])
        headers = {
        "apikey": "{}".format(api_key),
        "x-file-metadata": "0"
        }

        response = requestWithErrorHandling("GET")
        
        data = response.json()
        waiting_time = waiting_time*1.5
    print('Processing...')    
    while 'process_info' in data.keys() and data['process_info']['progress_percentage'] != 100:
        time.sleep(waiting_time)
        url = "https://api.metadefender.com/v4/file/{}".format(data['data_id'])
        headers = {
        "apikey": "{}".format(api_key),
        "x-file-metadata": "0"
        }
        print()
        response = requestWithErrorHandling("GET")
        
        data = response.json()
        waiting_time = waiting_time*1.5 
else:
    print("Found cashed file")            
            

print("Filename: "+filename)
print("Overall result: "+data["scan_results"]["scan_all_result_a"])
for key in data["scan_results"]["scan_details"]:
    print("Engine: "+key)
    for subkey in data["scan_results"]["scan_details"][key]:
        print("{}: {}".format(subkey,data["scan_results"]["scan_details"][key][subkey]))