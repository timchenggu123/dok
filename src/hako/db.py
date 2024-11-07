import sqlite3
import os
class Database():
    def __init__(self):
        file_dir = os.path.dirname(os.path.abspath(str(__file__)))
        self.db_path = os.path.join(file_dir, "hako.db")
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()
    
    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE if not exists hako(name, image, commands, docker_file)")
    
    def insert_hako(self, name, image, commands, docker_file):
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO hako VALUES ('{name}', '{image}','{commands}', '{docker_file}')")
        self.conn.commit

    def select_hako(self, name):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM hako WHERE name = '{name}'")
        return cur.fetchone()
    
    def delete_hako(self, name):
        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM hako WHERE name = '{name}'")
        



    


