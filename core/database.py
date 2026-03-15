import sqlite3
import threading
from pathlib import Path


class Database():
    def __init__(self, dbPath="data/app.db"):
        self.databasePath = Path(dbPath)
        self.databasePath.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.databasePath, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.lock = threading.Lock()

    def initDb(self):
        try:
            self.conn.execute("BEGIN")

            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS subscribers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    frequency TEXT DEFAULT 'WEEKLY')
                    """
            )

            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS teams(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    short_name TEXT,
                    tla TEXT,
                    crest TEXT,
                    address TEXT,
                    website TEXT,
                    founded INTEGER,
                    club_colors TEXT,
                    venue TEXT,
                    last_updated_on_api TEXT,
                    last_update_on_db TEXT DEFAULT CURRENT_TIMESTAMP)
                    """
            )

            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscriber_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    UNIQUE(subscriber_id, team_id),
                    FOREIGN KEY (subscriber_id) REFERENCES subscribers(id) ON DELETE CASCADE,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE)
                    """
            )

            self.conn.commit()
            return None
        except Exception as e:
            self.conn.rollback()
            return e

    def insertSubscriber(self, email, frequency):
        try:
            with self.lock:
                self.conn.execute(
                    """
                    INSERT INTO subscribers (email, frequency)
                    VALUES(?,?)
                    """,
                    (email, frequency)
                )
                self.conn.commit()
                return None
        except Exception as e:
            return e

    def upsertTeamsInfo(self, teams):
        try:
            with self.lock:
                self.conn.execute("BEGIN")
                self.conn.executemany(
                    """
                    INSERT OR REPLACE INTO teams
                    (id, name, short_name, tla, crest, address, website, founded, club_colors, venue, last_updated_on_api)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            t["id"],
                            t["name"],
                            t["shortName"],
                            t["tla"],
                            t["crest"],
                            t["address"],
                            t["website"],
                            t["founded"],
                            t["clubColors"],
                            t["venue"],
                            t["lastUpdated"]
                        )
                        for t in teams
                    ]
                )
                self.conn.commit()
                return True, None
        except Exception as e:
            self.conn.rollback()
            return False, e

    def insertSubscription(self, subscriberId, teamId):
        try:
            with self.lock:
                cursor = self.conn.execute(
                    """
                    INSERT INTO subscriptions (subscriber_id, team_id)
                    VALUES(?,?)
                    """,
                    (subscriberId, teamId)
                )
                self.conn.commit()
                return cursor.lastrowid, None
        except Exception as e:
            return None, e

    def isTeamsEmpty(self):
        try:
            with self.lock:
                row = self.conn.execute("SELECT COUNT(*) AS c FROM teams").fetchone()
                return row["c"] == 0, None
        except Exception as e:
            return None, e

    def getAllSubscribers(self):
        try:
            with self.lock:
                rows = self.conn.execute("SELECT * FROM subscribers").fetchall()
                return [dict(row) for row in rows], None
        except Exception as e:
            return None, e

    def getTeamIdByName(self, teamName):
        try:
            with self.lock:
                row = self.conn.execute(
                    """
                    SELECT id FROM teams
                    WHERE name = ?
                    """,
                    (teamName,)
                ).fetchone()
                return row["id"] if row else None, None
        except Exception as e:
            return None, str(e)

    def getSubscribersByFrequencies(self, frequencies):
        try:
            with self.lock:
                placeholders = ",".join(["?"] * len(frequencies))
                query = f"""
                    SELECT *
                    FROM subscribers
                    WHERE frequency IN ({placeholders})
                """
                rows = self.conn.execute(query, frequencies).fetchall()
                return [dict(row) for row in rows], None
        except Exception as e:
            return None, str(e)

    def getSubscriberTeamIds(self, subscriberId):
        try:
            with self.lock:
                rows = self.conn.execute(
                    """
                    SELECT t.id
                    FROM teams t
                    JOIN subscriptions s ON s.team_id = t.id
                    WHERE s.subscriber_id = ?
                    """,
                    (subscriberId,)
                ).fetchall()
                return [row["id"] for row in rows], None
        except Exception as e:
            return None, e

    def getSubscriberTeams(self, subscriberId):
        try:
            with self.lock:
                rows = self.conn.execute(
                    """
                    SELECT t.name, t.crest
                    FROM teams t
                    JOIN subscriptions s ON s.team_id = t.id
                    WHERE s.subscriber_id = ?
                    ORDER BY t.name
                    """,
                    (subscriberId,)
                ).fetchall()
                return [{"name": row["name"], "crest": row["crest"]} for row in rows], None
        except Exception as e:
            return None, e



    def getSubscriberIdByEmail(self, email):
        try:
            with self.lock:
                row = self.conn.execute(
                    """
                    SELECT id
                    FROM subscribers
                    WHERE email = ?
                    """,
                    (email,)
                ).fetchone()
                return row["id"] if row else None, None
        except Exception as e:
            return None, e

    def deleteSubscription(self, subscriberId, teamId):
        try:
            with self.lock:
                self.conn.execute(
                    """
                    DELETE FROM subscriptions
                    WHERE subscriber_id = ? AND team_id = ?
                    """,
                    (subscriberId, teamId)
                )
                self.conn.commit()
                return None
        except Exception as e:
            self.conn.rollback()
            return e

    def deleteSubscriber(self, subscriberId):
        try:
            with self.lock:
                self.conn.execute(
                    """
                    DELETE FROM subscribers
                    WHERE id = ?
                    """,
                    (subscriberId,)
                )
                self.conn.commit()
                return None
        except Exception as e:
            self.conn.rollback()
            return e

    def searchTeams(self, query):
        try:
            with self.lock:
                search = f"%{query}%"
                rows = self.conn.execute(
                    """
                    SELECT name, crest
                    FROM teams
                    WHERE name LIKE ? COLLATE NOCASE
                    OR short_name LIKE ? COLLATE NOCASE
                    ORDER BY name
                    LIMIT 20
                    """,
                    (search, search)
                ).fetchall()
                return [{"name": row["name"], "crest": row["crest"]} for row in rows], None
        except Exception as e:
            return None, e

            