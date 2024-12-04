import requests

# TeamCity REST API endpoint to get project parameters
url = "https://teamcity.test-digital.com/httpAuth/app/rest/projects/HelloWorldTC/parameters"

# Authentication credentials
auth = ("test", "test")  # Replace with your TeamCity username and password
headers = {
    'Accept': 'application/json'
}
# Fetch project parameters using GET request
response = requests.get(url, auth=auth,headers=headers)
if response.status_code == 200:
    print(response.json()['property'])
else:
    print(f"Failed to get parameters: {response.status_code} - {response.text}")
