# main.py
from m5_database import M5Database
from m1_alphabet import M1Alphabet
from m2_rules import M2Rules
from m3_calculation import M3Calculation
from m4_report import M4Report


def main():
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА: СИСТЕМА ДВОИЧНОГО СЛОЖЕНИЯ")
    print("=" * 60)

    # 1. Инициализация М5 (БД)
    db = M5Database()
    db.connect()
    print("✓ М5: Подключение к PostgreSQL установлено")

    # 2. М2: Запись аксиом (разовая инициализация)
    m2 = M2Rules(db)
    m2.init_rules()

    # 3. М1: Ввод алфавита пользователем
    m1 = M1Alphabet(db)
    alpha_id = m1.input_alphabet()

    # 4. М2: Формирование именованных колонок
    alphabet_list = db.get_alphabet_list(alpha_id)
    m2.build_alphabet_columns(alpha_id, alphabet_list)

    # 5. М3: Вычисление таблицы сложения
    m3 = M3Calculation(db)
    m3.calculate_addition_table(alpha_id)

    # 6. М4: Вывод отчёта (таблицы)
    m4 = M4Report(db)
    m4.print_addition_table(alpha_id)

    # 7. Завершение
    db.close()
    print("\n✓ Работа завершена. Данные сохранены в PostgreSQL.")
    print("  Для повторного просмотра таблицы выполните SQL-запрос к v_addition_table")


if __name__ == "__main__":
    main()
