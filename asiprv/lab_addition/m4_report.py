# m4_report.py
class M4Report:
    """Модуль формирования отчёта. Строит таблицу сложения."""

    def __init__(self, db):
        self.db = db

    def print_addition_table(self, alpha_id):
        """Вывести таблицу сложения"""

        # ИСПРАВЛЕНО: используем get_alphabet_list вместо list(alphabet_str)
        alphabet = self.db.get_alphabet_list(alpha_id)
        n = len(alphabet)

        # Получаем результаты из представления
        self.db.cursor.execute(
            "SELECT sym_i, sym_j, cell_value FROM v_addition_table WHERE alpha_id = %s ORDER BY sym_i, sym_j",
            (alpha_id,)
        )
        rows = self.db.cursor.fetchall()

        # Строим словарь для быстрого доступа
        table = {}
        for row in rows:
            i = row[0]
            j = row[1]
            val = row[2]
            table[(i, j)] = val

        print("\n" + "=" * 60)
        print("ТАБЛИЦА СЛОЖЕНИЯ")
        print("=" * 60)

        # Заголовок
        header = "     " + " ".join(f"{s:>4}" for s in alphabet)
        print(header)
        print("    " + "-" * (5 * n + 2))

        # Строки таблицы
        for i in alphabet:
            row_str = f"{i:2} |"
            for j in alphabet:
                val = table.get((i, j), "")
                if val == "":
                    val = table.get((j, i), "")
                row_str += f"{val:>4}"
            print(row_str)

        print("=" * 60)

    def get_table_dict(self, alpha_id):
        """Вернуть таблицу сложения в виде словаря для отображения в HTML"""

        # ИСПРАВЛЕНО: используем get_alphabet_list вместо list(alphabet_str)
        alphabet = self.db.get_alphabet_list(alpha_id)
        n = len(alphabet)

        # Получаем результаты
        self.db.cursor.execute(
            "SELECT sym_i, sym_j, cell_value FROM v_addition_table WHERE alpha_id = %s",
            (alpha_id,)
        )
        rows = self.db.cursor.fetchall()

        # Строим словарь
        table = {}
        for row in rows:
            i = row[0]
            j = row[1]
            val = row[2]
            table[(i, j)] = val

        # Дозаполняем симметричные ячейки
        for i in alphabet:
            for j in alphabet:
                if (i, j) not in table and (j, i) in table:
                    table[(i, j)] = table[(j, i)]

        # Формируем матрицу для шаблона
        matrix = []
        for i in alphabet:
            row = []
            for j in alphabet:
                row.append(table.get((i, j), ""))
            matrix.append(row)

        return {
            'alphabet': alphabet,
            'matrix': matrix
        }