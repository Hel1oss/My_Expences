import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import csv
import base64
import io
from assets.login_back import load_id, Load_user
DB = "expenses.db"

def create_table(name):
    user_id = load_id(name)
    conn = sqlite3.connect(DB) 
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS expenses_user_{user_id} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        spending INTEGER NOT NULL
    )
    """)
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS balance_user_{user_id} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        name TEXT NOT NULL,
        income INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()

class ExpenceTrack:
    User_id = None
    _instances = {}
    def __new__(cls, category):
        if category in cls._instances:
            return cls._instances[category]
        obj = super().__new__(cls)
        cls._instances[category] = obj
        return obj

    def __init__(self, category):
        if hasattr(self, "_initialized"):
            return
        self.category = category
        self.log = []
        self._load()
        self._initialized = True

    def _load(self):
         user_id = ExpenceTrack.User_id
         with sqlite3.connect(DB) as database:
            cursor = database.cursor() 
            cursor.execute(
            f"SELECT id, date, category, name, spending FROM expenses_user_{user_id} WHERE category = ?",
            (self.category,))

            for row in cursor.fetchall():
                self.log.append({
                    "id": row[0],
                    "date": row[1],
                    "category": row[2],
                    "name": row[3],
                    "spending": row[4]
                })

    def addExpence(self, name :str, spending :int):
        user_id = ExpenceTrack.User_id
        date = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(DB) as database:
            cursor = database.cursor()
            cursor.execute(
            f"INSERT INTO expenses_user_{user_id} (date, category, name, spending) VALUES (?, ?, ?, ?)",
            (date, self.category, name, spending))
            expense_id = cursor.lastrowid
        self.log.append({
            "id": expense_id,
            "date": date,
            "category": self.category,
            "name": name,
            "spending": spending
        })
    @classmethod
    def InputClass(cls, category, id):
        cls.User_id = id 
        return cls(category)

    def __str__(self):
        bon = ""
        for item in self.log:
            bon += f"{item}\n"
        return bon

def expenceRegister(category, name, expences):
    ExpenceTrack(category).addExpence(name, expences)

def CategoryRegister(category):
    ExpenceTrack(category)

def View(types):
    return ExpenceTrack(types)

def CategoryViewer():
    return ExpenceTrack._instances

def CategoryDeleter(Target):
    ids, name = Load_user()
    print(f"{Target} been deleted")
    with sqlite3.connect(DB) as database:
        cursor = database.cursor()
        cursor.execute(f"DELETE FROM expenses_user_{ids} WHERE category = ?", (Target,))
    ExpenceTrack._instances.pop(Target, None)

def logFrame(category, time_line):
    ids, name = Load_user()
    data = ExpenceTrack.InputClass(category, ids).log

    filtered = data[:]  # copy
    if time_line == "All spending":
        filtered = data[:]

    elif time_line == "Today":
        today = datetime.now().strftime("%Y-%m-%d")
        filtered = [x for x in data if x["date"] == today]

    elif time_line == "This_week":
        start = (datetime.now() - timedelta(days=7)).date()
        filtered = [
            x for x in data
            if datetime.strptime(x["date"], "%Y-%m-%d").date() >= start
        ]

    elif time_line == "This_month":
        now = datetime.now()
        filtered = [
            x for x in data
            if (d := datetime.strptime(x["date"], "%Y-%m-%d")).year == now.year
            and d.month == now.month
        ]

    elif time_line == "This_Year":
        year = datetime.now().year
        filtered = [
            x for x in data
            if datetime.strptime(x["date"], "%Y-%m-%d").year == year
        ]

    return  [{"id": filtered[n]["id"], \
              "date": filtered[n]["date"], \
              "category":filtered[n]["category"], \
              "name":filtered[n]["name"], \
              "spending":f"Rp.{filtered[n]['spending']:,}"} for n in range(len(filtered))]

def Scrape(time_line="All spending"):
    where = ""
    params = ()
    ids, name = Load_user()
    if time_line == "Today":
        where = "WHERE date = ?"
        params = (datetime.now().strftime("%Y-%m-%d"),)

    elif time_line == "This_week":
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        where = "WHERE date >= ?"
        params = (start,)

    elif time_line == "This_month":
        start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        where = "WHERE date >= ?"
        params = (start,)

    elif time_line == "This_Year":
        start = datetime.now().replace(month=1, day=1).strftime("%Y-%m-%d")
        where = "WHERE date >= ?"
        params = (start,)

    query = f"""
        SELECT category, SUM(spending)
        FROM expenses_user_{ids}
        {where}
        GROUP BY category
    """

    with sqlite3.connect(DB) as database:
        cursor = database.cursor()
        rows = cursor.execute(query, params).fetchall()

    return rows if rows else [("empty", 0)]

def Download():
    ids, name = Load_user()
    with sqlite3.connect(DB) as database:
        df = pd.read_sql_query(
            f"SELECT * FROM expenses_user_{ids}",
            database
        )
    return df

def Upload(content_string):
    ids, name = Load_user()
    allowed_fields = {"id", "date", "name", "category", "spending"}

    file_bytes = base64.b64decode(content_string)
    myfile = io.TextIOWrapper(io.BytesIO(file_bytes), encoding="utf-8")

    read = csv.DictReader(myfile)

    try:
        if set(read.fieldnames) != allowed_fields:
            raise ValueError

        with sqlite3.connect(DB) as database:
            cursor = database.cursor()
            cursor.execute(f"DELETE FROM expenses_user_{ids};")
            ExpenceTrack._instances = {}   
            for item in read:

                cursor.execute(
                    f"INSERT INTO expenses_user_{ids} (date, category, name, spending) VALUES (?, ?, ?, ?)",
                    (item["date"], item["category"], item["name"], item["spending"])
                )
        with sqlite3.connect(DB) as databased:
            cursor1 = databased.cursor()
            cursor1.execute(
                f"SELECT DISTINCT category FROM expenses_user_{ids}"
            )

            for (category,) in cursor.fetchall():
                ExpenceTrack.InputClass(category, ids)    

        return "Success"

    except ValueError:
        return "CannotParse"

def rowDeleter(target, id):
    user_ids, name = Load_user()
    data = ExpenceTrack(target).log

    for idx, row in enumerate(data):
        if row["id"] == id:
            data.pop(idx)
            break
    with sqlite3.connect(DB) as database:
        cursor = database.cursor()
        cursor.execute(
            f"DELETE FROM expenses_user_{user_ids} WHERE id = {id}"
        )

def state(value=None):
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS app_state (
                id INTEGER PRIMARY KEY,
                dark_clicks INTEGER NOT NULL
            )
        """)

        cur.execute("""
            INSERT OR IGNORE INTO app_state (id, dark_clicks)
            VALUES (1, 0)
        """)

        if value is not None:
            cur.execute("""
                UPDATE app_state
                SET dark_clicks = dark_clicks + ?
                WHERE id = 1
            """, (value,))
            conn.commit()

        cur.execute("""
            SELECT dark_clicks
            FROM app_state
            WHERE id = 1
        """)

        return cur.fetchone()[0]

def load_table(user_id: int):
    """
    ### loading table every refresh page to the ram
    """
    ExpenceTrack._instances = {}
    with sqlite3.connect(DB) as database:
        cursor = database.cursor()
        cursor.execute(
            f"SELECT DISTINCT category FROM expenses_user_{user_id}"
        )

        for (category,) in cursor.fetchall():
            ExpenceTrack.InputClass(category, user_id)

def Add_balance(count: int) -> None:
    """
    #### inserting the balance from input to the sql
    """

    user_ids, name = Load_user()
    date = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB) as database:
        cursor = database.cursor()
        cursor.execute(
            f"INSERT INTO balance_user_{user_ids} (date, name, income) VALUES (?, ?, ?)",
            (date, name, count))


def Load_balance(time_line: str = None) -> list[dict]:
    """
    ### Load user balance table and convert it to list of dict to display in grid
    """

    user_ids, name = Load_user()
    date = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB) as database:
        cursor = database.cursor()
        row = cursor.execute(f"SELECT id, date, income FROM balance_user_{user_ids}").fetchall()
    return [{"id": r[0], "date": r[1], "income": f"Rp.{r[2]:,}"} for r in row][::-1]
            # if row else {"id":0, "date":date, "income":0}

def Delete_balance(Target_ids: int) -> None:
    user_ids, name = Load_user()
    with sqlite3.connect(DB) as database:
        cursor = database.cursor()
        cursor.execute(f"DELETE FROM balance_user_{user_ids} WHERE id = ?", (Target_ids,))





def sumALL() -> tuple[int, int, int]:
    """
    ### return
    `(spending, income, balance)`\n
    in order
    """
    user_ids, name = Load_user()
    with sqlite3.connect(DB) as database:
        cursor = database.cursor()
        spending = cursor.execute(f"SELECT SUM(spending) FROM expenses_user_{user_ids}").fetchone()[0] or 0
        income = cursor.execute(f"SELECT SUM(income) FROM balance_user_{user_ids}").fetchone()[0] or 0
        balance = income - spending
        return income, spending,  balance



if __name__ == "__main__":
    load_table(13)
    print(ExpenceTrack._instances)
    print(ExpenceTrack._instances["Food"])
    print(logFrame("Food", "All spending"))
    print(sumALL())
