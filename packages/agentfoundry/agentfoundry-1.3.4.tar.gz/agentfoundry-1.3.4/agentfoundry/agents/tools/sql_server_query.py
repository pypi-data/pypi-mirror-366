import pyodbc
import json

from langchain_core.tools import Tool


def sql_query_executor(config_json: str):
    """
    Execute a SQL query using connection parameters from a JSON string.

    Args:
        config_json (str): JSON string with connection parameters.
            Example:
            {
                "server": "localhost\\SQLEXPRESS",
                "database": "master",
                "username": "sa",
                "password": "your_password",
                "driver": "ODBC Driver 17 for SQL Server",
                "trust": True,
                "query": "SQL Query to execute"
            }
    Returns:
        str: Query result or error message.
    """
    try:
        config = json.loads(config_json)

        conn_str = (
            f"DRIVER={{{config['driver']}}};"
            f"SERVER={config['server']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
        )
        if config["database"]:
            conn_str += f"DATABASE={config['database']};"
        if config['trust']:
            conn_str += "TrustServerCertificate=Yes;"
        query = config['query']
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return str(rows)
    except Exception as e:
        return f"Error executing query: {e}"


# Wrap the function as a LangChain Tool.
sqlite_tool = Tool(
    name="sql_server_query",
    func=sql_query_executor,
    description=(
        "Executes a SQL query on a SQL Server database using connection parameters provided in a JSON string. "
        "Input must include both the SQL query and the connection configuration in the following format:\n\n"
        "{\n"
        '  "server": "hostname\\\\SQLEXPRESS",\n'
        '  "database": "your_db",\n'
        '  "username": "your_user",\n'
        '  "password": "your_pass",\n'
        '  "driver": "ODBC Driver 17 for SQL Server",\n'
        '  "trust": boolean on whether to use TrustServerCertificate'
        '  "query": "query to execute"'
        "}\n\n"
        "Note: database can be optional if the user is creating the database in the query."
        "Returns the query result as a string. This tool is intended for direct SQL execution where the user provides full context."
    )
)

