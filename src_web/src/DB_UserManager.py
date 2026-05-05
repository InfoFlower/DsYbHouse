from DB_Manager import db_manager
import sqlalchemy

class DB_UserManager(db_manager):
    def __init__(self, db_path):
        super().__init__(db_path)

    def add_user(self, username, password_hash):
        insert_sql = f"""
        INSERT INTO users (username, password_hash)
        VALUES (%s, %s);
        """
        conn = sqlalchemy.create_engine(self.db_path).connect()
        conn.exec_driver_sql(insert_sql, (username, password_hash))
        res = conn.exec_driver_sql("select * from users where username = %s;", (username,)).fetchone()
        print(f"User {username} added: {res}")
        conn.exec_driver_sql("COMMIT;")
        conn.close()
        return True if res is not None else False
    
    def get_password_hash(self, username):
        select_sql = f"""
        SELECT password_hash FROM users WHERE username = %s;
        """
        conn = sqlalchemy.create_engine(self.db_path).connect()
        result = conn.exec_driver_sql(select_sql, (username,)).fetchone()
        conn.close()
        return result[0] if result else None
