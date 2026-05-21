# m5_database.py (исправленный)
import psycopg2
from psycopg2.extras import RealDictCursor


class M5Database:
    """Единственная точка доступа к БД. Все модули получают ссылку на этот класс."""

    def __init__(self):
        self.host = 'localhost'
        self.port = 5432
        self.database = 'addition_lab'
        self.user = 'postgres'
        self.password = None
        self.conn = None
        self.cursor = None
        self.current_alpha_id = None

    def connect(self, password='postgres'):
        self.password = password
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            self._init_tables()
            print("✓ М5: Подключение к PostgreSQL установлено")
            return True
        except Exception as e:
            print(f"ОШИБКА подключения к БД: {e}")
            return False

    def _init_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS t_alphabet (
                alpha_id SERIAL PRIMARY KEY,
                alphabet_str TEXT NOT NULL,
                flag_char CHAR(1) DEFAULT '$',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS k_rules (
                rule_id SERIAL PRIMARY KEY,
                rule_name VARCHAR(50),
                condition TEXT,
                action TEXT,
                param INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS k_alphabet_columns (
                col_id SERIAL PRIMARY KEY,
                alpha_id INTEGER REFERENCES t_alphabet(alpha_id) ON DELETE CASCADE,
                position INTEGER,
                col_name VARCHAR(100)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS t_addition_result (
                result_id SERIAL PRIMARY KEY,
                alpha_id INTEGER REFERENCES t_alphabet(alpha_id) ON DELETE CASCADE,
                sym_i VARCHAR(100),
                sym_j VARCHAR(100),
                result_char VARCHAR(100),
                carry INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE OR REPLACE VIEW v_addition_table AS
            SELECT 
                alpha_id,
                sym_i,
                sym_j,
                CASE 
                    WHEN carry = 1 THEN result_char || '^' || carry
                    ELSE result_char
                END AS cell_value
            FROM t_addition_result
        """)
        self.conn.commit()

    def save_alphabet(self, alphabet_str, flag_char='$'):
        self.cursor.execute(
            "INSERT INTO t_alphabet (alphabet_str, flag_char) VALUES (%s, %s) RETURNING alpha_id",
            (alphabet_str, flag_char)
        )
        self.current_alpha_id = self.cursor.fetchone()[0]
        self.conn.commit()
        print(f"✓ М5: Алфавит '{alphabet_str}' сохранён, alpha_id={self.current_alpha_id}")
        return self.current_alpha_id

    def get_alphabet(self, alpha_id=None):
        if alpha_id is None:
            alpha_id = self.current_alpha_id
        self.cursor.execute(
            "SELECT alphabet_str FROM t_alphabet WHERE alpha_id = %s",
            (alpha_id,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    # ИСПРАВЛЕННЫЙ метод get_alphabet_list
    def get_alphabet_list(self, alpha_id=None):
        """Получить алфавит как список слов/символов"""
        alphabet_str = self.get_alphabet(alpha_id)
        if not alphabet_str:
            return []

        # Если есть пробелы - разбиваем по пробелам (слова)
        if ' ' in alphabet_str:
            return alphabet_str.split()
        else:
            # Если нет пробелов - разбиваем по символам (цифры/буквы)
            return list(alphabet_str)

    def get_alphabet_length(self, alpha_id=None):
        alphabet_list = self.get_alphabet_list(alpha_id)
        return len(alphabet_list) if alphabet_list else 0

    def save_rules(self, rules):
        self.cursor.execute("DELETE FROM k_rules")
        for rule in rules:
            self.cursor.execute(
                "INSERT INTO k_rules (rule_name, condition, action, param) VALUES (%s, %s, %s, %s)",
                (rule['name'], rule['condition'], rule['action'], rule.get('param'))
            )
        self.conn.commit()
        print(f"✓ М5: Сохранено {len(rules)} правил (аксиом)")

    def get_rules(self):
        if self.cursor is None or self.cursor.closed:
            self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM k_rules ORDER BY rule_id")
        return self.cursor.fetchall()

    def check_rules_exist(self):
        self.cursor.execute("SELECT COUNT(*) FROM k_rules")
        count = self.cursor.fetchone()[0]
        return count > 0

    def save_alphabet_columns(self, alpha_id, alphabet_list):
        self.cursor.execute("DELETE FROM k_alphabet_columns WHERE alpha_id = %s", (alpha_id,))
        for pos, symbol in enumerate(alphabet_list):
            self.cursor.execute(
                "INSERT INTO k_alphabet_columns (alpha_id, position, col_name) VALUES (%s, %s, %s)",
                (alpha_id, pos, str(symbol))
            )
        self.conn.commit()
        print(f"✓ М5: Сохранено {len(alphabet_list)} именованных колонок")

    def get_column_name(self, alpha_id, position):
        self.cursor.execute(
            "SELECT col_name FROM k_alphabet_columns WHERE alpha_id = %s AND position = %s",
            (alpha_id, position)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_all_columns(self, alpha_id=None):
        if alpha_id is None:
            alpha_id = self.current_alpha_id
        self.cursor.execute(
            "SELECT position, col_name FROM k_alphabet_columns WHERE alpha_id = %s ORDER BY position",
            (alpha_id,)
        )
        return {row[1]: row[0] for row in self.cursor.fetchall()}

    def save_addition_result(self, alpha_id, sym_i, sym_j, result_char, carry=None):
        if self.cursor is None or self.cursor.closed:
            self.cursor = self.conn.cursor()
        self.cursor.execute(
            """INSERT INTO t_addition_result (alpha_id, sym_i, sym_j, result_char, carry) 
               VALUES (%s, %s, %s, %s, %s)""",
            (alpha_id, sym_i, sym_j, result_char, carry)
        )
        self.conn.commit()

    def get_addition_results(self, alpha_id=None):
        if alpha_id is None:
            alpha_id = self.current_alpha_id
        if self.cursor is None or self.cursor.closed:
            self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT * FROM v_addition_table WHERE alpha_id = %s ORDER BY sym_i, sym_j",
            (alpha_id,)
        )
        return self.cursor.fetchall()

    def clear_addition_results(self, alpha_id=None):
        if alpha_id is None:
            alpha_id = self.current_alpha_id
        if self.cursor is None or self.cursor.closed:
            self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM t_addition_result WHERE alpha_id = %s", (alpha_id,))
        self.conn.commit()
        print(f"✓ М5: Очищены результаты сложения для alpha_id={alpha_id}")

    def clear_session(self, alpha_id=None):
        if alpha_id is None:
            alpha_id = self.current_alpha_id
        if self.cursor is None or self.cursor.closed:
            self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM t_addition_result WHERE alpha_id = %s", (alpha_id,))
        self.cursor.execute("DELETE FROM k_alphabet_columns WHERE alpha_id = %s", (alpha_id,))
        self.conn.commit()
        print(f"✓ М5: Очищены данные сессии для alpha_id={alpha_id}")

    def get_current_alpha_id(self):
        return self.current_alpha_id

    def is_connected(self):
        try:
            if self.conn is None:
                return False
            if self.conn.closed:
                return False
            if self.cursor is None or self.cursor.closed:
                self.cursor = self.conn.cursor()
                return True
            return True
        except:
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ М5: Соединение с PostgreSQL закрыто")