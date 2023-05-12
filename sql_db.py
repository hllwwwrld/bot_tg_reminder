from db_conn import DbConnection


class SqlRequests(DbConnection):
    # если fetch=True - запрос на выборку, нужно что-то вернуть, иначе запрос на изменение
    # fetchone - если надо вернуть одну строку
    def execute_sql(self, sql: str, select: bool = True, fetchone: bool = False) -> list[tuple] | tuple:
        try:
            self.database.execute(sql)
            if select:
                if fetchone:
                    return self.database.fetchone()
                else:
                    return self.database.fetchall()
            else:
                self.db_connection.commit()
        except:
            print(f'Ошибка выполнения sql-запроса {sql}')

    def is_user_new(self, user_id: str) -> bool:
        sql_request = f'''
        select * from "user"
        where user_id = '{user_id}' 
        '''
        res = self.execute_sql(sql_request, fetchone=True)
        return not bool(res)

    def get_user_tab_id_by_user_id(self, user_id: str) -> int:
        sql_request = f"""
        select tab_id from "user"
        where user_id = '{user_id}'
        """
        res = self.execute_sql(sql_request, fetchone=True)
        return res[0]

    def create_user(self, user_id: str, username: str) -> None:
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
        self.execute_sql(sql_request, select=False)

    def update_user(self, user_id: str, username: str) -> None:
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
        self.execute_sql(sql_request, select=False)

    def add_date(self, name: str, date: str, user_id: str) -> None:
        user_tab_id = self.get_user_tab_id_by_user_id(user_id)
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
        self.execute_sql(sql_request, select=False)

    def check_dates(self, user_id: str, month: str = 'all', nearest: bool = False) -> dict[str: str]:
        if month == 'all':
            month = ''
        else:
            month = f"and date_part('month', d.date) = '{month}'"

        sql_request = f'''
        select d."name", d."date"
        from dates d
        join "user" u 
        on  d.user_id = u.tab_id
        where u.user_id = '{user_id}'
        {month}
        order by date_part('month', d.date), date_part('day', d.date)
        '''
        if nearest:
            res = self.execute_sql(sql_request, fetchone=True)
            return {res[0]: str(res[1])}
        else:
            res = self.execute_sql(sql_request)
            return {row[0]: row[1] for row in res}

    def get_all_users(self) -> list[str]:
        sql_request = """
        select u.user_id 
        from "user" u 
        """
        res = self.execute_sql(sql_request)
        return [user_id for tu in res for user_id in tu]

    def get_remind_date(self, user_id: str, user_days_remind_to: int = 3) -> list[tuple[str | int]]:
        sql_request = f"""
        select d."name", d."date", d.user_id, 
        {user_days_remind_to} - (date_part('day', age(current_date, d.date::date - interval '{user_days_remind_to} days'))) 
        as "days_until_date"
        from dates d
        join "user" u on d.user_id = u.tab_id
        where date_part('month', age(current_date, d.date::date - interval '{user_days_remind_to} days')) = 0
        and date_part('day', age(current_date, d.date::date - interval '{user_days_remind_to} days')) between 0 and
        {user_days_remind_to}
        and u.user_id = '{user_id}'
        order by 4
        """
        res = self.execute_sql(sql_request)
        return res

    def get_remind_hours(self, user_id: str) -> list[tuple[str | int]]:
        sql_request = f'''
        select d."name", d."date", u.user_id, 
        3 - (date_part('hour', age(current_timestamp, d."date" - interval '3 hours'))) as hours_until,
        abs(date_part('minute', age(current_timestamp, d."date"))) as minutes_until
        --3 - (date_part('day', age(current_timestamp, d.date - interval '3 days'))) as "days_until_date"
        --date_part('month', age(current_timestamp, d.date - interval '3 days')) as "month_until"
        from dates d
        join "user" u 
        on d.user_id = u.tab_id 
        where 
        case 
            when 3 - (date_part('hour', age(current_timestamp, d."date" - interval '3 hours'))) = 0
            then date_part('minute', age(d."date", current_timestamp)) >= 0
            else 3 - (date_part('hour', age(current_timestamp, d."date" - interval '3 hours'))) between 1 and 3
        end
        and 3 - (date_part('day', age(current_date, d.date::date - interval '3 days'))) in (0, 1)
        and date_part('month', age(current_date, d.date::date - interval '3 days')) = 0
        and d."date"::text not like '% 00:00:00'
        and u.user_id = '{user_id}'
        order by 4
        '''
        res = self.execute_sql(sql_request)
        return res

    def delete_date(self, user_id: str, name: str) -> None:
        body = f'''
        delete from dates d
        where d.tab_id in (select d.tab_id from dates d
                            join "user" u
                            on d.user_id = u.tab_id
                            where u.user_id = '{user_id}'
                            and d.name = '{name}'
                            )
        '''
        self.execute_sql(body, select=False)
