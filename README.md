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
* Use the script `fetch_plan.py` in order to do so
* Make sure to generate your Token via Bamboo GUI:  Go to Profile > Personal access token > Click on generate access token > Use it to the through the script
* Make sure to justify the correct Project and Plan name