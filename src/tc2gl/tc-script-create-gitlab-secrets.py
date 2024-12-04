import requests
import os

TOKEN = os.environ.get('TOKEN')

def store_secret(key, value, headers):
    url = "https://gitlab.com/api/v4/projects/58422563/variables"
    print(f"Secret value to be stored '{key}' '{value}'")

    data = {
        "key": key,
        "value": value,
        "protected": False,
        "masked": False
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Secret '{key}' stored successfully.")
    else:
        print(f"Failed to store secret '{key}': {response.status_code} {response.text}")

def main(file_path):
    headers = {
        f"PRIVATE-TOKEN": "{TOKEN}",
        "Content-Type": "application/json"
    }

    with open(file_path, 'r') as file:
        for line in file:
            # Strip whitespace and split the line into key and value
            key_value = line.strip().split('=', 1)
            if len(key_value) == 2:
                key, value = key_value
                # Replace dots with underscores in the key
                key = key.replace('.', '_')
                store_secret(key, value, headers)
            else:
                print(f"Invalid line format: '{line.strip()}'")

if __name__ == "__main__":
    main("/opt/buildagent/temp/buildTmp/teamcity.subset.config.parameters")
