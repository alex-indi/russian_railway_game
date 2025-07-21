# config.py
# Этот файл содержит все основные параметры и данные для настройки баланса игры.

# --- 1. ЭКОНОМИЧЕСКИЕ ПАРАМЕТРЫ ---
STARTING_MONEY = 2000  # Стартовый баланс игрока
REPAIR_LOCO = 500
REPAIR_WAGON = 400

GOODS_PRICES = {
    "Уголь": 120,
    "Щебень": 100,
    "Желтый": 100,
    "Зеленый": 110,
    "Синий": 140,
    "Металл": 800
}

WAGON_PRICES = {
    1: 3000,
    2: 3000,
    3: 3000,
    4: 3000,
    5: 5000
}

# --- 2. ПАРАМЕТРЫ СОСТАВА И ГРУЗОВ ---
WAGON_INFO = {
    1: {"name": "Полувагон 1", "type": "gondola"},
    2: {"name": "Контейнер 1", "type": "container"},
    3: {"name": "Полувагон 2", "type": "gondola"},
    4: {"name": "Контейнер 2", "type": "container"},
    5: {"name": "Платформа", "type": "platform"},
}

GOOD_COMPATIBILITY = {
    "Уголь": "gondola", "Щебень": "gondola", "Желтый": "container",
    "Зеленый": "container", "Синий": "container", "Металл": "platform"
}

# --- 3. ДАННЫЕ ДЛЯ ВИЗУАЛИЗАЦИИ ---
GOODS_HTML = {
    "Уголь": '<span style="font-size:20px;">⬛</span>',
    "Щебень": '<span style="font-size:20px; color:#888;">🟫</span>',
    "Желтый": '<span style="font-size:20px; color:#FFD700;">🟨</span>',
    "Зеленый": '<span style="font-size:20px; color:#228B22;">🟩</span>',
    "Синий": '<span style="font-size:20px; color:#0066FF;">🟦</span>',
    "Металл": '<span style="font-size:20px; color:#333;">⬜</span>',
    None: '<span style="font-size:20px; color:#ccc;">▫️</span>',
}
PLATFORM_EMPTY = '<span style="font-size:20px; color:#aaa;">⚪</span>'
PLATFORM_FULL = '<span style="font-size:20px; color:#000;">⚫</span>'

# --- 4. СПИСОК КОНТРАКТОВ ---
CONTRACTS = [
    {"id": "P1", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Уголь", "qty_1": 6, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P2", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Щебень", "qty_1": 6, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P3", "origin": "B", "destination": "A", "max_rounds": 3, "goods_1": "Желтый", "qty_1": 6, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P4", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Синий", "qty_1": 2, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P5", "origin": "B", "destination": "A", "max_rounds": 3, "goods_1": "Зеленый", "qty_1": 4, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P6", "origin": "B", "destination": "A", "max_rounds": 3, "goods_1": "Уголь", "qty_1": 4, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P7", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Щебень", "qty_1": 6, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P8", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Уголь", "qty_1": 2,
     "goods_2": "Желтый", "qty_2": 4, "goods_3": None, "qty_3": 0},
    {"id": "M1", "origin": "A", "destination": "B", "max_rounds": 2, "goods_1": "Уголь", "qty_1": 6,
     "goods_2": "Желтый", "qty_2": 6, "goods_3": None, "qty_3": 0},
    {"id": "M2", "origin": "B", "destination": "A", "max_rounds": 2, "goods_1": "Щебень", "qty_1": 9,
     "goods_2": "Синий", "qty_2": 2, "goods_3": None, "qty_3": 0},
    {"id": "M3", "origin": "A", "destination": "B", "max_rounds": 2, "goods_1": "Зеленый", "qty_1": 10, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "M4", "origin": "A", "destination": "B", "max_rounds": 2, "goods_1": "Уголь", "qty_1": 6,
     "goods_2": "Щебень", "qty_2": 4, "goods_3": None, "qty_3": 0},
    {"id": "M5", "origin": "B", "destination": "A", "max_rounds": 2, "goods_1": "Синий", "qty_1": 6, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "M6", "origin": "A", "destination": "B", "max_rounds": 2, "goods_1": "Уголь", "qty_1": 10,
     "goods_2": "Зеленый", "qty_2": 4, "goods_3": None, "qty_3": 0},
    {"id": "M7", "origin": "B", "destination": "A", "max_rounds": 2, "goods_1": "Щебень", "qty_1": 12,
     "goods_2": "Желтый", "qty_2": 6, "goods_3": None, "qty_3": 0},
    {"id": "M8", "origin": "A", "destination": "B", "max_rounds": 2, "goods_1": "Щебень", "qty_1": 6,
     "goods_2": "Желтый", "qty_2": 6, "goods_3": None, "qty_3": 0},
    {"id": "S1", "origin": "A", "destination": "B", "max_rounds": 1, "goods_1": "Металл", "qty_1": 1,
     "goods_2": "Уголь", "qty_2": 6, "goods_3": None, "qty_3": 0},
    {"id": "S2", "origin": "B", "destination": "A", "max_rounds": 1, "goods_1": "Металл", "qty_1": 2,
     "goods_2": "Щебень", "qty_2": 6, "goods_3": None, "qty_3": 0},
    {"id": "S3", "origin": "A", "destination": "B", "max_rounds": 1, "goods_1": "Зеленый", "qty_1": 6,
     "goods_2": "Синий", "qty_2": 6, "goods_3": None, "qty_3": 0},
    {"id": "S4", "origin": "A", "destination": "B", "max_rounds": 1, "goods_1": "Металл", "qty_1": 2,
     "goods_2": "Зеленый", "qty_2": 4, "goods_3": "Щебень", "qty_3": 4},
]

# --- 5. СПИСОК СОБЫТИЙ ---
EVENTS = [
    {"id": "E01", "group": "Нештатные", "name": "Поломка локомотива",
     "description": "−1 к техническому состоянию локомотива."},
    {"id": "E02", "group": "Нештатные", "name": "Текущий ремонт",
     "description": "+1 к техническому состоянию всему составу (включая локомотив)."},
    {"id": "E03", "group": "Нештатные", "name": "Поломка пути",
     "description": "−1 единица времени и 500 рублей на непредвиденный ремонт."},
    {"id": "E04", "group": "Нештатные", "name": "День железнодорожника",
     "description": "Коллеги поздравляют друг друга. Никаких эффектов."},
    {"id": "E05", "group": "Нештатные", "name": "Обвал тоннеля", "description": "−1000 рублей на расчистку путей."},
    {"id": "E06", "group": "Нештатные", "name": "Потеря груза",
     "description": "Вся прибыль от разгрузки в этом раунде снижена на 50%."},
    {"id": "E07", "group": "Нештатные", "name": "Капитальный ремонт",
     "description": "Техническое состояние всего поезда полностью восстановлено!"},
    {"id": "E08", "group": "Нештатные", "name": "Инновация",
     "description": "Стоимость ремонта локомотивов и вагонов снижена на 50% в этом раунде."},
    {"id": "E09", "group": "Нештатные", "name": "Поломка пути",
     "description": "−1 единица времени и 500 рублей на непредвиденный ремонт."},
    {"id": "E10", "group": "Нештатные", "name": "Текущий ремонт",
     "description": "+1 к техническому состоянию всему составу (включая локомотив)."},
    {"id": "E11", "group": "Нештатные", "name": "Поломка локомотива",
     "description": "−1 к техническому состоянию локомотива."},
    {"id": "E12", "group": "Нештатные", "name": "Дерево на пути", "description": "−800 рублей на расчистку."},
    {"id": "P01", "group": "Погодные", "name": "Дождь", "description": "−2 единицы времени из-за плохой видимости."},
    {"id": "P02", "group": "Погодные", "name": "Снегопад",
     "description": "−1 единица времени. Возможны дополнительные поломки."},
    {"id": "P03", "group": "Погодные", "name": "Туман", "description": "−1 единица времени."},
    {"id": "P04", "group": "Погодные", "name": "Ясная погода",
     "description": "Отличные условия для работы. Никаких эффектов."},
    {"id": "P05", "group": "Погодные", "name": "Ясная погода",
     "description": "Отличные условия для работы. Никаких эффектов."},
    {"id": "P06", "group": "Погодные", "name": "Гололёд",
     "description": "Погрузка и разгрузка теперь занимает 2 единицы времени вместо одной."},
    {"id": "P07", "group": "Погодные", "name": "Дождь", "description": "−2 единицы времени из-за плохой видимости."},
    {"id": "P08", "group": "Погодные", "name": "Туман", "description": "−1 единица времени."},
    {"id": "P09", "group": "Погодные", "name": "Снегопад",
     "description": "−1 единица времени. Возможны дополнительные поломки."},
    {"id": "P10", "group": "Погодные", "name": "Дождь", "description": "−2 единицы времени из-за плохой видимости."},
    {"id": "H01", "group": "Человеческий фактор", "name": "Болезнь машиниста",
     "description": "Движение между станциями теперь занимает 4 единицы времени."},
    {"id": "H02", "group": "Человеческий фактор", "name": "Болезнь составителя",
     "description": "Погрузка и разгрузка теперь занимает 2 единицы времени."},
    {"id": "H03", "group": "Человеческий фактор", "name": "Болезнь логиста",
     "description": "Вы не можете брать новые контракты в этом раунде."},
    {"id": "H04", "group": "Человеческий фактор", "name": "Болезнь логиста",
     "description": "Вы не можете брать новые контракты в этом раунде."},
    {"id": "H05", "group": "Человеческий фактор", "name": "Премия",
     "description": "Вы получаете премию в размере 1000 рублей."},
    {"id": "H06", "group": "Человеческий фактор", "name": "Машинист 1-ого класса",
     "description": "Движение между станциями в этом раунде не требует времени!"},
    {"id": "H07", "group": "Человеческий фактор", "name": "День рождения машиниста",
     "description": "Все поздравляют именинника. Никаких эффектов."},
    {"id": "H08", "group": "Человеческий фактор", "name": "Увольнение машиниста",
     "description": "−500 рублей на найм и обучение нового сотрудника."},
]
