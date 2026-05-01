from django.db import connection

def call_procedure(proc_name, *args):
    """
    Call a stored procedure using a parameterised CALL statement.
    Returns a list of dicts (empty for DML procedures).
    """
    with connection.cursor() as cursor:
        placeholders = ', '.join(['%s'] * len(args))
        sql = f"CALL {proc_name}({placeholders})"
        cursor.execute(sql, args)
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return []

def execute_query(query, params=None):
    """
    Execute a raw SELECT query and return a list of dicts.
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