# m2_rules.py
class M2Rules:
    """Модуль формирования правил и знаний. Хранит аксиомы как машиночитаемые условия."""

    def __init__(self, db):
        self.db = db

    def init_rules(self):
        """Записать 6 аксиом из документа в БД (если ещё не записаны)"""
        # Проверяем, есть ли уже правила
        existing = self.db.get_rules()
        if existing:
            print("Правила уже существуют в БД, пропускаем инициализацию")
            return

        # 6 аксиом в машиночитаемом виде
        rules = [
            {
                'name': 'Аксиома 1',
                'condition': 'elem == начало',
                'action': 'return_elem',
                'param': None
            },
            {
                'name': 'Аксиома 2',
                'condition': 'шаг_от_начала',
                'action': 'next_elem',
                'param': 1
            },
            {
                'name': 'Аксиома 3',
                'condition': 'idx >= len(алфавит)',
                'action': 'wrap_to_start',
                'param': None
            },
            {
                'name': 'Аксиома 4',
                'condition': 'wrap_occurred',
                'action': 'create_carry',
                'param': 1
            },
            {
                'name': 'Аксиома 5',
                'condition': 'True',
                'action': 'ordered',
                'param': None
            },
            {
                'name': 'Аксиома 6',
                'condition': 'True',
                'action': 'commutative',
                'param': None
            }
        ]

        self.db.save_rules(rules)
        print(f"Записано {len(rules)} аксиом в базу знаний")

    def build_alphabet_columns(self, alpha_id, alphabet_list):
        """Сформировать именованные колонки для алфавита"""
        self.db.save_alphabet_columns(alpha_id, alphabet_list)
        print(f"Сформированы именованные колонки: {alphabet_list}")