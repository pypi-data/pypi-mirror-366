import logging
import re
from typing import Dict, Any, Optional, List, Annotated
from pydantic import BaseModel, AfterValidator
from psycopg import Connection, Cursor
from psycopg.errors import SyntaxError as PgSyntaxError

WHITESPACE = re.compile('\s')
_SQL_INVALID_CHARS = re.compile(r"[\x00-\x1F]")  # ASCII control characters

def _escape_cypher_string(s:str)->str:
    return s.replace("\\", "\\\\").replace("'", "\\'")

def _coerce_values_as_str(params: Dict[str, Any]) -> Dict[str, str]:
    """Pure function to validate that Cypher param values have a valid string representation."""

    result = {}
    for key, value in params.items():
        if not isinstance(value, str):
            try:
                result[key] = str(value)
            except Exception as e:
                raise ValueError(
                    f"Invalid value for parameter '{key}': {value}. Value cannot be cast to a string."
                ) from e
        else:
            result[key] = value
    
    return result

def _sanitize_param_strs(params: Dict[str,str]) -> Dict[str,str]:
    """Coerce values to valid SQL strings, escaping single quotes."""
    result = {}
    for key, value in params.items():
        if not isinstance(value, str):
            raise ValueError(f"Invalid value for parameter '{key}': {value}. Value must be a string.")
          
        clean = _SQL_INVALID_CHARS.sub('', value)
        escaped = _escape_cypher_string(clean)
        result[key] = escaped

    return result

class CypherParams(BaseModel):
    """Model for Cypher parameters with strict validation."""
    params: Annotated[Dict[str,Any], AfterValidator(_coerce_values_as_str), AfterValidator(_sanitize_param_strs)] = None

    def __getitem__(self, key):
        return self.params[key]

    def __iter__(self):
        return iter(self.params)

    def __len__(self):
        return len(self.params)
    
    def get(self, key, default=None):
        return self.params.get(key, default)

    def items(self):
        return self.params.items()
    
def exec_cypher(cursor:Cursor, graph_name:str, cypher_stmt:str, params:Optional[CypherParams]=None, cols:Optional[List[str]]=None) -> Cursor :
    
    if cursor == None or cursor.closed:
        raise Exception("Connection is not open or is closed")

    if graph_name is None:
        raise Exception("Graph name cannot be None")

    #clean up the string for parameter injection
    cypher_stmt = cypher_stmt.replace("\n", "")
    cypher_stmt = cypher_stmt.replace("\t", "")

    # Simple parameter injection for backend-only use
    if params:
        cypher = cypher_stmt % params
    else:
        cypher = cypher_stmt
    
    cypher = cypher.strip()

    # build and execute the cypher statement
    stmt = _build_cypher(graph_name, cypher, cols)

    try:
        return cursor.execute(stmt)
    except PgSyntaxError as cause:
        raise cause
    except Exception as cause:
        raise Exception("Execution error in statement execution: ERR[" + str(cause) +"](" + stmt +")") from cause

def _build_cypher(graph_name:str, cypher_stmt:str, columns:Optional[List[str]]) ->str:
    if graph_name == None:
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

    return f"SELECT * FROM cypher('{graph_name}',$${cypher_stmt}$$) AS ({','.join(columnExp)});"

def graph_exists(conn: Connection, graph_name: str) -> bool:
    """Check if the AGE graph with the given name exists."""
    try:
        query = f"SELECT * FROM ag_graph WHERE name = '{graph_name}';"
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            return result is not None
    except Exception:
        logging.error(f"Error checking graph existence: {graph_name}")
        return False


def create_graph(conn: Connection, graph_name: str) -> bool:
    """Create the AGE graph if it doesn't exist."""
    try:
        query = f"SELECT create_graph('{graph_name}');"
        with conn.cursor() as cur:
            cur.execute(query)
        return True
    except Exception:
        logging.error(f"Error creating graph: {graph_name}", exc_info=True)
        return False


def drop_graph(conn: Connection, graph_name: str) -> bool:
    """Drop the AGE graph."""
    try:
        query = f"SELECT drop_graph('{graph_name}', true);"
        with conn.cursor() as cur:
            cur.execute(query)
        return True
    except Exception:
        logging.error(f"Error dropping graph: {graph_name}", exc_info=True)
        return False
