import random
from copy import deepcopy

import streamlit as st

# --- КОНФИГУРАЦИЯ И КОНСТАНТЫ ---
# Цены на товары
GOODS_PRICES = {
    "Уголь": 100,
    "Щебень": 80,
    "Желтый": 80,
    "Зеленый": 90,
    "Синий": 110,
    "Металл": 800,
}

# Ремонт и кредит
REPAIR_LOCO = 400
REPAIR_WAGON = 300
CREDIT_GIVE = 3000
CREDIT_PAY = 4000

# Цены на покупку новых вагонов
WAGON_PRICES = {
    1: 3000,  # Полувагон
    2: 3000,  # Контейнер
    3: 3000,  # Полувагон
    4: 3000,  # Контейнер
    5: 5000  # Платформа
}

# Описание вагонов
WAGON_INFO = {
    1: {"name": "Полувагон 1", "type": "gondola", "capacity": 6},
    2: {"name": "Контейнер 1", "type": "container", "capacity": 6},
    3: {"name": "Полувагон 2", "type": "gondola", "capacity": 6},
    4: {"name": "Контейнер 2", "type": "container", "capacity": 6},
    5: {"name": "Платформа", "type": "platform", "capacity": 3},
}

GOOD_COMPATIBILITY = {
    "Уголь": "gondola",
    "Щебень": "gondola",
    "Желтый": "container",
    "Зеленый": "container",
    "Синий": "container",
    "Металл": "platform",
}

# Список всех контрактов в игре
CONTRACTS = [
    {"id": "P1", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Уголь", "qty_1": 5, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P2", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Щебень", "qty_1": 6, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P3", "origin": "B", "destination": "A", "max_rounds": 3, "goods_1": "Желтый", "qty_1": 6, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P4", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Синий", "qty_1": 3, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P5", "origin": "B", "destination": "A", "max_rounds": 3, "goods_1": "Зеленый", "qty_1": 4, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P6", "origin": "B", "destination": "A", "max_rounds": 3, "goods_1": "Уголь", "qty_1": 4, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P7", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Щебень", "qty_1": 5, "goods_2": None,
     "qty_2": 0, "goods_3": None, "qty_3": 0},
    {"id": "P8", "origin": "A", "destination": "B", "max_rounds": 3, "goods_1": "Уголь", "qty_1": 2,
     "goods_2": "Желтый", "qty_2": 3, "goods_3": None, "qty_3": 0},
    {"id": "M1", "origin": "A", "destination": "B", "max_rounds": 2, "goods_1": "Уголь", "qty_1": 6,
     "goods_2": "Желтый", "qty_2": 6, "goods_3": None, "qty_3": 0},
    {"id": "M2", "origin": "B", "destination": "A", "max_rounds": 2, "goods_1": "Щебень", "qty_1": 9,
     "goods_2": "Синий", "qty_2": 3, "goods_3": None, "qty_3": 0},
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

# --- СПИСОК ВСЕХ СОБЫТИЙ В ИГРЕ ---
EVENTS = [
    # Нештатные
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
     "description": "Вы теряете самый дешевый из ваших активных контрактов."},
    {"id": "E07", "group": "Нештатные", "name": "Капитальный ремонт",
     "description": "Техническое состояние всего поезда полностью восстановлено!"},
    {"id": "E08", "group": "Нештатные", "name": "Инновация",
     "description": "Стоимость ремонта локомотивов и вагонов снижена на 50% в этом раунде."},
    {"id": "E09", "group": "Нештатные", "name": "Поломка пути",
     "description": "−1 единица времени и 500 рублей на непредвиденный ремонт."},  # Дубликат по заданию
    {"id": "E10", "group": "Нештатные", "name": "Текущий ремонт",
     "description": "+1 к техническому состоянию всему составу (включая локомотив)."},  # Дубликат по заданию
    {"id": "E11", "group": "Нештатные", "name": "Поломка локомотива",
     "description": "−1 к техническому состоянию локомотива."},  # Дубликат по заданию
    {"id": "E12", "group": "Нештатные", "name": "Дерево на пути", "description": "−800 рублей на расчистку."},
    # Погодные
    {"id": "P01", "group": "Погодные", "name": "Дождь", "description": "−2 единицы времени из-за плохой видимости."},
    {"id": "P02", "group": "Погодные", "name": "Снегопад",
     "description": "−1 единица времени. Возможны дополнительные поломки."},
    {"id": "P03", "group": "Погодные", "name": "Туман", "description": "−1 единица времени."},
    {"id": "P04", "group": "Погодные", "name": "Ясная погода",
     "description": "Отличные условия для работы. Никаких эффектов."},
    {"id": "P05", "group": "Погодные", "name": "Ясная погода",
     "description": "Отличные условия для работы. Никаких эффектов."},  # Дубликат по заданию
    {"id": "P06", "group": "Погодные", "name": "Гололёд",
     "description": "Погрузка и разгрузка теперь занимает 2 единицы времени вместо одной."},
    {"id": "P07", "group": "Погодные", "name": "Дождь", "description": "−2 единицы времени из-за плохой видимости."},
    # Дубликат по заданию
    {"id": "P08", "group": "Погодные", "name": "Туман", "description": "−1 единица времени."},  # Дубликат по заданию
    {"id": "P09", "group": "Погодные", "name": "Снегопад",
     "description": "−1 единица времени. Возможны дополнительные поломки."},  # Дубликат по заданию
    {"id": "P10", "group": "Погодные", "name": "Дождь", "description": "−2 единицы времени из-за плохой видимости."},
    # Дубликат по заданию
    # Человеческий фактор
    {"id": "H01", "group": "Человеческий фактор", "name": "Болезнь машиниста",
     "description": "Движение между станциями теперь занимает 4 единицы времени."},
    {"id": "H02", "group": "Человеческий фактор", "name": "Болезнь составителя",
     "description": "Погрузка и разгрузка теперь занимает 2 единицы времени."},
    {"id": "H03", "group": "Человеческий фактор", "name": "Болезнь логиста",
     "description": "Вы не можете брать новые контракты в этом раунде."},
    {"id": "H04", "group": "Человеческий фактор", "name": "Болезнь логиста",
     "description": "Вы не можете брать новые контракты в этом раунде."},  # Дубликат по заданию
    {"id": "H05", "group": "Человеческий фактор", "name": "Премия",
     "description": "Вы получаете премию в размере 1000 рублей."},
    {"id": "H06", "group": "Человеческий фактор", "name": "Машинист 1-ого класса",
     "description": "Движение между станциями в этом раунде не требует времени!"},
    {"id": "H07", "group": "Человеческий фактор", "name": "День рождения машиниста",
     "description": "Все поздравляют именинника. Никаких эффектов."},
    {"id": "H08", "group": "Человеческий фактор", "name": "Увольнение машиниста",
     "description": "−500 рублей на найм и обучение нового сотрудника."},
]

# Карта отображения грузов
GOODS_HTML = {
    "Уголь": '<span style="font-size:20px;">⬛</span>', "Щебень": '<span style="font-size:20px; color:#888;">⬜</span>',
    "Желтый": '<span style="font-size:20px; color:#FFD700;">🟨</span>',
    "Зеленый": '<span style="font-size:20px; color:#228B22;">🟩</span>',
    "Синий": '<span style="font-size:20px; color:#0066FF;">🟦</span>',
    "Металл": '<span style="font-size:20px; color:#bbb;">⬜</span>',
    None: '<span style="font-size:20px; color:#ccc;">▫️</span>',
}
PLATFORM_EMPTY = '<span style="font-size:20px; color:#aaa;">⚪</span>'
PLATFORM_FULL = '<span style="font-size:20px; color:#000;">⚫</span>'


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def start_new_game():
    """Полностью очищает состояние сессии, чтобы начать игру заново."""
    # Получаем список всех ключей, которые есть в состоянии
    keys_to_delete = list(st.session_state.keys())
    # Удаляем каждый ключ
    for key in keys_to_delete:
        del st.session_state[key]
    # Принудительно перезапускаем скрипт, чтобы сработал блок инициализации
    st.rerun()

def contract_price(contract):
    s = 0
    for g, q in [(contract["goods_1"], contract["qty_1"]), (contract["goods_2"], contract["qty_2"]),
                 (contract["goods_3"], contract["qty_3"])]:
        if g and q: s += GOODS_PRICES[g] * q
    return s


def calculate_current_price(contract):
    """Вычисляет ТЕКУЩУЮ стоимость контракта с учетом штрафов за просрочку."""
    base_price = contract_price(contract)
    rounds_left = contract.get('rounds_left', contract['max_rounds'])
    max_rounds = contract['max_rounds']

    multiplier = 1.0

    # Правила для простых контрактов
    if contract['id'].startswith('P'):  # max_rounds = 3
        if rounds_left <= 0:
            multiplier = 0.0
        elif rounds_left == 1:
            multiplier = 0.3
        elif rounds_left == 2:
            multiplier = 0.6

    # Правила для средних контрактов
    elif contract['id'].startswith('M'):  # max_rounds = 2
        if rounds_left <= 0:
            multiplier = 0.0
        elif rounds_left == 1:
            multiplier = 0.5

    # Правила для сложных контрактов
    elif contract['id'].startswith('S'):  # max_rounds = 1
        if rounds_left <= 0: multiplier = 0.0

    return int(base_price * multiplier)

def get_wagon_fill_html(contents, capacity):  # Аргумент переименован с hp на capacity
    html = ''
    for i in range(capacity):  # Используем capacity напрямую
        html += GOODS_HTML.get(contents[i]['good'] if i < len(contents) else None, GOODS_HTML[None])
    return html


def get_platform_fill_html(contents, capacity):  # Аргумент переименован с hp на capacity
    html = ''
    for i in range(capacity):  # Используем capacity напрямую
        html += PLATFORM_FULL if i < len(contents) else PLATFORM_EMPTY
    return html


def get_available_capacity():
    """Считает общую свободную вместимость всех купленных вагонов."""
    total_capacity = 0
    total_load = 0
    for i in range(1, 6):
        if st.session_state[f"wagon_{i}_is_purchased"]:
            # Берем постоянную вместимость из WAGON_INFO
            total_capacity += WAGON_INFO[i]["capacity"]
            total_load += len(st.session_state[f"wagon_{i}_contents"])
    return total_capacity - total_load


def get_current_capacity(wagon_index):
    """Возвращает ТЕКУЩУЮ вместимость вагона в зависимости от его HP."""
    hp = st.session_state[f"wagon_{wagon_index}_hp"]
    wagon_type = WAGON_INFO[wagon_index]["type"]

    if hp <= 0:
        return 0

    # Правило для платформы
    if wagon_type == "platform":
        # Вместимость = HP (3, 2, или 1)
        return hp
    # Правило для полувагонов и контейнеров
    else:
        if hp == 3:
            return 6
        elif hp == 2:
            return 4
        elif hp == 1:
            return 2
    return 0  # На случай непредвиденных обстоятельств

def check_capacity_for_contract(contract):
    """
    Проверяет, хватит ли места в СОВМЕСТИМЫХ вагонах для загрузки контракта,
    используя надежный метод симуляции.
    """
    goods_to_load = []
    for g, q in [(contract["goods_1"], contract["qty_1"]), (contract["goods_2"], contract["qty_2"]),
                 (contract["goods_3"], contract["qty_3"])]:
        if g and q:
            goods_to_load.extend([g] * q)

    available_space = {i: get_current_capacity(i) - len(st.session_state[f"wagon_{i}_contents"])
                       for i in range(1, 6) if st.session_state[f"wagon_{i}_is_purchased"]}

    gondola_type = {i: st.session_state[f"wagon_{i}_contents"][0]['good']
                    for i in available_space if
                    WAGON_INFO[i]["type"] == "gondola" and st.session_state[f"wagon_{i}_contents"]}

    for good in goods_to_load:
        found_slot = False
        compatible_wagon_type = GOOD_COMPATIBILITY[good]

        for i in sorted(available_space.keys()):
            # САМАЯ ГЛАВНАЯ ПРОВЕРКА: Тип вагона должен соответствовать товару
            if WAGON_INFO[i]["type"] == compatible_wagon_type and available_space[i] > 0:
                if compatible_wagon_type == "gondola":
                    if i in gondola_type and gondola_type[i] != good:
                        continue
                    if i not in gondola_type:
                        gondola_type[i] = good

                available_space[i] -= 1
                found_slot = True
                break

        if not found_slot:
            return False
    return True


def load_contract(contract):
    """Загружает товары из контракта в СОВМЕСТИМЫЕ вагоны, соблюдая правила."""
    goods_to_load = []
    for g, q in [(contract["goods_1"], contract["qty_1"]), (contract["goods_2"], contract["qty_2"]),
                 (contract["goods_3"], contract["qty_3"])]:
        if g and q:
            goods_to_load.extend([{"good": g, "contract_id": contract['id']}] * q)

    for good_item in goods_to_load:
        compatible_wagon_type = GOOD_COMPATIBILITY[good_item['good']]

        for i in range(1, 6):
            if not st.session_state[f"wagon_{i}_is_purchased"]:
                continue

            # САМАЯ ГЛАВНАЯ ПРОВЕРКА: Тип вагона должен соответствовать товару
            if WAGON_INFO[i]["type"] == compatible_wagon_type:
                contents_key = f"wagon_{i}_contents"
                wagon_capacity = get_current_capacity(i)

                if len(st.session_state[contents_key]) < wagon_capacity:
                    if compatible_wagon_type == "gondola" and st.session_state[contents_key]:
                        if st.session_state[contents_key][0]['good'] != good_item['good']:
                            continue

                    st.session_state[contents_key].append(good_item)
                    break


def unload_contract(contract):
    """Выгружает товары контракта из всех вагонов."""
    for i in range(1, 6):
        if st.session_state[f"wagon_{i}_is_purchased"]:
            contents_key = f"wagon_{i}_contents"
            # Фильтруем список, оставляя только товары от других контрактов
            st.session_state[contents_key] = [item for item in st.session_state[contents_key] if
                                              item['contract_id'] != contract['id']]


def apply_event_effect(event):
    """
    Применяет игровой эффект от вытянутого события и проверяет все условия проигрыша
    или уничтожения вагонов.
    """
    event_id = event['id']

    # --- Нештатные события ---
    if event_id in ["E01", "E11"]:  # Поломка локомотива
        if st.session_state.loco_hp > 0:
            st.session_state.loco_hp -= 1
            st.toast("Событие: Локомотив получил повреждения!", icon="💥")
            # Проверка на фатальную поломку
            if st.session_state.loco_hp <= 0:
                st.session_state.game_over = True
                st.session_state.game_over_reason = "Локомотив полностью сломан в результате нештатной ситуации!"

    elif event_id in ["E02", "E10"]:  # Текущий ремонт
        st.session_state.loco_hp = min(3, st.session_state.loco_hp + 1)
        for i in range(1, 6):
            if st.session_state[f"wagon_{i}_is_purchased"]:
                hp_key = f"wagon_{i}_hp"
                st.session_state[hp_key] = min(3, st.session_state[hp_key] + 1)

    elif event_id in ["E03", "E09"]:  # Поломка пути
        st.session_state.time = max(0, st.session_state.time - 1)
        st.session_state.money -= 500

    elif event_id == "E05":  # Обвал тоннеля
        st.session_state.money -= 1000


    elif event_id == "E06":  # Потеря груза
        st.session_state.modifiers["revenue_multiplier"] = 0.5  # 0.5 означает 50% прибыли
        st.toast("Событие: Потеря груза! Вся прибыль от разгрузки в этом раунде снижена на 50%.", icon="📉")

    elif event_id == "E07":  # Капитальный ремонт
        st.session_state.loco_hp = 3
        for i in range(1, 6):
            if st.session_state[f"wagon_{i}_is_purchased"]:
                st.session_state[f"wagon_{i}_hp"] = 3

    elif event_id == "E08":  # Инновация
        st.session_state.modifiers["repair_cost_multiplier"] = 0.5

    elif event_id == "E12":  # Дерево на пути
        st.session_state.money -= 800

    # --- Погодные события ---
    elif event_id in ["P01", "P07", "P10"]:  # Дождь
        st.session_state.time = max(0, st.session_state.time - 2)

    elif event_id in ["P02", "P09"]:  # Снегопад
        st.session_state.time = max(0, st.session_state.time - 1)
        st.toast("Событие: Снегопад! Возможны дополнительные повреждения.", icon="❄️")

        # Проверка локомотива
        if random.randint(1, 6) == 1 and st.session_state.loco_hp > 0:
            st.session_state.loco_hp -= 1
            st.toast("Локомотив поврежден снегопадом!", icon="💥")
            if st.session_state.loco_hp <= 0:
                st.session_state.game_over = True
                st.session_state.game_over_reason = "Локомотив полностью сломан из-за плохих погодных условий!"

        # Проверка каждого вагона
        for i in range(1, 6):
            if st.session_state[f"wagon_{i}_is_purchased"] and st.session_state[f"wagon_{i}_hp"] > 0:
                if random.randint(1, 6) == 1:
                    hp_key = f"wagon_{i}_hp"
                    st.session_state[hp_key] -= 1
                    st.toast(f"{WAGON_INFO[i]['name']} поврежден снегопадом!", icon="🔧")
                    # Если вагон сломался полностью
                    if st.session_state[hp_key] <= 0:
                        st.session_state[f"wagon_{i}_is_purchased"] = False
                        st.session_state[f"wagon_{i}_contents"] = []
                        st.error(f"{WAGON_INFO[i]['name']} полностью сломан и отцеплен! Весь груз в нем утерян.")

    elif event_id in ["P03", "P08"]:  # Туман
        st.session_state.time = max(0, st.session_state.time - 1)

    elif event_id == "P06":  # Гололёд
        st.session_state.modifiers["load_unload_time_cost"] = 2

    # --- Человеческий фактор ---
    elif event_id == "H01":  # Болезнь машиниста
        st.session_state.modifiers["move_time_cost"] = 4

    elif event_id == "H02":  # Болезнь составителя
        st.session_state.modifiers["load_unload_time_cost"] = 2

    elif event_id in ["H03", "H04"]:  # Болезнь логиста
        st.session_state.modifiers["can_take_contracts"] = False

    elif event_id == "H05":  # Премия
        st.session_state.money += 1000

    elif event_id == "H06":  # Машинист 1-ого класса
        st.session_state.modifiers["move_time_cost"] = 0

    elif event_id == "H08":  # Увольнение машиниста
        st.session_state.money -= 500

    # --- ФИНАЛЬНАЯ ПРОВЕРКА НА БАНКРОТСТВО ПОСЛЕ ВСЕХ ОПЕРАЦИЙ ---
    if st.session_state.money < 0:
        st.session_state.game_over = True
        st.session_state.game_over_reason = f"Вы обанкротились в результате события «{event['name']}»!"


# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ ---
if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.time = 10
    st.session_state.money = 0
    st.session_state.credit = 0
    st.session_state.station = "A"
    st.session_state.loco_hp = 3

    # Инициализация вагонов
    for i in range(1, 6):
        st.session_state[f"wagon_{i}_is_purchased"] = i <= 2  # Первые два куплены
        st.session_state[f"wagon_{i}_hp"] = 3 if i <= 2 else 0
        st.session_state[f"wagon_{i}_contents"] = []

    # Инициализация контрактов
    st.session_state.contracts_pool = deepcopy(CONTRACTS)
    st.session_state.active_contracts = []
    st.session_state.completed_contracts = []

    st.session_state.moves_made_this_round = 0

    st.session_state.events_pool = deepcopy(EVENTS)
    st.session_state.current_event = None
    # Модификаторы, которые события могут изменять в течение раунда
    st.session_state.modifiers = {
        "repair_cost_multiplier": 1.0,
        "move_time_cost": 2,
        "load_unload_time_cost": 1,
        "can_take_contracts": True,
        "revenue_multiplier": 1.0,  # 1.0 означает 100% прибыли
    }

    st.session_state.game_over = False
    st.session_state.game_over_reason = ""

# --- Отрисовка UI ---
# st.set_page_config(layout="wide")
st.title("Железные дороги России")

if st.session_state.game_over:
    st.error(f"**ИГРА ОКОНЧЕНА!**\n\nПричина: {st.session_state.game_over_reason}")

    # --- НОВАЯ КНОПКА ---
    if st.button("Начать новую игру"):
        start_new_game()  # Вызываем нашу новую функцию для сброса

    # Останавливаем отрисовку остальной части страницы
    st.stop()

cols = st.columns(4)
cols[0].markdown(f"**Раунд:** {st.session_state.round}")
cols[1].markdown(f"**Время:** {st.session_state.time}")
cols[2].markdown(f"**Деньги:** {st.session_state.money} ₽")
cols[3].markdown(f"**Кредит:** {st.session_state.credit} ₽")
st.write(f"**Станция:** {st.session_state.station}")
if st.session_state.current_event:
    event = st.session_state.current_event
    # Используем контейнер с рамкой для лучшей визуальной организации
    with st.container(border=True):
        # Отображаем название события как заголовок
        st.markdown(f"#### Событие раунда: **{event['name']}**")
        # Отображаем описание как поясняющий текст под ним
        st.caption(f"Описание: {event['description']}")
st.markdown("---")

# --- Таблица "Состав поезда" ---
header_cols = st.columns([2, 1, 3, 2])
header_cols[0].markdown("**Состав**")
header_cols[1].markdown("**Здоровье**")
header_cols[2].markdown("**Заполненность**")
header_cols[3].markdown("**Действие**")

# Локомотив
loco_cols = st.columns([2, 1, 3, 2])
loco_cols[0].markdown("Локомотив")
loco_cols[1].markdown(
    f'<span style="color:red; font-size:20px;">{"♥" * st.session_state.loco_hp}</span><span style="color:lightgrey; font-size:20px;">{"♥" * (3 - st.session_state.loco_hp)}</span>',
    unsafe_allow_html=True)
repair_cost = int(REPAIR_LOCO * st.session_state.modifiers['repair_cost_multiplier'])
st.markdown("<hr style='margin:0.2rem 0'>", unsafe_allow_html=True)

# Вагоны в цикле
for i in range(1, 6):
    is_purchased_key = f"wagon_{i}_is_purchased"
    hp_key = f"wagon_{i}_hp"
    contents_key = f"wagon_{i}_contents"
    row_cols = st.columns([2, 1, 3, 2])
    if st.session_state[is_purchased_key]:
        wagon_capacity = get_current_capacity(i)
        if WAGON_INFO[i]['type'] != 'platform':
            fill_html = get_wagon_fill_html(st.session_state[contents_key], wagon_capacity)
        else:
            fill_html = get_platform_fill_html(st.session_state[contents_key], wagon_capacity)
        row_cols[0].markdown(WAGON_INFO[i]["name"])
        row_cols[1].markdown(
            f'<span style="color:red; font-size:20px;">{"♥" * st.session_state[hp_key]}</span><span style="color:lightgrey; font-size:20px;">{"♥" * (3 - st.session_state[hp_key])}</span>',
            unsafe_allow_html=True)
        row_cols[2].markdown(fill_html, unsafe_allow_html=True)
    else:
        row_cols[0].markdown(f"<span style='color:grey;'>{WAGON_INFO[i]['name']}</span>", unsafe_allow_html=True)
        row_cols[1].markdown("<span style='color:grey;'>-</span>", unsafe_allow_html=True)
        row_cols[2].markdown("<span style='color:grey;'>Не куплен</span>", unsafe_allow_html=True)
        if row_cols[3].button(f"Купить ({WAGON_PRICES[i]}₽)", key=f"buy_wagon_{i}"):
            if st.session_state.money >= WAGON_PRICES[i]:
                st.session_state.money -= WAGON_PRICES[i]
                st.session_state[is_purchased_key] = True
                st.session_state[
                    hp_key] = 3;
                st.rerun()
            else:
                st.error("Недостаточно денег!")
    st.markdown("<hr style='margin:0.1rem 0'>", unsafe_allow_html=True)

st.markdown("---")

# Этот блок виден только в начале раунда, до первого переезда.
if st.session_state.moves_made_this_round == 0:
    with st.container(border=True):
        st.subheader("Предрейсовое обслуживание (Депо)")

        # --- Ремонт Локомотива ---
        if 0 < st.session_state.loco_hp < 3:
            loco_repair_cost = int(REPAIR_LOCO * st.session_state.modifiers['repair_cost_multiplier'])
            # Используем колонки для красивого расположения
            cols = st.columns([3, 2])
            cols[0].markdown("**Локомотив** нуждается в ремонте.")
            if cols[1].button(f"Ремонт ({loco_repair_cost}₽)", key="depot_repair_loco"):
                if st.session_state.money >= loco_repair_cost:
                    st.session_state.money -= loco_repair_cost
                    st.session_state.loco_hp = 3
                    st.rerun()
                else:
                    st.error("Недостаточно денег!")

        # --- Ремонт Вагонов ---
        st.markdown("---")  # Разделитель
        for i in range(1, 6):
            # Проверяем каждый купленный и поврежденный вагон
            if st.session_state[f"wagon_{i}_is_purchased"] and (0 < st.session_state[f"wagon_{i}_hp"] < 3):
                wagon_repair_cost = int(REPAIR_WAGON * st.session_state.modifiers['repair_cost_multiplier'])
                cols = st.columns([3, 2])
                cols[0].markdown(f"**{WAGON_INFO[i]['name']}** нуждается в ремонте.")
                if cols[1].button(f"Ремонт ({wagon_repair_cost}₽)", key=f"depot_repair_wagon_{i}"):
                    if st.session_state.money >= wagon_repair_cost:
                        st.session_state.money -= wagon_repair_cost
                        st.session_state[f"wagon_{i}_hp"] = 3
                        st.rerun()
                    else:
                        st.error("Недостаточно денег!")

# --- Блок взятия контрактов ---
if st.session_state.moves_made_this_round == 0:
    st.subheader("Взять новый контракт")
    if len(st.session_state.active_contracts) >= 4:
        st.warning("Вы не можете взять больше 4 контрактов одновременно.")
    else:
        contract_cols = st.columns(3)
        # Определяем доступные контракты для каждого типа
        simple_contracts = [c for c in st.session_state.contracts_pool if c['id'].startswith('P')]
        medium_contracts = [c for c in st.session_state.contracts_pool if c['id'].startswith('M')]
        hard_contracts = [c for c in st.session_state.contracts_pool if c['id'].startswith('S')]


        def take_contract(contract_list):
            if contract_list:
                chosen_contract = random.choice(contract_list)
                chosen_contract['is_loaded'] = False  # Новый флаг статуса
                chosen_contract['rounds_left'] = chosen_contract['max_rounds']
                st.session_state.active_contracts.append(chosen_contract)
                st.session_state.contracts_pool.remove(chosen_contract)
                st.rerun()


        with contract_cols[0]:
            if st.button(f"Простой ({len(simple_contracts)} шт.)", disabled=not st.session_state.modifiers['can_take_contracts']):
                take_contract(simple_contracts)
        with contract_cols[1]:
            if st.button(f"Средний ({len(medium_contracts)} шт.)", disabled=not st.session_state.modifiers['can_take_contracts']):
                take_contract(medium_contracts)
        with contract_cols[2]:
            if st.button(f"Сложный ({len(hard_contracts)} шт.)", disabled=not st.session_state.modifiers['can_take_contracts']):
                take_contract(hard_contracts)

st.markdown("---")

# --- Таблица "Активные контракты" ---
st.subheader("Активные контракты")
if not st.session_state.active_contracts:
    st.info("У вас нет активных контрактов.")
else:
    # Заголовок
    act_header = st.columns([1, 2, 3, 1, 2])
    act_header[0].markdown("**ID**")
    act_header[1].markdown("**Маршрут**")
    act_header[2].markdown("**Товары**")
    act_header[3].markdown("**Срок**")
    act_header[4].markdown("**Действие**")

    # Копируем список для безопасной итерации при удалении
    for contract in st.session_state.active_contracts[:]:
        act_cols = st.columns([1, 2, 3, 1, 2])
        goods_str = f"{contract['goods_1']}×{contract['qty_1']}"
        if contract['goods_2']: goods_str += f", {contract['goods_2']}×{contract['qty_2']}"
        if contract['goods_3']: goods_str += f", {contract['goods_3']}×{contract['qty_3']}"

        status_color = "lightgreen" if contract.get('is_loaded') else "orange"

        act_cols[0].markdown(f"**{contract['id']}**")
        act_cols[1].markdown(
            f"{contract['origin']} → {contract['destination']} <span style='color:{status_color};'>●</span>",
            unsafe_allow_html=True)
        act_cols[2].markdown(f"{goods_str} ({calculate_current_price(contract)}₽)")
        act_cols[3].markdown(f"{contract['rounds_left']}")

        with act_cols[4]:
            # Логика кнопок Погрузка/Разгрузка
            # Определяем, запрещена ли погрузка на текущей станции в конце раунда
            loading_forbidden = (st.session_state.station == 'A' and st.session_state.moves_made_this_round >= 2)

            # Логика кнопки "Погрузка"
            # Она появляется, только если:
            # 1. Контракт не загружен.
            # 2. Поезд на станции отправления.
            # 3. Погрузка НЕ запрещена в конце раунда.
            if not contract['is_loaded'] and st.session_state.station == contract['origin'] and not loading_forbidden:
                if st.button("Погрузка", key=f"load_{contract['id']}"):
                    if check_capacity_for_contract(contract):
                        load_contract(contract)
                        contract['is_loaded'] = True
                        st.session_state.time = max(0, st.session_state.time - st.session_state.modifiers[
                            'load_unload_time_cost'])
                        st.rerun()
                    else:
                        st.error("Недостаточно места в вагонах!")

            # Логика кнопки "Разгрузка"
            if contract['is_loaded'] and st.session_state.station == contract['destination']:
                if st.button("Разгрузка", key=f"unload_{contract['id']}"):
                    unload_contract(contract)
                    # Рассчитываем итоговую прибыль с учетом модификатора
                    current_price = calculate_current_price(contract)
                    revenue = int(current_price * st.session_state.modifiers["revenue_multiplier"])
                    st.session_state.money += revenue
                    st.session_state.completed_contracts.append(contract)
                    st.session_state.active_contracts.remove(contract)
                    st.session_state.time = max(0, st.session_state.time - st.session_state.modifiers[
                        'load_unload_time_cost'])
                    st.rerun()
        st.markdown("<hr style='margin:0.2rem 0'>", unsafe_allow_html=True)

st.markdown("---")
# --- Основные действия по игре ---
st.subheader("Действия")
main_action_cols = st.columns(3)
if main_action_cols[0].button("Двигаться на другую станцию", disabled=(st.session_state.moves_made_this_round >= 2)):
    st.session_state.station = "A" if st.session_state.station == "B" else "B"
    st.session_state.time = max(0, st.session_state.time - st.session_state.modifiers['move_time_cost'])
    # Устанавливаем флаг, чтобы запретить повторное движение в этом раунде
    st.session_state.moves_made_this_round += 1

    st.rerun()

if main_action_cols[1].button("Взять кредит (3000₽, вернуть 4000₽)"):
    if st.session_state.credit == 0:
        st.session_state.money += CREDIT_GIVE
        st.session_state.credit = CREDIT_GIVE
        # Тут можно добавить логику возврата
    else:
        st.warning("У вас уже есть активный кредит.")

if main_action_cols[2].button("Конец раунда (следующий)",
                               disabled=(st.session_state.station != 'A'),
                               help="Завершить раунд можно только на станции А."):
    st.session_state.round += 1
    st.session_state.time = 10
    st.session_state.moves_made_this_round = 0

    if st.session_state.time <= 0 and st.session_state.station == "B":
        st.session_state.game_over = True
        st.session_state.game_over_reason = "Время истекло, а поезд не вернулся на базу (Станция А)."
        st.rerun()  # Немедленно перезапускаем, чтобы показать экран проигрыша

    # 1. Сброс всех временных модификаторов
    st.session_state.modifiers = {
        "repair_cost_multiplier": 1.0,
        "move_time_cost": 2,
        "load_unload_time_cost": 1,
        "can_take_contracts": True,
        "revenue_multiplier": 1.0,  # 1.0 означает 100% прибыли
    }

    # 2. Проверяем, не закончились ли события в "колоде".
    if not st.session_state.events_pool:
        # Если да, "перемешиваем колоду" - создаем ее заново из мастер-листа.
        st.session_state.events_pool = deepcopy(EVENTS)
        st.toast("Все события закончились. Колода перемешана!")

    # 3. Вытягиваем случайное событие, ИЗЫМАЯ его из пула.
    # Это гарантирует, что оно не повторится до "перемешивания".
    event_index = random.randrange(len(st.session_state.events_pool))
    new_event = st.session_state.events_pool.pop(event_index)
    st.session_state.current_event = new_event

    # 4. Применяем эффект вытянутого события
    apply_event_effect(new_event)

    # 5. Обновляем сроки по контрактам
    for c in st.session_state.active_contracts:
        c['rounds_left'] -= 1

        # 6. Стандартный износ в конце раунда (для всего состава)
        st.toast("Состав проходит проверку износа...")

        # Сначала проверяем локомотив
        if random.randint(1, 6) == 1 and st.session_state.loco_hp > 0:
            st.session_state.loco_hp -= 1
            st.toast(f"Локомотив получил повреждения от износа!", icon="💥")
            if st.session_state.loco_hp <= 0:
                st.session_state.game_over = True
                st.session_state.game_over_reason = "Локомотив полностью сломан в результате износа!"
                st.rerun()  # Немедленно заканчиваем игру

        # Затем проверяем КАЖДЫЙ купленный вагон
        for i in range(1, 6):
            # Проверяем только те вагоны, которые куплены и еще не сломаны
            if st.session_state[f"wagon_{i}_is_purchased"] and st.session_state[f"wagon_{i}_hp"] > 0:
                # У каждого вагона свой, независимый шанс сломаться
                if random.randint(1, 6) == 1:
                    hp_key = f"wagon_{i}_hp"
                    st.session_state[hp_key] -= 1
                    st.toast(f"{WAGON_INFO[i]['name']} получил повреждения от износа!", icon="🔧")

                    # Если вагон сломался полностью в результате износа
                    if st.session_state[hp_key] <= 0:
                        st.session_state[f"wagon_{i}_is_purchased"] = False
                        # Важно: теряем весь груз, который был в этом вагоне!
                        st.session_state[f"wagon_{i}_contents"] = []
                        st.error(f"{WAGON_INFO[i]['name']} полностью сломан и отцеплен! Весь груз в нем утерян.")

    st.rerun()
