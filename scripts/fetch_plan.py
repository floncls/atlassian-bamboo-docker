import requests
import yaml
import os
from datetime import datetime


def fetch_data_from_api(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"Error: {err}")
    return None


def convert_json_to_yaml(json_data):
    try:
        yaml_data = yaml.dump(json_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return yaml_data
    except Exception as e:
        print(f"Error during JSON to YAML conversion: {e}")
    return None


def save_yaml_to_file(yaml_data, folder_path, base_name):
    if yaml_data:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        file_name = f"{timestamp}-{base_name}.yaml"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'w') as file:
            file.write(yaml_data)
        print(f"YAML file saved at: {file_path}")
    else:
        print("No data to save.")


def main():
    url = 'http://localhost:8085/rest/api/latest/plan/TEST-TEST/specs?format=yaml'
    headers = {
        'Authorization': 'Bearer <>',
        'Accept': 'application/json'
    }

    data_json = fetch_data_from_api(url, headers)
    yaml_output = convert_json_to_yaml(data_json)

    parsed_yaml = yaml.safe_load(yaml_output)
    if "spec" in parsed_yaml and "code" in parsed_yaml["spec"]:
        raw_code = parsed_yaml["spec"]["code"]
        formatted_code = raw_code.replace("\\n", "\n")
        parsed_yaml["spec"]["code"] = formatted_code
        folder_path = '../bamboo_export'
        base_name = 'plan_config'

        save_yaml_to_file(formatted_code, folder_path, base_name)



if __name__ == "__main__":
    main()