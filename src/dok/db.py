import sqlite3
import os
class Database():
    def __init__(self):
        file_dir = os.path.dirname(os.path.abspath(str(__file__)))
        self.db_path = os.path.join(file_dir, "dok.db")
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()
    
    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE if not exists dok(name, image, commands, docker_file)")
        cur.execute("CREATE TABLE if not exists active_dok(name)")
    
    def insert_dok(self, name, image, commands, docker_file):
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO dok VALUES ('{name}', '{image}','{commands}', '{docker_file}')")
        self.conn.commit()

    def select_dok(self, name):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM dok WHERE name = '{name}'")
        return cur.fetchone()
    
    def select_all_dok(self):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM dok")
        return cur.fetchall()
    
    def remove_dok(self, name):
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM dok WHERE name = '{name}'")
        self.conn.commit()
    
    def set_active_dok(self):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM active_dok")
        res = cur.fetchone()
        return res[-1] if res else None
    
    def replace_active_dok(self, name):
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM active_dok")
        cur.execute(f"INSERT INTO active_dok VALUES ('{name}')")
        self.conn.commit()
    
    def deactivate_dok(self):
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM active_dok")
        self.conn.commit()
