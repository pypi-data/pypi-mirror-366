import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from mtbs.mtbs import Mtbs
load_dotenv()

mcp = FastMCP("mtbs")
environment = os.getenv("MTBS_ENV", "prd")
print(f"Using environment: {environment}")
_mtbs = Mtbs(env=environment, cookie_file_path=os.getenv("MTBS_COOKIE_FILE", None))


@mcp.tool()
async def databases_list():
    """
    List all databases available in the MTBS system.
    
    Returns:
        dict: A dictionary containing the list of databases.
        [
            "dabase_name": id_database,
        ]
    """
    return _mtbs.databases_list()


@mcp.tool()
async def sql(query: str, database: int):
    """
    Execute a SQL query on the specified database.
    
    Args:
        query (str): The SQL query to execute.
        database (int): The ID of the database to query.
    
    Returns:
        str: The result of the SQL query.
    """
    return _mtbs.send_sql(query=query, database=database, raw=False, cache_enabled=True)

def main_stdio():
    """
    Main function to run the MCP server.
    """
    mcp.run(transport="stdio")

def main_sse():
    mcp.run(transport="sse")

if __name__ == "__main__":
    print("JJJJJJ")
    #main()

    #  "mcp-server": {
    #         "command": "/usr/bin/uv",
    #         "args": [
    #             "--directory",
    #             "/home/ruddy/dev/workspaces/bpifrance/python/mtbs",
    #             "run",
    #             "mcp"
    #         ]
    #     }
