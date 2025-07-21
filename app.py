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
def contract_price(contract):
    s = 0
    for g, q in [(contract["goods_1"], contract["qty_1"]), (contract["goods_2"], contract["qty_2"]),
                 (contract["goods_3"], contract["qty_3"])]:
        if g and q: s += GOODS_PRICES[g] * q
    return s


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

    available_space = {i: WAGON_INFO[i]["capacity"] - len(st.session_state[f"wagon_{i}_contents"])
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
                wagon_capacity = WAGON_INFO[i]["capacity"]

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

# --- Отрисовка UI ---
# st.set_page_config(layout="wide")
st.title("Железные дороги России")

cols = st.columns(4)
cols[0].markdown(f"**Раунд:** {st.session_state.round}")
cols[1].markdown(f"**Время:** {st.session_state.time}")
cols[2].markdown(f"**Деньги:** {st.session_state.money} ₽")
cols[3].markdown(f"**Кредит:** {st.session_state.credit} ₽")
st.write(f"**Станция:** {st.session_state.station}")
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
if st.session_state.loco_hp < 3:
    if loco_cols[3].button(f"Ремонт ({REPAIR_LOCO}₽)", key="repair_loco"):
        if st.session_state.money >= REPAIR_LOCO:
            st.session_state.money -= REPAIR_LOCO
            st.session_state.loco_hp = 3
            st.rerun()
        else:
            st.error("Недостаточно денег!")
st.markdown("<hr style='margin:0.2rem 0'>", unsafe_allow_html=True)

# Вагоны в цикле
for i in range(1, 6):
    is_purchased_key = f"wagon_{i}_is_purchased"
    hp_key = f"wagon_{i}_hp"
    contents_key = f"wagon_{i}_contents"
    row_cols = st.columns([2, 1, 3, 2])
    if st.session_state[is_purchased_key]:
        wagon_capacity = WAGON_INFO[i]["capacity"]
        if WAGON_INFO[i]['type'] != 'platform':
            fill_html = get_wagon_fill_html(st.session_state[contents_key], wagon_capacity)
        else:
            fill_html = get_platform_fill_html(st.session_state[contents_key], wagon_capacity)
        row_cols[0].markdown(WAGON_INFO[i]["name"])
        row_cols[1].markdown(
            f'<span style="color:red; font-size:20px;">{"♥" * st.session_state[hp_key]}</span><span style="color:lightgrey; font-size:20px;">{"♥" * (3 - st.session_state[hp_key])}</span>',
            unsafe_allow_html=True)
        row_cols[2].markdown(fill_html, unsafe_allow_html=True)
        if st.session_state[hp_key] < 3:
            if row_cols[3].button(f"Ремонт ({REPAIR_WAGON}₽)", key=f"repair_wagon_{i}"):
                if st.session_state.money >= REPAIR_WAGON:
                    st.session_state.money -= REPAIR_WAGON;
                    st.session_state[hp_key] = 3;
                    st.rerun()
                else:
                    st.error("Недостаточно денег!")
    else:
        row_cols[0].markdown(f"<span style='color:grey;'>{WAGON_INFO[i]['name']}</span>", unsafe_allow_html=True)
        row_cols[1].markdown("<span style='color:grey;'>-</span>", unsafe_allow_html=True)
        row_cols[2].markdown("<span style='color:grey;'>Не куплен</span>", unsafe_allow_html=True)
        if row_cols[3].button(f"Купить ({WAGON_PRICES[i]}₽)", key=f"buy_wagon_{i}"):
            if st.session_state.money >= WAGON_PRICES[i]:
                st.session_state.money -= WAGON_PRICES[i];
                st.session_state[is_purchased_key] = True;
                st.session_state[
                    hp_key] = 3;
                st.rerun()
            else:
                st.error("Недостаточно денег!")
    st.markdown("<hr style='margin:0.1rem 0'>", unsafe_allow_html=True)

st.markdown("---")

# --- Блок взятия контрактов ---
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
        if st.button(f"Простой ({len(simple_contracts)} шт.)", disabled=not simple_contracts):
            take_contract(simple_contracts)
    with contract_cols[1]:
        if st.button(f"Средний ({len(medium_contracts)} шт.)", disabled=not medium_contracts):
            take_contract(medium_contracts)
    with contract_cols[2]:
        if st.button(f"Сложный ({len(hard_contracts)} шт.)", disabled=not hard_contracts):
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
        act_cols[2].markdown(f"{goods_str} ({contract_price(contract)}₽)")
        act_cols[3].markdown(f"{contract['rounds_left']}")

        with act_cols[4]:
            # Логика кнопок Погрузка/Разгрузка
            if not contract['is_loaded'] and st.session_state.station == contract['origin']:
                if st.button("Погрузка", key=f"load_{contract['id']}"):
                    if check_capacity_for_contract(contract):
                        load_contract(contract)
                        contract['is_loaded'] = True
                        st.session_state.time = max(0, st.session_state.time - 1)
                        st.rerun()
                    else:
                        st.error("Недостаточно места в вагонах!")

            if contract['is_loaded'] and st.session_state.station == contract['destination']:
                if st.button("Разгрузка", key=f"unload_{contract['id']}"):
                    unload_contract(contract)
                    st.session_state.money += contract_price(contract)
                    st.session_state.completed_contracts.append(contract)
                    st.session_state.active_contracts.remove(contract)
                    st.session_state.time = max(0, st.session_state.time - 1)
                    st.rerun()
        st.markdown("<hr style='margin:0.2rem 0'>", unsafe_allow_html=True)

st.markdown("---")
# --- Основные действия по игре ---
st.subheader("Действия")
main_action_cols = st.columns(3)
if main_action_cols[0].button("Двигаться на другую станцию", disabled=(st.session_state.moves_made_this_round >= 2)):
    st.session_state.station = "A" if st.session_state.station == "B" else "B"
    st.session_state.time = max(0, st.session_state.time - 2)

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

if main_action_cols[2].button("Конец раунда (следующий)"):
    st.session_state.round += 1
    st.session_state.time = 10
    st.session_state.moves_made_this_round = 0
    # Списание сроков контрактов
    for c in st.session_state.active_contracts:
        c['rounds_left'] -= 1
    # Случайная поломка локомотива
    if random.randint(1, 6) == 1 and st.session_state.loco_hp > 0:
        st.session_state.loco_hp -= 1
    st.rerun()
