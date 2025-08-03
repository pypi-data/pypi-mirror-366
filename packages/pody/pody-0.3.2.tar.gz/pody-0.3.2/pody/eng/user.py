import sqlite3
import hashlib
import dataclasses
from typing import Optional

from .db import DatabaseAbstract
from .log import get_logger
from .nparse import check_name_part
from .errors import InvalidUsernameError
from .utils import format_storage_size, parse_storage_size
from ..config import DATA_HOME, Config, config

def hash_password(username: str, password: str):
    return hashlib.sha256(f"{username}:{password}".encode()).hexdigest()

def check_username(username: str):
    if not (res := check_name_part(username, ['share']))[0]: raise InvalidUsernameError(res[1])

@dataclasses.dataclass
class UserRecord:
    userid: int
    name: str
    is_admin: bool

class UserDatabase(DatabaseAbstract):
    @property
    def conn(self): return self._conn
    def __init__(self):
        self.logger = get_logger('engine')

        DATA_HOME.mkdir(exist_ok=True)
        self._conn = sqlite3.connect(DATA_HOME / "users.db", check_same_thread=False)
        # enable foreign key constraint
        self.conn.execute("PRAGMA foreign_keys = ON;")

        with self.transaction() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    credential TEXT NOT NULL, 
                    is_admin BOOLEAN NOT NULL DEFAULT 0
                );
                """
            )

    def add_user(self, username: str, password: str, is_admin: bool = False):
        check_username(username)
        with self.transaction() as cursor:
            cursor.execute(
                "INSERT INTO users (username, credential, is_admin) VALUES (?, ?, ?)",
                (username, hash_password(username, password), is_admin),
            )
            res = cursor.lastrowid
            self.logger.info(f"User {username} added with id {res}")
    
    def update_user(self, username: str, **kwargs):
        check_username(username)
        if 'password' in kwargs and kwargs['password'] is not None:
            with self.transaction() as c:
                c.execute("UPDATE users SET credential = ? WHERE username = ?", (hash_password(username, kwargs.pop('password')), username))
                self.logger.info(f"User {username} password updated")
        if 'is_admin' in kwargs and kwargs['is_admin'] is not None:
            with self.transaction() as c:
                c.execute("UPDATE users SET is_admin = ? WHERE username = ?", (kwargs.pop('is_admin'), username))
                self.logger.info(f"User {username} is_admin updated") # to fix
    
    def has_user(self, username: str)->bool:
        with self.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            return cur.fetchone() is not None
    
    def get_user(self, user_id: str | int):
        """May return UserRecord of id=0 if not found"""
        if isinstance(user_id, str):
            with self.cursor() as cur:
                cur.execute("SELECT id, username, is_admin FROM users WHERE username = ?", (user_id,))
                res = cur.fetchone()
                if res is None: return UserRecord(0, '', False)
                else: return UserRecord(*res)
        else:
            with self.cursor() as cur:
                cur.execute("SELECT id, username, is_admin FROM users WHERE id = ?", (user_id,))
                res = cur.fetchone()
                if res is None: return UserRecord(0, '', False)
                else: return UserRecord(*res)

    def check_user(self, credential: str):
        with self.cursor() as cur:
            cur.execute("SELECT id, username, is_admin FROM users WHERE credential = ?", (credential,))
            res = cur.fetchone()
            if res is None: return UserRecord(0, '', False)
            else: return UserRecord(*res)
    
    def list_users(self, usernames: Optional[list[str]] = None):
        if usernames is None:
            with self.cursor() as cur:
                cur.execute("SELECT id, username, is_admin FROM users")
                return [UserRecord(*u) for u in cur.fetchall()]
        else:
            with self.cursor() as cur:
                cur.execute(f"SELECT id, username, is_admin FROM users WHERE username IN ({','.join(['?']*len(usernames))})", usernames)
                return [UserRecord(*u) for u in cur.fetchall()]

    def delete_user(self, username: str):
        with self.transaction() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE username = ?",
                (username,),
            )
            self.logger.info(f"User {username} deleted")

@dataclasses.dataclass
class UserQuota:
    max_pods: int
    gpu_count: int
    gpus: str
    memory_limit: int # in bytes (per container)
    storage_size: int # in bytes (per container, exclude external volumes)
    shm_size: int # in bytes (per container)
    commit_count: int
    commit_size_limit: int

    def __str__(self):
        return  f"Quota(max_pods={self.max_pods}, gpu_count={self.gpu_count}, gpus={self.gpus}, "\
                f"memory_limit={format_storage_size(self.memory_limit) if self.memory_limit >= 0 else self.memory_limit}, "\
                f"storage_size={format_storage_size(self.storage_size) if self.storage_size >= 0 else self.storage_size}, "\
                f"shm_size={format_storage_size(self.shm_size) if self.shm_size >= 0 else self.shm_size}, "\
                f"commit_count={self.commit_count}, "\
                f"commit_size_limit={format_storage_size(self.commit_size_limit) if self.commit_size_limit >= 0 else self.commit_size_limit})"

def get_fallback_quota(q: UserQuota, cq: Optional[Config.DefaultQuota] = None) -> UserQuota:
    """
    Takes a UserQuota object, returns a new UserQuota object with fallback values from Config.DefaultQuota, 
    Replace any -1 values in q with the corresponding value in cq. 
    If cq is None, use the default quota in config.
    """
    if cq is None:
        cq = config().default_quota
    def storage_size_from_str(s: str) -> int:
        if not s: return -1
        return parse_storage_size(s)
    return UserQuota(
        max_pods = q.max_pods if q.max_pods >= 0 else cq.max_pods,
        gpu_count = q.gpu_count if q.gpu_count >= 0 else cq.gpu_count,
        gpus = q.gpus if q.gpus != "" else cq.gpus,
        memory_limit = q.memory_limit if q.memory_limit >= 0 else storage_size_from_str(cq.memory_limit),
        storage_size = q.storage_size if q.storage_size >= 0 else storage_size_from_str(cq.storage_size),
        shm_size = q.shm_size if q.shm_size >= 0 else storage_size_from_str(cq.shm_size),
        commit_count= q.commit_count if q.commit_count >= 0 else cq.commit_count, 
        commit_size_limit = q.commit_size_limit if q.commit_size_limit >= 0 else storage_size_from_str(cq.commit_size_limit),
        )

class QuotaDatabase(DatabaseAbstract):
    @property
    def conn(self): return self._conn
    def __init__(self):
        self.logger = get_logger('engine')

        DATA_HOME.mkdir(exist_ok=True)
        self._conn = sqlite3.connect(DATA_HOME / "quota.db", check_same_thread=False)

        with self.transaction() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS quota (
                    username TEXT PRIMARY KEY,
                    max_pods INTEGER NOT NULL DEFAULT -1,
                    gpu_count INTEGER NOT NULL DEFAULT -1,
                    gpus TEXT NOT NULL DEFAULT '',
                    memory_limit INTEGER NOT NULL DEFAULT -1,
                    storage_size INTEGER NOT NULL DEFAULT -1,
                    shm_size INTEGER NOT NULL DEFAULT -1, 
                    commit_count INTEGER NOT NULL DEFAULT -1, 
                    commit_size_limit INTEGER NOT NULL DEFAULT -1
                );
                """
            )

        self.__maybe_upgrade()
    
    def __maybe_upgrade(self):
        # if commit_count is not in schema, add it
        def add_commit_count():
            with self.cursor() as cursor:
                cursor.execute("PRAGMA table_info(quota)")
                columns = [col[1] for col in cursor.fetchall()]
                if "commit_count" in columns:
                    return
            with self.transaction() as cursor:
                cursor.execute(
                    "ALTER TABLE quota ADD COLUMN commit_count INTEGER NOT NULL DEFAULT -1"
                )
                self.logger.info("Quota database upgraded to latest version")
        # if commit_size_limit is not in schema, add it
        def add_commit_size_limit():
            with self.cursor() as cursor:
                cursor.execute("PRAGMA table_info(quota)")
                columns = [col[1] for col in cursor.fetchall()]
                if "commit_size_limit" in columns:
                    return
            with self.transaction() as cursor:
                cursor.execute(
                    "ALTER TABLE quota ADD COLUMN commit_size_limit INTEGER NOT NULL DEFAULT -1"
                )
                self.logger.info("Quota database upgraded to latest version")
        add_commit_count()
        add_commit_size_limit()
    
    def delete_quota(self, usrname: str):
        with self.transaction() as cursor:
            r = cursor.execute(
                "DELETE FROM quota WHERE username = ?",
                (usrname,),
            )
            if r.rowcount:
                self.logger.info(f"Quota for user {usrname} deleted")
            else:
                self.logger.debug(f"Skip deleting quota for user {usrname}, not found")

    def check_quota(self, usrname: str, use_fallback: bool = True) -> UserQuota:
        """
        Get user quota, if not exists, returns a default quota. 
        If use_fallback is True, the default quota in config will be used as fallback.
        """
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    max_pods, gpu_count, gpus, 
                    memory_limit, storage_size, shm_size, 
                    commit_count, commit_size_limit
                FROM quota WHERE username = ?
                """,
                (usrname,),
            )
            res = cur.fetchone()
            if res is None: q = UserQuota(-1, -1, "", -1, -1, -1, -1, -1)
            else: q = UserQuota(*res)
        if use_fallback:
            return get_fallback_quota(q)
        else:
            return q

    def update_quota(
        self, usrname: str, 
        max_pods: Optional[int] = None,
        gpu_count: Optional[int] = None,
        gpus: Optional[str] = None,
        memory_limit: Optional[int] = None,
        storage_size: Optional[int] = None,
        shm_size: Optional[int] = None,
        commit_count: Optional[int] = None, 
        ):
        """
        Update user quota, 
        will create a new record if not exists, update the record if exists
        """
        with self.transaction() as cursor:
            r = cursor.execute(
                "INSERT OR IGNORE INTO quota (username) VALUES (?)",
                (usrname,),
            )
            if r.rowcount != 0:
                self.logger.debug(f"Quota for user {usrname} initialized")

        with self.transaction() as cursor:
            if max_pods is not None:
                cursor.execute(
                    "UPDATE quota SET max_pods = ? WHERE username = ?",
                    (max_pods, usrname),
                )
                self.logger.info(f"User {usrname} max_pods updated")
            if gpu_count is not None:
                cursor.execute(
                    "UPDATE quota SET gpu_count = ? WHERE username = ?",
                    (gpu_count, usrname),
                )
                self.logger.info(f"User {usrname} gpu_count updated")
            if gpus is not None:
                cursor.execute(
                    "UPDATE quota SET gpus = ? WHERE username = ?",
                    (gpus, usrname),
                )
                self.logger.info(f"User {usrname} gpus updated")
            if memory_limit is not None:
                cursor.execute(
                    "UPDATE quota SET memory_limit = ? WHERE username = ?",
                    (memory_limit, usrname),
                )
                self.logger.info(f"User {usrname} memory_limit updated")
            if storage_size is not None:
                cursor.execute(
                    "UPDATE quota SET storage_size = ? WHERE username = ?",
                    (storage_size, usrname),
                )
                self.logger.info(f"User {usrname} storage_size updated")
            if shm_size is not None:
                cursor.execute(
                    "UPDATE quota SET shm_size = ? WHERE username = ?",
                    (shm_size, usrname),
                )
                self.logger.info(f"User {usrname} shm_size updated")
            if commit_count is not None:
                cursor.execute(
                    "UPDATE quota SET commit_count = ? WHERE username = ?",
                    (commit_count, usrname),
                )
                self.logger.info(f"User {usrname} commit_count updated")
