import os
import struct
import hashlib
from typing import Dict, List, Union, Optional, Callable, Any, Tuple
from contextlib import contextmanager
import secrets
import time
import warnings
from bisect import bisect_left

MAGIC_NUMBER = b'INSQLDB'
VERSION = 3
HEADER_SIZE = 16
MAX_CONCURRENT_DB = 3
WARNING_DELAY = 0.1

_open_databases = {}
_last_access_time = {}

class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.values = []
        self.children = []

class BTree:
    def __init__(self, degree=2):
        self.root = BTreeNode(leaf=True)
        self.degree = degree

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        i = bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i]
        elif node.leaf:
            return None
        else:
            return self._search(node.children[i], key)

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == (2 * self.degree) - 1:
            new_root = BTreeNode()
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)

    def _insert_non_full(self, node, key, value):
        i = bisect_left(node.keys, key)
        if node.leaf:
            node.keys.insert(i, key)
            node.values.insert(i, value)
        else:
            if len(node.children[i].keys) == (2 * self.degree) - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent, index):
        degree = self.degree
        child = parent.children[index]
        new_child = BTreeNode(leaf=child.leaf)
        
        parent.keys.insert(index, child.keys[degree-1])
        parent.values.insert(index, child.values[degree-1])
        
        new_child.keys = child.keys[degree:(2*degree-1)]
        new_child.values = child.values[degree:(2*degree-1)]
        child.keys = child.keys[0:(degree-1)]
        child.values = child.values[0:(degree-1)]
        
        if not child.leaf:
            new_child.children = child.children[degree:(2*degree)]
            child.children = child.children[0:degree]
            
        parent.children.insert(index+1, new_child)

class HashIndex:
    def __init__(self):
        self.index = {}
        
    def insert(self, key, value):
        if key not in self.index:
            self.index[key] = []
        self.index[key].append(value)
        
    def search(self, key):
        return self.index.get(key, [])

class insql:
    def __init__(self):
        self.current_db = None
        self.current_db_path = None
        self._data = None
        self._transaction_stack = []
        self._salt = None
        self._cache = {}
        self._last_cache_update = 0
        self._cache_ttl = 60
        self._check_concurrent_access()

    def _check_concurrent_access(self):
        global _open_databases, _last_access_time
        
        current_time = time.time()
        old_keys = [k for k, t in _last_access_time.items() if current_time - t > 300]
        for k in old_keys:
            _open_databases.pop(k, None)
            _last_access_time.pop(k, None)
            
        if len(_open_databases) >= MAX_CONCURRENT_DB:
            warnings.warn(
                f"Обнаружено {len(_open_databases)} одновременно открытых баз данных. "
                f"Рекомендуется использовать не более {MAX_CONCURRENT_DB}. "
                f"Добавлена задержка {WARNING_DELAY} сек для безопасности.",
                UserWarning
            )
            time.sleep(WARNING_DELAY)

    def _register_db_access(self):
        global _open_databases, _last_access_time
        if self.current_db_path:
            _open_databases[self.current_db_path] = self
            _last_access_time[self.current_db_path] = time.time()

    def _generate_salt(self) -> bytes:
        return secrets.token_bytes(8)

    def _is_cache_valid(self) -> bool:
        return (time.time() - self._last_cache_update) < self._cache_ttl

    def _update_cache(self, data: Any) -> None:
        self._cache = data
        self._last_cache_update = time.time()
        self._register_db_access()

    @contextmanager
    def transaction(self):
        self._begin_transaction()
        try:
            yield
            self._commit_transaction()
        except Exception as e:
            self._rollback_transaction()
            raise e

    def _begin_transaction(self):
        if not self._transaction_stack:
            self._load_database(self.current_db_path)
        self._transaction_stack.append(self._deepcopy(self._data))

    def _commit_transaction(self):
        if self._transaction_stack:
            self._transaction_stack.pop()
            self._save_database()
            self._update_cache(self._data)

    def _rollback_transaction(self):
        if self._transaction_stack:
            self._data = self._transaction_stack.pop()
            self._save_database()
            self._update_cache(self._data)

    def _deepcopy(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: self._deepcopy(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._deepcopy(item) for item in data]
        else:
            return data

    def create_database(self, db_name: str) -> bool:
        if not isinstance(db_name, str):
            raise TypeError("Database name must be a string")
        
        if not db_name.strip():
            raise ValueError("Database name cannot be empty")
        
        if not db_name.endswith('.insql'):
            db_name += '.insql'
        
        try:
            if os.path.exists(db_name):
                self._load_database(db_name)
                return True
            
            self._data = {"tables": {}, "metadata": {"version": VERSION}}
            self._salt = self._generate_salt()
            
            with open(db_name, 'wb') as f:
                f.write(MAGIC_NUMBER)
                f.write(struct.pack('!B', VERSION))
                f.write(self._salt)
                
                self._write_value(f, self._data)
            
            self.current_db = db_name
            self.current_db_path = db_name
            self._update_cache(self._data)
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to create database: {str(e)}")

    def _write_value(self, f, value):
        if value is None:
            f.write(b'\x00')
        elif isinstance(value, bool):
            f.write(b'\x01' + struct.pack('?', value))
        elif isinstance(value, int):
            f.write(b'\x02' + struct.pack('q', value))
        elif isinstance(value, float):
            f.write(b'\x03' + struct.pack('d', value))
        elif isinstance(value, str):
            encoded = value.encode('utf-8')
            f.write(b'\x04' + struct.pack('I', len(encoded)) + encoded)
        elif isinstance(value, list):
            f.write(b'\x05')
            f.write(struct.pack('I', len(value)))
            for item in value:
                self._write_value(f, item)
        elif isinstance(value, dict):
            f.write(b'\x06')
            f.write(struct.pack('I', len(value)))
            for k, v in value.items():
                self._write_value(f, k)
                self._write_value(f, v)
        elif isinstance(value, BTree):
            f.write(b'\x07')
            nodes = []
            self._serialize_btree(value.root, nodes)
            self._write_value(f, nodes)
        elif isinstance(value, HashIndex):
            f.write(b'\x08')
            self._write_value(f, value.index)
        else:
            raise ValueError(f"Unsupported type: {type(value)}")

    def _serialize_btree(self, node, nodes_list):
        node_data = {
            'leaf': node.leaf,
            'keys': node.keys,
            'values': node.values,
            'children_count': len(node.children)
        }
        nodes_list.append(node_data)
        if not node.leaf:
            for child in node.children:
                self._serialize_btree(child, nodes_list)

    def _read_value(self, f):
        type_byte = f.read(1)
        if not type_byte:
            raise EOFError("Unexpected end of file")
        
        if type_byte == b'\x00':  # None
            return None
        elif type_byte == b'\x01':  # bool
            return struct.unpack('?', f.read(1))[0]
        elif type_byte == b'\x02':  # int
            return struct.unpack('q', f.read(8))[0]
        elif type_byte == b'\x03':  # float
            return struct.unpack('d', f.read(8))[0]
        elif type_byte == b'\x04':  # str
            length = struct.unpack('I', f.read(4))[0]
            return f.read(length).decode('utf-8')
        elif type_byte == b'\x05':  # list
            length = struct.unpack('I', f.read(4))[0]
            return [self._read_value(f) for _ in range(length)]
        elif type_byte == b'\x06':  # dict
            length = struct.unpack('I', f.read(4))[0]
            result = {}
            for _ in range(length):
                key = self._read_value(f)
                value = self._read_value(f)
                result[key] = value
            return result
        elif type_byte == b'\x07':
            nodes_data = self._read_value(f)
            if not nodes_data:
                return BTree()
            tree = BTree()
            tree.root = self._deserialize_btree(nodes_data)
            return tree
        elif type_byte == b'\x08':
            index_data = self._read_value(f)
            index = HashIndex()
            index.index = index_data
            return index
        else:
            raise ValueError(f"Unknown type byte: {type_byte}")

    def _deserialize_btree(self, nodes_data):
        if not nodes_data:
            return None
        
        nodes = []
        for node_data in nodes_data:
            node = BTreeNode(leaf=node_data['leaf'])
            node.keys = node_data['keys']
            node.values = node_data['values']
            nodes.append(node)
        
        node_index = 0
        for node_data in nodes_data:
            node = nodes[node_index]
            if not node.leaf:
                for _ in range(node_data['children_count']):
                    node_index += 1
                    child = nodes[node_index]
                    node.children.append(child)
            node_index += 1
        
        return nodes[0] if nodes else None

    def _load_database(self, db_path: str) -> None:
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
        
        if self._is_cache_valid() and self.current_db_path == db_path:
            self._data = self._deepcopy(self._cache)
            return
            
        with open(db_path, 'rb') as f:
            magic = f.read(7)
            if magic != MAGIC_NUMBER:
                raise ValueError("Invalid database file format")
            
            version = struct.unpack('B', f.read(1))[0]
            if version != VERSION:
                raise ValueError(f"Unsupported database version: {version}")
            
            self._salt = f.read(8)
            self._data = self._read_value(f)
            self.current_db = os.path.basename(db_path)
            self.current_db_path = db_path
            self._update_cache(self._data)

    def _save_database(self) -> None:
        if not self.current_db_path:
            raise RuntimeError("No database path set")
        
        temp_path = self.current_db_path + '.tmp'
        with open(temp_path, 'wb') as f:
            f.write(MAGIC_NUMBER)
            f.write(struct.pack('B', VERSION))
            f.write(self._salt if self._salt else self._generate_salt())
            
            self._write_value(f, self._data)
        
        os.replace(temp_path, self.current_db_path)
        self._update_cache(self._data)

    def create_table(self, table_name: str, columns: List[str], primary_key: Optional[str] = None) -> bool:
        if not self.current_db:
            raise RuntimeError("No database selected")
        
        if not isinstance(table_name, str):
            raise TypeError("Table name must be a string")
        
        if primary_key and primary_key not in columns:
            raise ValueError(f"Primary key '{primary_key}' not in columns")
        
        if not self._data or not self._is_cache_valid():
            self._load_database(self.current_db_path)
        
        if table_name in self._data["tables"]:
            existing = self._data["tables"][table_name]
            if existing["columns"] != columns or existing.get("primary_key") != primary_key:
                raise ValueError("Table already exists with different structure")
            return False
        
        self._data["tables"][table_name] = {
            "columns": columns,
            "rows": [],
            "primary_key": primary_key,
            "indexes": {}
        }
        self._save_database()
        return True

    def create_index(self, table_name: str, column: str, index_type: str = 'hash') -> bool:
        if not self.current_db:
            raise RuntimeError("No database selected")
        
        if not self._data or not self._is_cache_valid():
            self._load_database(self.current_db_path)
        
        if table_name not in self._data["tables"]:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        if column not in self._data["tables"][table_name]["columns"]:
            raise ValueError(f"Column '{column}' does not exist")
        
        if column in self._data["tables"][table_name]["indexes"]:
            return False
        
        if index_type == 'btree':
            index = BTree()
            for idx, row in enumerate(self._data["tables"][table_name]["rows"]):
                val = row.get(column)
                index.insert(val, idx)
        else:
            index = HashIndex()
            for idx, row in enumerate(self._data["tables"][table_name]["rows"]):
                val = row.get(column)
                index.insert(val, idx)
        
        self._data["tables"][table_name]["indexes"][column] = index
        self._save_database()
        return True

    def insert(self, table_name: str, data: Dict, skip_duplicates: bool = True) -> bool:
        if not self.current_db:
            raise RuntimeError("No database selected")
        
        if not self._data or not self._is_cache_valid():
            self._load_database(self.current_db_path)
        
        table = self._data["tables"].get(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        if table["primary_key"] and table["primary_key"] in data:
            pk_val = data[table["primary_key"]]
            if any(row.get(table["primary_key"]) == pk_val for row in table["rows"]):
                if skip_duplicates:
                    return False
                raise ValueError(f"Duplicate primary key: {pk_val}")
        
        new_index = len(table["rows"])
        
        if table["indexes"]:
            for col, index in table["indexes"].items():
                val = data.get(col)
                if isinstance(index, BTree):
                    index.insert(val, new_index)
                else:
                    if val not in index.index:
                        index.index[val] = []
                    index.index[val].append(new_index)
        
        table["rows"].append(data)
        self._save_database()
        return True

    def search(self, table_name: str, condition: Callable[[Dict], bool]) -> List[Dict]:
        if not self.current_db:
            raise RuntimeError("No database selected")
        
        if not self._data or not self._is_cache_valid():
            self._load_database(self.current_db_path)
        
        table = self._data["tables"].get(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        return [row for row in table["rows"] if condition(row)]

    def search_by_index(self, table_name: str, column: str, value: Union[str, int]) -> List[Dict]:
        if not self.current_db:
            raise RuntimeError("No database selected")
        
        if not self._data or not self._is_cache_valid():
            self._load_database(self.current_db_path)
        
        table = self._data["tables"].get(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        if column not in table["indexes"]:
            raise ValueError(f"No index on column '{column}'")
        
        index = table["indexes"][column]
        if isinstance(index, BTree):
            row_indices = index.search(value)
            if row_indices is None:
                return []
            return [table["rows"][row_indices]] if not isinstance(row_indices, list) else [table["rows"][i] for i in row_indices]
        else:
            return [table["rows"][i] for i in index.search(value)]

    def get_by_id(self, table_name: str, pk_value: Union[str, int]) -> Optional[Dict]:
        if not self.current_db:
            raise RuntimeError("No database selected")
        
        if not self._data or not self._is_cache_valid():
            self._load_database(self.current_db_path)
        
        table = self._data["tables"].get(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        if not table["primary_key"]:
            raise ValueError("Table has no primary key")
        
        if table["primary_key"] in table["indexes"]:
            results = self.search_by_index(table_name, table["primary_key"], pk_value)
            return results[0] if results else None
        
        for row in table["rows"]:
            if row.get(table["primary_key"]) == pk_value:
                return row
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._save_database()
        return False

    def __repr__(self) -> str:
        return f"InSQL(database='{self.current_db}')"