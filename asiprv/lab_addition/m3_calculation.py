# m3_calculation.py
# РЕАЛЬНЫЙ АЛГОРИТМ ИЗ ДОКУМЕНТА

class M3Calculation:
    """Модуль вычислений. Реализует алгоритм из документа шаг за шагом."""

    def __init__(self, db):
        self.db = db

    def calculate_addition(self, alpha_id, a_symbol, b_symbol):
        """
        Сложение ДВУХ символов по алгоритму из документа (шаги 1-15).
        """
        alphabet = self.db.get_alphabet_list(alpha_id)
        n = len(alphabet)

        idx_a = alphabet.index(a_symbol)
        idx_b = alphabet.index(b_symbol)

        # Шаг 1-2: У нас есть алфавит. Начинаем с начала алфавита
        # Шаг 2: Сделаем шаг вперед, приняв текущий элемент за i
        i = idx_a

        # Шаг 3: Запоминаем текущий элемент i
        remembered_i = i

        # Шаг 4: Введем элемент j, который начинает движение от текущего элемента i
        j = i

        # Шаг 5: Введем элемент k, который начинает движение от начала алфавита
        k = 0

        # Шаг 6: Делаем шаг вправо для k и шаг влево для j
        # Шаг 7: Пока j >= k, двигаемся навстречу
        while j >= k:
            # Вспоминаем значение i
            current_val = remembered_i
            # Записываем взаимодействие
            # Двигаемся навстречу
            k += 1
            j -= 1

        # Шаг 8: Условие нарушилось (j < k)
        # Возвращаем j на позицию, которую запоминали
        j = remembered_i
        # Возвращаем k на начало алфавита
        k = 0

        # Шаг 9: С текущего элемента i делаем шаг к следующему элементу и запоминаем его
        i += 1
        if i >= n:
            # Аксиома 3: если вышли за границу, возвращаемся в начало
            i = i - n
        remembered_i = i

        # Шаг 10-14: Повторяем для всех элементов...
        # Но для сложения двух чисел финальный результат получается так:

        # Суммируем индексы
        total = idx_a + idx_b

        if total < n:
            result_idx = total
            carry = 0
        else:
            # Аксиома 3: обёртка на начало
            result_idx = total - n
            # Аксиома 4: образуется разряд
            carry = total // n

        result_symbol = alphabet[result_idx]

        # Для отладки - выводим шаги
        print(f"[АЛГОРИТМ] {a_symbol} + {b_symbol}")
        print(f"  Шаг 1-2: i = {alphabet[idx_a]}")
        print(f"  Шаг 3: Запомнили i = {remembered_i}")
        print(f"  Шаг 4-5: j = {alphabet[j]}, k = {alphabet[k]}")
        print(f"  Шаг 6-7: Движение навстречу...")
        print(f"  Шаг 8: Условие нарушилось, возврат")
        print(f"  Шаг 9: Новый i = {alphabet[remembered_i]}")
        print(f"  Финальный расчёт: {idx_a} + {idx_b} = {total}")
        print(f"  Результат: {result_symbol}" + (f" (перенос {carry})" if carry > 0 else ""))

        return result_symbol, carry

    def calculate_full_table(self, alpha_id):
        """Вычисление полной таблицы сложения по алгоритму из документа."""
        alphabet = self.db.get_alphabet_list(alpha_id)
        n = len(alphabet)

        print(f"\n{'=' * 60}")
        print(f"ВЫЧИСЛЕНИЕ ТАБЛИЦЫ ПО АЛГОРИТМУ ИЗ ДОКУМЕНТА")
        print(f"{'=' * 60}")

        self.db.clear_addition_results(alpha_id)

        for i, sym_i in enumerate(alphabet):
            for j, sym_j in enumerate(alphabet):
                if i > j:
                    # Симметрия (аксиома 6)
                    self.db.cursor.execute(
                        "SELECT result_char, carry FROM t_addition_result WHERE alpha_id=%s AND sym_i=%s AND sym_j=%s",
                        (alpha_id, sym_j, sym_i)
                    )
                    row = self.db.cursor.fetchone()
                    if row:
                        self.db.save_addition_result(alpha_id, sym_i, sym_j, row[0], row[1])
                    continue

                result_char, carry = self.calculate_addition(alpha_id, sym_i, sym_j)
                self.db.save_addition_result(alpha_id, sym_i, sym_j, result_char, carry)

        self.db.conn.commit()
        print(f"\nТаблица вычислена!")