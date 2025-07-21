import random

import streamlit as st

from config import *

# --- Вспомогательные функции ---
GOODS_PRICES = {
    "Уголь": G_COAL,
    "Щебень": G_GRAVEL,
    "Желтый": G_BOX_Y,
    "Зеленый": G_BOX_G,
    "Синий": G_BOX_B,
    "Металл": G_METAL,
}


def contract_price(contract):
    s = 0
    for g, q in [
        (contract["goods_1"], contract["qty_1"]),
        (contract["goods_2"], contract["qty_2"]),
        (contract["goods_3"], contract["qty_3"])
    ]:
        if g and q:
            s += GOODS_PRICES[g] * q
    return s


def wagon_capacity(hp, cap3, cap2, cap1):
    if hp == 3:
        return cap3
    elif hp == 2:
        return cap2
    elif hp == 1:
        return cap1
    else:
        return 0


# --- Инициализация состояния ---
if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.time = 10
    st.session_state.money = 0
    st.session_state.credit = 0
    st.session_state.credit_due = 0
    st.session_state.station = "A"
    st.session_state.loco_hp = 3
    st.session_state.wagon_1_is_purchased = True
    st.session_state.wagon_1_hp = 3
    st.session_state.wagon_2_is_purchased = True
    st.session_state.wagon_2_hp = 3
    st.session_state.wagon_3_is_purchased = False
    st.session_state.wagon_3_hp = 0
    st.session_state.wagon_4_is_purchased = False
    st.session_state.wagon_4_hp = 0
    st.session_state.wagon_5_is_purchased = False
    st.session_state.wagon_5_hp = 0
    st.session_state.active_contracts = []
    st.session_state.completed_contracts = []
    st.session_state.selected_contract = None
    st.session_state.contracts_pool = list(CONTRACTS)

for i in range(1, 6):
    key = f"wagon_{i}_contents"
    if key not in st.session_state:
        st.session_state[key] = []
if "platform_contents" not in st.session_state:
    st.session_state.platform_contents = []

# --- Отрисовка состояния поезда ---
st.title("Железные дороги России")

cols = st.columns(4)
cols[0].markdown(f"**Раунд:** {st.session_state.round}")
cols[1].markdown(f"**Время:** {st.session_state.time}")
cols[2].markdown(f"**Деньги:** {st.session_state.money}")
cols[3].markdown(f"**Кредит:** {st.session_state.credit}")

st.write(f"**Станция:** {st.session_state.station}")

# st.markdown(f"**Локомотив:** {'♥ ' * st.session_state.loco_hp}{'□' * (3 - st.session_state.loco_hp)}")
# st.markdown(f"**Полувагон:** {'♥ ' * st.session_state.wagon_hp}{'□' * (3 - st.session_state.wagon_hp)}")
# st.markdown(f"**Контейнер:** {'♥ ' * st.session_state.boxcar_hp}{'□' * (3 - st.session_state.boxcar_hp)}")
# if st.session_state.have_platform:
#     st.markdown(f"**Платформа:** {'♥' * st.session_state.platform_hp}{'□' * (3 - st.session_state.platform_hp)}")
# else:
#     st.markdown("*Платформа не куплена*")

# Карта отображения грузов для HTML (можно заменить на SVG или эмодзи)
GOODS_HTML = {
    "Уголь": '<span style="font-size:20px;">⬛</span>',
    "Щебень": '<span style="font-size:20px; color:#888;">⬜</span>',
    "Желтый": '<span style="font-size:20px; color:#FFD700;">🟨</span>',
    "Зеленый": '<span style="font-size:20px; color:#228B22;">🟩</span>',
    "Синий": '<span style="font-size:20px; color:#0066FF;">🟦</span>',
    "Металл": '<span style="font-size:20px; color:#bbb;">⬜</span>',
    None: '<span style="font-size:20px; color:#ccc;">▫️</span>',
}

PLATFORM_EMPTY = '<span style="font-size:20px; color:#aaa;">⚪</span>'
PLATFORM_FULL = '<span style="font-size:20px; color:#000;">⚫</span>'


def get_wagon_fill_html(contents, hp):
    html = ''
    for i in range(hp):
        if i < len(contents):
            html += GOODS_HTML.get(contents[i], GOODS_HTML[None])
        else:
            html += GOODS_HTML[None]
    return html


def get_platform_fill_html(contents, hp):
    html = ''
    for i in range(hp):
        if i < len(contents):
            html += PLATFORM_FULL
        else:
            html += PLATFORM_EMPTY
    return html


rows = []

# Локомотив
rows.append(f"""
<tr>
    <td>Локомотив</td>
    <td><span style="color:red; font-size:20px;">{"♥" * st.session_state.loco_hp}{"□ " * (3 - st.session_state.loco_hp)}</span></td>
    <td></td>
</tr>
""")

# Полувагон 1
if st.session_state.wagon_1_is_purchased:
    rows.append(f"""
<tr>
    <td>Полувагон 1</td>
    <td><span style="color:red; font-size:20px;">{"♥" * st.session_state.wagon_1_hp}{"□" * (3 - st.session_state.wagon_1_hp)}</span></td>
    <td>{get_wagon_fill_html(st.session_state.wagon_1_contents, st.session_state.wagon_1_hp)}</td>
</tr>
    """)

# Контейнер 1
if st.session_state.wagon_2_is_purchased:
    rows.append(f"""
<tr>
    <td>Контейнер 1</td>
    <td><span style="color:red; font-size:20px;">{"♥" * st.session_state.wagon_2_hp}{"□" * (3 - st.session_state.wagon_2_hp)}</span></td>
    <td>{get_wagon_fill_html(st.session_state.wagon_2_contents, st.session_state.wagon_2_hp)}</td>
</tr>
    """)

# Полувагон 2
if st.session_state.wagon_3_is_purchased:
    rows.append(f"""
<tr>
    <td>Полувагон 2</td>
    <td><span style="color:red; font-size:20px;">{"♥" * st.session_state.wagon_3_hp}{"□" * (3 - st.session_state.wagon_3_hp)}</span></td>
    <td>{get_wagon_fill_html(st.session_state.wagon_3_contents, st.session_state.wagon_3_hp)}</td>
</tr>
    """)

# Контейнер 2
if st.session_state.wagon_4_is_purchased:
    rows.append(f"""
<tr>
    <td>Контейнер 2</td>
    <td><span style="color:red; font-size:20px;">{"♥" * st.session_state.wagon_4_hp}{"□" * (3 - st.session_state.wagon_4_hp)}</span></td>
    <td>{get_wagon_fill_html(st.session_state.wagon_4_contents, st.session_state.wagon_4_hp)}</td>
</tr>
    """)

# Платформа
if st.session_state.wagon_5_is_purchased:
    rows.append(f"""
<tr>
    <td>Платформа</td>
    <td><span style="color:red; font-size:20px;">{"♥" * st.session_state.platform_hp}{"□" * (3 - st.session_state.platform_hp)}</span></td>
    <td>{get_platform_fill_html(st.session_state.platform_contents, st.session_state.platform_hp)}</td>
</tr>""")

# Собираем финальный HTML
table_html = f"""
<table style="width:100%; border-collapse: collapse;">
<tr>
    <th style="text-align:left;">Состав</th>
    <th style="text-align:left;">Здоровье</th>
    <th style="text-align:left;">Заполненность</th>
</tr>
{''.join(rows)}
</table>
"""
st.markdown(table_html, unsafe_allow_html=True)

# --- Блок с выбором контракта ---
st.subheader("Контракты (выбрать и взять до 4 одновременно)")
available = [c for c in st.session_state.contracts_pool if
             c not in st.session_state.active_contracts and c not in st.session_state.completed_contracts]
contract_options = [
    f"{c['id']}: {c['goods_1']}×{c['qty_1']}" + (f", {c['goods_2']}×{c['qty_2']}" if c['goods_2'] else "") + (
        f", {c['goods_3']}×{c['qty_3']}" if c['goods_3'] else "") + f" ({contract_price(c)}₽)" for c in available]
contract_idx = st.selectbox("Доступные контракты", range(len(available)), format_func=lambda i: contract_options[i],
                            key="contract_choice")

if st.button("Взять контракт"):
    if len(st.session_state.active_contracts) < 4:
        st.session_state.active_contracts.append(available[contract_idx])
        st.session_state.contracts_pool.remove(available[contract_idx])

# --- Отображение активных контрактов ---
st.subheader("Активные контракты")
if st.session_state.active_contracts:
    for i, c in enumerate(st.session_state.active_contracts):
        st.markdown(f"**{c['id']}** | {c['origin']}→{c['destination']} | "
                    f"{c['goods_1']}×{c['qty_1']}"
                    + (f", {c['goods_2']}×{c['qty_2']}" if c['goods_2'] else "")
                    + (f", {c['goods_3']}×{c['qty_3']}" if c['goods_3'] else "")
                    + f" | Осталось раундов: {c.get('rounds_left', c['max_rounds'])} | Сумма: {contract_price(c)}₽")

        if st.button(f"Выполнить контракт {c['id']}", key=f"done_{i}"):
            st.session_state.completed_contracts.append(c)
            st.session_state.active_contracts.remove(c)
            st.session_state.money += contract_price(c)

# --- Действия по поезду и игре ---
st.subheader("Действия")

cols = st.columns(3)
if cols[0].button("Двигаться на другую станцию"):
    st.session_state.station = "A" if st.session_state.station == "B" else "B"
    st.session_state.time = max(0, st.session_state.time - 2)  # 2 ед. времени

if cols[1].button("Погрузка/разгрузка"):
    st.session_state.time = max(0, st.session_state.time - 1)  # 1 ед. времени

if cols[2].button("Чинить локомотив"):
    if st.session_state.money >= REPAIR_LOCO and st.session_state.loco_hp < 3:
        st.session_state.money -= REPAIR_LOCO
        st.session_state.loco_hp = 3

st.subheader("Управление вагонами")
wcol = st.columns(3)
if wcol[0].button("Чинить полувагон"):
    if st.session_state.money >= REPAIR_WAGON and st.session_state.wagon_hp < 3:
        st.session_state.money -= REPAIR_WAGON
        st.session_state.wagon_hp = 3
if wcol[1].button("Чинить контейнер"):
    if st.session_state.money >= REPAIR_WAGON and st.session_state.boxcar_hp < 3:
        st.session_state.money -= REPAIR_WAGON
        st.session_state.boxcar_hp = 3
if wcol[2].button("Купить платформу (5000₽)"):
    if not st.session_state.have_platform and st.session_state.money >= 5000:
        st.session_state.money -= 5000
        st.session_state.have_platform = True
        st.session_state.platform_hp = 3

# --- Взять кредит ---
if st.button("Взять кредит (3000₽, вернуть 4000₽)"):
    if st.session_state.credit == 0:
        st.session_state.money += CREDIT_GIVE
        st.session_state.credit = CREDIT_GIVE
        st.session_state.credit_due = CREDIT_PAY

# --- Конец раунда ---
if st.button("Конец раунда (следующий)"):
    st.session_state.round += 1
    st.session_state.time = 10
    # Списание сроков
    for c in st.session_state.active_contracts:
        c['rounds_left'] = c.get('rounds_left', c['max_rounds']) - 1
        # Обесценивание после срока
        if c['rounds_left'] < 0:
            c['depreciation'] = c.get('depreciation', 1) * 0.5

    # Случайная поломка (например 1/6 шанс) для локомотива
    if random.randint(1, 6) == 1:
        st.session_state.loco_hp = max(0, st.session_state.loco_hp - 1)

    # Обновить цену контрактов с учетом обесценивания
    for c in st.session_state.active_contracts:
        if 'depreciation' in c:
            old_price = contract_price(c)
            new_price = int(old_price * c['depreciation'])
            c['price'] = new_price

st.write("**Выполненные контракты:**")
for c in st.session_state.completed_contracts:
    st.write(f"{c['id']} ({contract_price(c)}₽)")

st.info(
    "*Базовая демо-версия. Для усложнения — добавьте события, хранение состояния вагонов, ограничения вместимости по HP, автоматизацию штрафов и проверок.*")
