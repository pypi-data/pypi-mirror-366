import logging
from psycopg import AsyncConnection, AsyncCursor
from psycopg import sql
from re import compile

WHITESPACE = compile('\s')
async def async_exec_cypher(conn:AsyncConnection, graph_name:str, cypher_stmt:str, cols:list=None, params:tuple=None) ->AsyncCursor:
    if conn == None or conn.closed:
        raise Exception("Connection is not open or is closed")

    cursor:AsyncCursor = conn.cursor()
    #clean up the string for parameter injection
    cypher_stmt = cypher_stmt.replace("\n", "")
    cypher_stmt = cypher_stmt.replace("\t", "")

    # Simple parameter injection for backend-only use
    # (not sql injection safe)
    if params:
        cypher = cypher_stmt % params
    else:
        cypher = cypher_stmt
    
    cypher = cypher.strip()

    # prepate the statement (validates)
    preparedStmt = "SELECT * FROM age_prepare_cypher({graphName},{cypherStmt})"
    cursor: AsyncCursor = conn.cursor()
    try:
        await cursor.execute(sql.SQL(preparedStmt).format(graphName=sql.Literal(graph_name),cypherStmt=sql.Literal(cypher)))
    except SyntaxError as cause:
        await conn.rollback()
        raise cause
    except Exception as cause:
        await conn.rollback()
        raise Exception("Execution ERR[" + str(cause) +"](" + preparedStmt +")") from cause

    # build and execute the cypher statement
    stmt = build_cypher(graph_name, cypher, cols)
    cursor: AsyncCursor = conn.cursor()
    try:
        await cursor.execute(stmt)
        return cursor
    except SyntaxError as cause:
        await conn.rollback()
        raise cause
    except Exception as cause:
        await conn.rollback()
        raise Exception("Execution ERR[" + str(cause) +"](" + stmt +")") from cause

# From apache age official repository
def build_cypher(graphName:str, cypherStmt:str, columns:list) ->str:
    if graphName == None:
        raise Exception("Graph name cannot be None")
    
    columnExp=[]
    if columns != None and len(columns) > 0:
        for col in columns:
            if col.strip() == '':
                continue
            elif WHITESPACE.search(col) != None:
                columnExp.append(col)
            else:
                columnExp.append(col + " agtype")
    else:
        columnExp.append('v agtype')

    stmtArr = []
    stmtArr.append("SELECT * from cypher(NULL,NULL) as (")
    stmtArr.append(','.join(columnExp))
    stmtArr.append(");")
    return "".join(stmtArr)

async def async_graph_exists(conn:AsyncConnection, graph_name: str) -> bool:
    """Check if the AGE graph with the given name exists."""
    try:
        query = f"SELECT * FROM ag_graph WHERE name = '{graph_name}';"
        async with conn.cursor() as cur:
            await cur.execute(query)
            result = await cur.fetchone()
            return result is not None
    except Exception:
        logging.error(f"Error checking if graph {graph_name} exists", exc_info=True)
        return False


async def async_create_graph(conn:AsyncConnection, graph_name: str):
    try:
        query = f"SELECT create_graph('{graph_name}');"
        async with conn.cursor() as cur:
            await cur.execute(query)
        return True
    except Exception:
        logging.error(f"Error creating graph: {graph_name}", exc_info=True)
        return False


async def async_drop_graph(conn:AsyncConnection, graph_name: str):
    try:
        query = f"SELECT drop_graph('{graph_name}', true);"
        async with conn.cursor() as cur:
            await cur.execute(query)
        return True
    except Exception:
        logging.error(f"Error dropping graph: {graph_name}", exc_info=True)
        return False
