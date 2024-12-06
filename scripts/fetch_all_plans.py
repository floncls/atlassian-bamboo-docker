import csv
import requests
import os
from datetime import datetime


def fetch_project_data_from_api(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()["projects"]["project"]
    return data

def fetch_plan_details(base_url, headers,project_key, plan_key):
   url = f"{base_url}/rest/api/latest/plan/{project_key}-{plan_key}"
   response = requests.get(url, headers=headers)
   response.raise_for_status()
   return response.json()

def fetch_plan_data_from_api(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"Error: {err}")
    return None

def format_yaml_conf(json_data):
    try:
        if "spec" in json_data and "code" in json_data["spec"]:
            raw_code = json_data["spec"]["code"]
            formatted_code = raw_code.replace("\\n", "\n").replace("\\", "")
            json_data["spec"]["code"] = formatted_code

        return json_data["spec"]["code"]
    except Exception as e:
        print(f"Error during code block formatting: {e}")
        return None


def process_exportation_in_excel(url, base_url, headers, folder_path, base_name):
    data = fetch_project_data_from_api(url, headers=headers)
    if not data:
        print("No project data found.")
        return

    projects_list = []
    project_data = []

    for project in data:
        if project["key"] not in projects_list:
            projects_list.append(project["key"])
        project_data.append(project)

    rows = []

    for project in projects_list:
        project_url = f"{base_url}/rest/api/latest/project/{project}?expand=plans.plan"
        res = fetch_plan_data_from_api(project_url, headers)

        if res and "plans" in res and "plan" in res["plans"]:
            for plan in res["plans"]["plan"]:
                plan_short_key = plan["shortKey"]
                plan_key = plan["key"]
                plan_name = plan["name"]
                plan_short_name = plan["shortName"]

                plan_details = fetch_plan_details(base_url, headers, project, plan_short_key)

                if plan_details:
                    project_name = plan_details.get("projectName", "Unknown")

                    config_url = f"{base_url}/rest/api/latest/plan/{project}-{plan_short_key}/specs?format=yaml"
                    config = fetch_plan_data_from_api(config_url, headers)
                    if config:
                        yaml_output = format_yaml_conf(config)
                        if yaml_output:
                            row = [
                                project_name,
                                project,
                                plan_key,
                                plan_short_key,
                                plan_name,
                                plan_short_name,
                                yaml_output
                            ]
                            rows.append(row)

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    csv_file_path = os.path.join(folder_path, f"{timestamp}-{base_name}_export.csv")

    if rows:
        try:
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    "projectName",
                    "projectKey",
                    "planKey",
                    "planShortKey",
                    "planName",
                    "planShortName",
                    "Yaml configuration"
                ])
                writer.writerows(rows)
            print(f"CSV file saved at: {csv_file_path}")
        except Exception as e:
            print(f"Error saving CSV file: {e}")
    else:
        print("No data to write to CSV.")


def main():
    token = input("Access token :  ")
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    base_url = input("Bamboo base url : ")
    url = f"{base_url}/rest/api/latest/project/"
    folder_path = "../bamboo_export"
    base_name = "project_export"

    process_exportation_in_excel(url, base_url, headers, folder_path, base_name)



if __name__ == "__main__":
    main()
