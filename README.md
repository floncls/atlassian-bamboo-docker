# atlassian-bamboo-docker
## Running Atlassian Bamboo on Docker

* Connection from pgadmin to the postgres database and create database called bamboo.
* Put the required informations in the correct field.
* Configure Bamboo database field at the first connexion for my case, I configured it like this :
    ```
    Connection type Connect using JDBC
    Driver class name org.postgresql.Driver
    Database URL  jdbc:postgresql://atlassian-postgres:5432/bamboo
    User name postgres
    Password  postgres
    ```

## Managing configuration with API 
### Fetching a plan configuration from a Bamboo Project
* Use the scripts `fetch_all_plans.py` or `fetch_plan.py` in order to do so
* Make sure to generate your Token via Bamboo GUI:  Go to Profile > Personal access token > Click on generate access token > Use it to the through the script
* Make sure to justify the correct Project and Plan name

## Exporting Bamboo Projects configurations
This Python script exports project and plan data from a Bamboo server to a CSV file. The data includes information about projects, plans, and the YAML configuration associated with each plan. It interacts with the Bamboo REST API to retrieve and format the necessary details.

### Features

- **Project Data Retrieval**: Fetches details about projects and their associated plans.
- **Plan Details Fetching**: For each plan, retrieves detailed information, including the YAML configuration of the plan.
- **CSV Export**: Outputs the fetched data to a CSV file, including project name, project key, plan key, plan name, and YAML configuration of the plan.
- **YAML Code Formatting**: Formats the YAML configuration by cleaning up line breaks and backslashes for better readability.

### Requirements

- Python 3.x
- `requests` 
- `csv`
- `os`
- `datetime`

You can install the required dependencies using pip:

```bash
pip install requests
```

## How to run?
In the folder called **scripts** you'll find the file called *fetch_all_plan.py*.  This is the main one.  Another file called *fetch_plan.py* is also available but not advised as it has not been thought to be used with 'automation'.  The *fetch_all_plan.py*  is far more complete to retrieve an entire configuration and the other one is here in case you need to fetch only one plan out of the other.

You can use it by using Python in a terminal as shown below:
```bash
python3 fetch_all_plans.py
```
Follow the instructions and provide the correct informations.