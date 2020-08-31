import sqlite3
import os
import logging
import datetime
from hoshino import logger
from ..exception import DatabaseError

DB_PATH = os.path.expanduser('~/.hoshino/pokemon.db')

class SqliteDao(object):
    def __init__(self, table, columns, fields):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._dbpath = DB_PATH
        self._table = table
        self._columns = columns
        self._fields = fields
        self._create_table()


    def _create_table(self):
        sql = "CREATE TABLE IF NOT EXISTS {0} ({1})".format(self._table, self._fields)
        # logging.getLogger('SqliteDao._create_table').debug(sql)
        with self._connect() as conn:
            conn.execute(sql)


    def _connect(self):
        # detect_types 中的两个参数用于处理datetime
        return sqlite3.connect(self._dbpath, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

class PokeDao(SqliteDao):#TODO：想一想查询宝可梦都要做什么操作
#用于调取pokedex表中的宝可梦数据，只读    
    def __init__(self):
        super().__init__(
            table='pokedex',
            columns='name, type_id, type',
            fields='''
            name TEXT NOT NULL,
            type_id INT NOT NULL,
            type INT NOT NULL,
            PRIMARY KEY (player_id)
            ''')

class MemberDao(SqliteDao):
    def __init__(self):
        super().__init__(
            table='player_info',
            columns='player_id, player_name, last_fight, last_capture, last_travel, money, ball, place',
            fields='''
            player_id INT NOT NULL,
            player_name TEXT NOT NULL,
            last_fight INT NOT NULL,
            last_capture INT NOT NULL,
            last_travel INT NOT NULL,
            money INT NOT NULL,
            ball INT NOT NULL,
            place INT NOT NULL,
            PRIMARY KEY (player_id)
            ''')

    @staticmethod
    def row2item(r):
        return {
            'player_id': r[0], 
            'last_fight': r[1], 
            'last_capture': r[2],
            'last_travel': r[3],
            'money': r[4],
            'ball': r[5],
            'place': r[6]
        } if r else None


    def add(self, member):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (?, ?, ?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (member['player_id'], 
                     member['last_fight'], 
                     member['last_capture'], 
                     member['last_travel'], 
                     member['money'],
                     member['ball'],
                     member['place']) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.add] {e}')
                raise DatabaseError('添加成员失败')


    def delete(self, player_id):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE player_id=?
                    '''.format(self._table), player_id)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.delete] {e}')
                raise DatabaseError('删除成员失败')


    def modify(self, member):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET
                                last_fight=?, 
                                last_capture=?,
                                last_travel=?,
                                money=?,
                                ball=?,
                                place=? 
                                WHERE player_id=?
                    '''.format(self._table),
                     member['last_fight'], 
                     member['last_capture'], 
                     member['last_travel'], 
                     member['money'],
                     member['ball'],
                     member['place']) 
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.modify] {e}')
                raise DatabaseError('修改成员失败')       


    def find_one(self, player_id):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE player_id=?
                    '''.format(self._table, self._columns),
                    (player_id) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_one] {e}')
                raise DatabaseError('查找成员失败')


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0}
                    '''.format(self._table, self._columns),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_all] {e}')
                raise DatabaseError('查找成员失败')


    def find_by(self, place=None):
        cond_str = []
        cond_tup = []
        if not place is None:
            cond_str.append('place=?')
            cond_tup.append(place)

        if 0 == len(cond_tup):
            return self.find_all()
        
        cond_str = " AND ".join(cond_str)
        
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE {2}
                    '''.format(self._table, self._columns, cond_str), 
                    cond_tup ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_by] {e}')
                raise DatabaseError('查找成员失败')


    def delete_by(self, player_id=None):
        cond_str = []
        cond_tup = []
        if not player_id is None:
            cond_str.append('player_id=?')
            cond_tup.append(player_id)

        if 0 == len(cond_tup):
            raise DatabaseError('删除成员的条件有误')
        
        cond_str = " AND ".join(cond_str)
        
        with self._connect() as conn:
            try:
                cur = conn.execute('''
                    DELETE FROM {0} WHERE {1}
                    '''.format(self._table, cond_str), 
                    cond_tup )
                return cur.rowcount
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_by] {e}')
                raise DatabaseError('查找成员失败')

class TypeDao(SqliteDao):
    def __init__(self):
        super().__init__(
            table='type_info',
            columns='type, normal, fire, water, electric, grass, ice, fighting, poison, ground, flying, psychic, bug, rock, ghost, dragon, dark, steel, fairy',
            fields='''
            type TEXT NOT NULL, 
            normal FLOAT NOT NULL, 
            fire FLOAT NOT NULL, 
            water FLOAT NOT NULL, 
            electric FLOAT NOT NULL, 
            grass FLOAT NOT NULL, 
            ice FLOAT NOT NULL, 
            fighting FLOAT NOT NULL, 
            poison FLOAT NOT NULL, 
            ground FLOAT NOT NULL, 
            flying FLOAT NOT NULL, 
            psychic FLOAT NOT NULL, 
            bug FLOAT NOT NULL, 
            rock FLOAT NOT NULL, 
            ghost FLOAT NOT NULL, 
            dragon FLOAT NOT NULL, 
            dark FLOAT NOT NULL, 
            steel FLOAT NOT NULL, 
            fairy FLOAT NOT NULL,
            PRIMARY KEY (type)
            ''')
    
    def row2item(r):
        return {
            'type': r[0], 
            'normal': r[1], 
            'fire': r[2],
            'water': r[3],
            'electric': r[4],
            'grass': r[5],
            'ice': r[6],
            'fighting': r[7],
            'poison': r[8],
            'ground': r[9],
            'flying': r[10],
            'psychic': r[11],
            'bug': r[12],
            'rock': r[13],
            'ghost': r[14],
            'dragon': r[15],
            'dark': r[16],
            'steel': r[17],
            'fairy': r[18]
        } if r else None

    def find_one(self, type):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE player_id=?
                    '''.format(self._table, self._columns),
                    (type) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[TypeDao.find_one] {e}')
                raise DatabaseError('查找属性失败')

    def find_by(self, type=None):
        cond_str = []
        cond_tup = []
        if not type is None:
            cond_str.append('type=?')
            cond_tup.append(type)

        if 0 == len(cond_tup):
            return self.find_all()
        
        cond_str = " AND ".join(cond_str)
        
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE {2}
                    '''.format(self._table, self._columns, cond_str), 
                    cond_tup ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[TypeDao.find_by] {e}')
                raise DatabaseError('查找属性失败')

class StorgeDao(SqliteDao):#TODO：实现分表存储
    def __init__(self, player_id):
        super().__init__(
            table=self.get_table_name(player_id),
            columns='player_id, poke_id, poke_name, poke_level, poke_status',
            fields='''
            player_id INT NOT NULL,
            poke_id INT NOT NULL,
            poke_name TEXT NOT NULL,
            poke_level INT NOT NULL,
            poke_status INT NOT NULL,
            PRIMARY KEY (player_id)
            ''')
    @staticmethod
    def get_table_name(player_id):
        return 'player_%d' % (player_id)
    
    @staticmethod
    def row2item(r):
        return {
            'player_id': r[0], 
            'poke_id': r[1], 
            'poke_name': r[2],
            'poke_level': r[3],
            'poke_status': r[4],
        } if r else None

class LocationDao(SqliteDao):#TODO：什么都还没想好
    pass
