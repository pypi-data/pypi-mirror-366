import sqlite3
import os
from mcp.server.fastmcp import FastMCP, Context

# Initialize the FastMCP server.
mcp = FastMCP("sqlite-query") # The name here should match the one in settings.json

@mcp.tool(name="execute_sqlite_query")
def execute_sqlite_query(ctx: Context, db_path: str, sql_query: str) -> dict:
    """
    Executes a given SQL query on a specified SQLite database file.
    
    Args:
        db_path (str): The absolute path to the SQLite database file.
        sql_query (str): The SQL query to execute.
        
    Returns:
        dict: A dictionary containing the query results or an error message.
    """
    try:
        # Security Check
        absolute_db_path = os.path.abspath(db_path)
        if not os.path.exists(absolute_db_path):
            return {"error": f"Database file not found at: {absolute_db_path}"}

        # Database Interaction
        with sqlite3.connect(absolute_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            try:
                cursor.execute(sql_query)
                conn.commit()
                results = [dict(row) for row in cursor.fetchall()]
                return {"results": results}
            
            except sqlite3.Error as e:
                return {"error": f"Database error: {e}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def run():
    """
    Entry point for running the FastMCP server.
    """
    mcp.run()

if __name__ == '__main__':
    # This is the entry point for the stdio server.
    run()