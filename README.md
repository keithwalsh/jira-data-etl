# jira-data-etl

## Environment Setup

To get started, follow these steps to set up your environment:

1. **Clone the Repository:**

2. **Configure Environment Variables:**

-   Copy the `.env.example` file to create your own `.env` file:
    ```
    cp .env.example .env
    ```
-   Open the `.env` file in a text editor and fill in the necessary values.

3. **Environment Variables Explained:**

    Here's what each variable in the `.env` file means and the expected values:

-   **JIRA_API_TOKEN**: Your API token for authenticating with JIRA.
-   **JIRA_DOMAIN**: The domain of your JIRA instance (e.g., `yourcompany.atlassian.net`).
-   **MYSQL_HOST**: The hostname of your MySQL server (e.g., `localhost` or an IP address).
-   **MYSQL_PORT**: The port on which your MySQL server is running (default is `3306`).
-   **MYSQL_USER**: Your MySQL username.
-   **MYSQL_PASSWORD**: Your MySQL password.
-   **MYSQL_DATABASE**: The name of the MySQL database you are connecting to.
