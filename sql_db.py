from db_conn import Connections


class SqlRequests(Connections):
    # если fetch=True - запрос на выборку, нужно что-то вернуть, иначе запрос на изменение
    # fetchone - если надо вернуть одну строку
    def execute_sql(self, sql, select=True, fetchone=False):
        try:
            self.cursor.execute(sql)
            if select:
                if fetchone:
                    return self.cursor.fetchone()
                else:
                    return self.cursor.fetchall()
            else:
                self.database.commit()
        except:
            print(f'Ошибка выполнения sql-запроса {sql}')

    def is_user_new(self, user_id):
        sql_request = f'''
        select * from "user"
        where user_id = '{user_id}' 
        '''
        res = self.execute_sql(sql_request, fetchone=True)
        return not bool(res)

    def get_user_tab_id_by_user_id(self, user_id):
        sql_requset = f"""
        select tab_id from "user"
        where user_id = '{user_id}'
        """
        res = self.execute_sql(sql_requset, fetchone=True)
        return res[0]

    def create_user(self, user_id, username):
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
        res = self.execute_sql(sql_request, select=False)
        assert res

    def update_user(self, user_id, username):
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
        res = self.execute_sql(sql_request, select=False)
        assert res

    def add_date(self, name, date, user_id):
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
        res = self.execute_sql(sql_request, select=False)
        assert res

    def check_dates(self, user_id, month='all', nearest=False):
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

    def get_all_users(self):
        sql_request = """
        select u.user_id 
        from "user" u 
        """
        res = self.execute_sql(sql_request)
        return [user_id for tu in res for user_id in tu]

    def get_remind_date(self, user_id, user_days_remaind_to=3):
        sql_request = f"""
        select d."name", d."date", d.user_id, 
        {user_days_remaind_to} - (date_part('day', age(current_date, d.date::date - interval '{user_days_remaind_to} days'))) 
        as "days_until_date"
        from dates d
        join "user" u on d.user_id = u.tab_id
        where date_part('month', age(current_date, d.date::date - interval '{user_days_remaind_to} days')) = 0
        and date_part('day', age(current_date, d.date::date - interval '{user_days_remaind_to} days')) between 0 and
        {user_days_remaind_to}
        and u.user_id = '{user_id}'
        order by 4
        """
        res = self.execute_sql(sql_request)
        return res

    def get_remind_hours(self, user_id):
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

    def delete_date(self, user_id, name):
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
