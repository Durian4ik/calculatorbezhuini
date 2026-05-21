# app.py
from flask import Flask, request, render_template, jsonify
from m5_database import M5Database
from m1_alphabet import M1Alphabet
from m2_rules import M2Rules
from m3_calculation import M3Calculation
from m4_report import M4Report

app = Flask(__name__)

# Глобальный объект БД (один на всё приложение)
db = M5Database()


@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """API для калькулятора - берёт результат из БД (из уже вычисленной таблицы)"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])

        print(f"[API] Получен запрос: {symbols}")

        if len(symbols) < 2:
            return jsonify({'success': False, 'error': 'Нужно минимум 2 символа'})

        alpha_id = db.get_current_alpha_id()
        if not alpha_id:
            return jsonify({'success': False, 'error': 'Сначала вычислите таблицу сложения'})

        # Берём первое значение
        current = symbols[0]
        steps = []
        last_carry = 0

        # Для каждого следующего символа - берём результат из БД
        for next_sym in symbols[1:]:
            # ЗАПРОС К БД: ищем результат сложения current + next_sym
            db.cursor.execute(
                """SELECT result_char, carry FROM t_addition_result 
                   WHERE alpha_id = %s AND sym_i = %s AND sym_j = %s""",
                (alpha_id, current, next_sym)
            )
            row = db.cursor.fetchone()

            if row:
                result = row[0]
                carry = row[1] if row[1] else 0
                last_carry = carry

                if carry > 0:
                    steps.append(f"{current} + {next_sym} = {result} (перенос {carry})")
                else:
                    steps.append(f"{current} + {next_sym} = {result}")

                current = result
            else:
                # Если не нашли в БД (например, симметричная пара)
                # Пробуем найти sym_j + sym_i
                db.cursor.execute(
                    """SELECT result_char, carry FROM t_addition_result 
                       WHERE alpha_id = %s AND sym_i = %s AND sym_j = %s""",
                    (alpha_id, next_sym, current)
                )
                row = db.cursor.fetchone()
                if row:
                    result = row[0]
                    carry = row[1] if row[1] else 0
                    last_carry = carry
                    steps.append(f"{current} + {next_sym} = {result} (коммутативность)" +
                                 (f" (перенос {carry})" if carry > 0 else ""))
                    current = result
                else:
                    steps.append(f"{current} + {next_sym} = НЕ НАЙДЕНО В БД")
                    current = "?"

        print(f"[API] Результат: {current}, последний перенос: {last_carry}")

        return jsonify({
            'success': True,
            'result': current,
            'carry': last_carry,
            'steps': steps
        })

    except Exception as e:
        print(f"[API] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/')
def index():
    """Главная страница — форма ввода алфавита"""
    return render_template('index.html', alphabet=None, table=None, error=None)


@app.route('/calculate', methods=['POST'])
def calculate():
    """Обработка формы: принимает алфавит, вычисляет таблицу, возвращает результат"""

    # Получаем алфавит из формы
    alphabet_input = request.form.get('alphabet', '').strip()

    # Ручной ввод через пробел: "0 1 2 3 4 10 11 12"
    alphabet_chars = alphabet_input.split()


    # Проверка: минимум 2 символа
    if len(alphabet_chars) < 2:
        return render_template('index.html',
                               alphabet=None,
                               table=None,
                               error="Ошибка: алфавит должен содержать минимум 2 символа")

    # Проверка на запрещённые символы
    forbidden = ['$', '^']
    for ch in alphabet_chars:
        if ch in forbidden:
            return render_template('index.html',
                                   alphabet=None,
                                   table=None,
                                   error=f"Ошибка: символ '{ch}' запрещён")

    # Проверка на дубликаты
    if len(alphabet_chars) != len(set(alphabet_chars)):
        return render_template('index.html',
                               alphabet=None,
                               table=None,
                               error="Ошибка: в алфавите не должно быть повторяющихся символов")

    try:
        # Подключаемся к БД
        if not db.connect(password='postgres'):  # поменяй пароль если нужно
            return render_template('index.html',
                                   alphabet=None,
                                   table=None,
                                   error="Ошибка подключения к базе данных")

        # М2: инициализация правил (если нет)
        m2 = M2Rules(db)
        m2.init_rules()

        # Сохраняем алфавит через М1 (имитируем ввод)
        alphabet_str = ' '.join(alphabet_chars)
        alpha_id = db.save_alphabet(alphabet_str, '$')

        # М2: именованные колонки
        m2.build_alphabet_columns(alpha_id, alphabet_chars)

        # М3: вычисления
        m3 = M3Calculation(db)
        m3.calculate_full_table(alpha_id)

        # М4: получение таблицы
        m4 = M4Report(db)
        table_data = m4.get_table_dict(alpha_id)  # новый метод, напишем ниже

        return render_template('index.html',
                               alphabet=alphabet_chars,
                               table=table_data,
                               error=None)

    except Exception as e:
        return render_template('index.html',
                               alphabet=None,
                               table=None,
                               error=f"Ошибка: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)