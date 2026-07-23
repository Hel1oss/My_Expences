import sqlite3

DB = "Login.db"

with sqlite3.connect(DB) as database:
    conn = database.cursor()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Users_data (
        User_id INTEGER PRIMARY KEY AUTOINCREMENT,
        User_name TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Active_user (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    """)
    database.commit()

def create_account(name): #### Inserting new user into the User_data table
    with sqlite3.connect(DB) as database:
        conn = database.cursor()
        conn.execute(
        "INSERT INTO Users_data (User_name) VALUES (?)",
        (name,)
         )

def login(name): ### inserting the selected user into the Active user table
    with sqlite3.connect(DB) as database:
        conn = database.cursor()
        user = conn.execute("SELECT * FROM Users_data WHERE User_name = ?", (name,)).fetchone()
        if user:
            ids, names = user
            conn.execute(
                "INSERT INTO Active_user (id, name) VALUES (?, ?)",
                (ids, names)
                )
            return user
        return None


def Load_user(): ### Load user from active user to memory ensure user doesnt need to login again
    with sqlite3.connect(DB) as database:
        conn = database.cursor()
        user = conn.execute("SELECT * FROM Active_user").fetchone()
        if user:
            return user
        return None

def load_id(name): ### return user ids by name to be use in expence backend
    with sqlite3.connect(DB) as database:
        conn = database.cursor()
        user_ids = conn.execute("SELECT User_id FROM Users_data WHERE User_name = ?", (name,)).fetchone()
        return user_ids[0]

def check_exist(name): ### return bool for true or false, if True user must be not recreated:
    with sqlite3.connect(DB) as database:
        conn = database.cursor()
        user_ids = conn.execute("SELECT User_id FROM Users_data WHERE User_name = ?", (name,)).fetchone()
        
        exist = user_ids is not None
        return exist  #True if exist False if none 

def logout(): ### deleting the active user table
    with sqlite3.connect(DB) as database:
        conn = database.cursor()
        conn.execute("DELETE FROM Active_user;")


print("im running")

if __name__ == "__main__":
    logout()