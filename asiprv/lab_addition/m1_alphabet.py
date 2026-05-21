# m1_alphabet.py
class M1Alphabet:
    """Модуль работы с алфавитом. Принимает ввод, проверяет, передаёт в М5."""

    def __init__(self, db):
        self.db = db  # ссылка на М5
        self.alphabet_chars = []
        self.FLAG = '$'
        self.FORBIDDEN = [self.FLAG, '^']  # запрещённые символы (^ - для разряда)

    def input_alphabet(self):
        """Интерактивный ввод алфавита от пользователя"""
        print("\n=== Ввод алфавита ===")
        print("Вводите символы (цифры/буквы) по одному.")
        print(f"Запрещённые символы: {self.FORBIDDEN}")
        print("Для завершения введите команду 'Сохранить алфавит'")
        print("-" * 40)

        while True:
            user_input = input("> ").strip()

            # Команда сохранения
            if user_input == "Сохранить алфавит":
                if len(self.alphabet_chars) < 2:
                    print("ОШИБКА: Алфавит должен содержать минимум 2 символа!")
                    continue
                break

            # Проверка на пустой ввод
            if not user_input:
                print("ОШИБКА: Введите символ или команду 'Сохранить алфавит'")
                continue

            # Проверка на запрещённые символы
            if user_input in self.FORBIDDEN:
                print(f"ОШИБКА: Символ '{user_input}' запрещён (служебный символ)")
                continue

            # Проверка на дубликаты
            if user_input in self.alphabet_chars:
                print(f"ОШИБКА: Символ '{user_input}' уже добавлен в алфавит")
                continue

            # Всё ок, добавляем
            self.alphabet_chars.append(user_input)
            print(f"Добавлен: {user_input}. Текущий алфавит: {self.alphabet_chars}")

        # Сохраняем в БД через М5
        alphabet_str = ''.join(self.alphabet_chars)
        alpha_id = self.db.save_alphabet(alphabet_str, self.FLAG)
        print(f"\nАлфавит сохранён! ID сессии: {alpha_id}")
        print(f"Алфавит: {self.alphabet_chars}")
        print(f"Флаг конца: '{self.FLAG}'")

        return alpha_id