from db_conn import conn


# если fetch=True - запрос на выборку, нужно что-то вернуть, иначе запрос на изменение
# fetchone - если надо вернуть одну строку
def execute_sql(sql, select=True, fetchone=False):
    with conn() as database, database.cursor() as cursor:
        cursor.execute(sql)
        if select:
            if fetchone:
                return cursor.fetchone()
            else:
                cursor.fetchall()
        else:
            database.commit()
    return True


def is_user_new(user_id):
    sql_request = f'''
    select * from "user"
    where user_id = '{user_id}' 
    '''
    res = execute_sql(sql_request, fetchone=True)
    return not bool(res)


def get_user_tab_id_by_user_id(user_id):
    sql_requset = f"""
    select tab_id from "user"
    where user_id = '{user_id}'
    """
    res = execute_sql(sql_requset, fetchone=True)
    return res[0]


def create_user(user_id, username):
    if username == 'None':
        username = 'null'
    else:
        username = "'" + username + "'"
    sql_request = f'''
    INSERT INTO "user" (
    user_id, username, updated
    )
    VALUES (
    '{user_id}',
    {username},
    now()::timestamp
    )
    '''
    res = execute_sql(sql_request, select=False)
    assert res


def update_user(user_id, username):
    if username == 'None':
        username = 'null'
    else:
        username = "'" + username + "'"
    sql_request = f'''
    update "user"
    set user_id = '{user_id}', 
    username = {username},
    updated = now()::timestamp
    where user_id = '{user_id}'
    '''
    res = execute_sql(sql_request, select=False)
    assert res


def add_date(name, date, user_id):
    user_tab_id = get_user_tab_id_by_user_id(user_id)
    sql_request = f'''
    insert into dates (
        name,
        date,
        user_id
    )
    values (
        '{name}',
        '{date}',
        {user_tab_id}
    )
    '''
    res = execute_sql(sql_request, select=False)
    assert res
