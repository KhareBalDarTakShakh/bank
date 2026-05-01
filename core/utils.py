from django.db import connection

def call_procedure(proc_name, *args):
    """
    Call a stored procedure that returns a single result set.
    Returns a list of dictionaries (one per row) where keys are column names.
    For procedures that do NOT return a result set (INSERT/UPDATE/DELETE),
    returns an empty list.
    """
    with connection.cursor() as cursor:
        cursor.callproc(proc_name, args)
        if cursor.description:  # there is a result set
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return []

def execute_query(query, params=None):
    """
    Execute a raw SELECT query and return a list of dictionaries.
    Use this for quick ad‑hoc queries (e.g., fetching a single row by id).
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return []

def fetch_one(table, id):
    """
    Fetch a single row from any table by primary key 'id'.
    Returns a dictionary or None.
    """
    query = f"SELECT * FROM `{table}` WHERE id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, [id])
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))
        return None