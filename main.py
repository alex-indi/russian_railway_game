import streamlit as st

import game_engine as ge  # Импортируем наш игровой движок

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ UI ---
# Эти функции генерируют HTML, поэтому они остаются в файле интерфейса.
GOODS_HTML = {
    "Уголь": '<span style="font-size:20px;">⬛</span>',
    "Щебень": '<span style="font-size:20px; color:#FFD700;">⬜</span>',
    "Желтый": '<span style="font-size:20px; color:#FFD700;">🟨</span>',
    "Зеленый": '<span style="font-size:20px; color:#228B22;">🟩</span>',
    "Синий": '<span style="font-size:20px; color:#0066FF;">🟦</span>',
    "Металл": '<span style="font-size:20px; color:#333;">⬜</span>',
    None: '<span style="font-size:20px; color:#ccc;">▫️</span>',
}
PLATFORM_EMPTY = '<span style="font-size:20px; color:#aaa;">⚪</span>'
PLATFORM_FULL = '<span style="font-size:20px; color:#000;">⚫</span>'


def get_wagon_fill_html(contents, capacity):
    """Генерирует HTML для отображения заполненности вагона."""
    html = ''
    for i in range(capacity):
        html += GOODS_HTML.get(contents[i]['good'] if i < len(contents) else None, GOODS_HTML[None])
    return html


def get_platform_fill_html(contents, capacity):
    """Генерирует HTML для отображения заполненности платформы."""
    html = ''
    for i in range(capacity):
        html += PLATFORM_FULL if i < len(contents) else PLATFORM_EMPTY
    return html


# --- ИНИЦИАЛИЗАЦИЯ ИГРЫ ---
# Если игрового состояния нет в сессии, создаем его с помощью движка.
if 'game_state' not in st.session_state:
    st.session_state.game_state = ge.initialize_state()

# --- ОСНОВНОЙ КОД ОТРИСОВКИ ИНТЕРФЕЙСА ---
st.set_page_config()
st.title("Железные дороги России")

# Блок "Игра окончена"
if st.session_state.game_state['game_over']:
    st.error(f"**ИГРА ОКОНЧЕНА!**\n\nПричина: {st.session_state.game_state['game_over_reason']}")
    if st.button("Начать новую игру"):
        # При старте новой игры мы просто заменяем старое состояние новым начальным.
        st.session_state.game_state = ge.initialize_state()
        st.rerun()
    st.stop()  # Останавливаем отрисовку остальной части страницы

# Создаем короткую переменную для удобства доступа к состоянию
state = st.session_state.game_state

# Отображение основной информации
cols = st.columns(4)
cols[0].markdown(f"**Раунд:** {state['round']}")
cols[1].markdown(f"**Время:** {state['time']}")
cols[2].markdown(f"**Деньги:** {state['money']} ₽")
st.write(f"**Станция:** {state['station']}")

# Отображение события раунда
if state['current_event']:
    event = state['current_event']
    with st.container(border=True):
        st.markdown(f"#### Событие раунда: **{event['name']}**")
        st.caption(f"Описание: {event['description']}")
st.markdown("---")

# Таблица "Состав поезда"
header_cols = st.columns([2, 1, 3, 2]);
header_cols[0].markdown("**Состав**");
header_cols[1].markdown("**Здоровье**");
header_cols[2].markdown("**Заполненность**");
header_cols[3].markdown("**Действие**")
loco_cols = st.columns([2, 1, 3, 2]);
loco_cols[0].markdown("Локомотив");
loco_cols[1].markdown(
    f'<span style="color:red; font-size:20px;">{"♥" * state["loco_hp"]}</span><span style="color:lightgrey; font-size:20px;">{"♥" * (3 - state["loco_hp"])}</span>',
    unsafe_allow_html=True)
st.markdown("<hr style='margin:0.1rem 0'>", unsafe_allow_html=True)

for i in range(1, 6):
    row_cols = st.columns([2, 1, 3, 2])
    if state[f"wagon_{i}_is_purchased"]:
        capacity = ge.get_current_capacity(state, i)
        fill_html = get_platform_fill_html(state[f"wagon_{i}_contents"], capacity) if ge.WAGON_INFO[i][
                                                                                          'type'] == 'platform' else get_wagon_fill_html(
            state[f"wagon_{i}_contents"], capacity)
        row_cols[0].markdown(ge.WAGON_INFO[i]["name"])
        row_cols[1].markdown(
            f'<span style="color:red; font-size:20px;">{"♥" * state[f"wagon_{i}_hp"]}</span><span style="color:lightgrey; font-size:20px;">{"♥" * (3 - state[f"wagon_{i}_hp"])}</span>',
            unsafe_allow_html=True)
        row_cols[2].markdown(fill_html, unsafe_allow_html=True)
    else:
        row_cols[0].markdown(f"<span style='color:grey;'>{ge.WAGON_INFO[i]['name']}</span>", unsafe_allow_html=True)
        row_cols[1].markdown("<span style='color:grey;'>-</span>", unsafe_allow_html=True)
        row_cols[2].markdown("<span style='color:grey;'>Не куплен</span>", unsafe_allow_html=True)
        price = ge.WAGON_PRICES[i]
        if row_cols[3].button(f"Купить ({price}₽)", key=f"buy_wagon_{i}"):
            if state['money'] >= price:
                st.session_state.game_state = ge.perform_action(state, "buy_wagon", wagon_index=i)
                st.rerun()
            else:
                st.error("Недостаточно денег для покупки!")
    st.markdown("<hr style='margin:0.1rem 0'>", unsafe_allow_html=True)
st.markdown("---")

# Блок обслуживания в Депо (виден только в начале раунда на станции А)
if state['moves_made_this_round'] == 0 and state['station'] == 'A':
    with st.container(border=True):
        st.subheader("Предрейсовое обслуживание (Депо)")

        # Ремонт локомотива
        if 0 < state['loco_hp'] < 3:
            cost = int(ge.REPAIR_LOCO * state['modifiers']['repair_cost_multiplier'])
            cols = st.columns([3, 2]);
            cols[0].markdown("**Локомотив** нуждается в ремонте.")
            if cols[1].button(f"Ремонт ({cost}₽)", key="depot_repair_loco"):
                if state['money'] >= cost:
                    st.session_state.game_state = ge.perform_action(state, "repair_loco")
                    st.rerun()
                else:
                    st.error("Недостаточно денег для ремонта!")

        # Ремонт вагонов
        st.markdown("---")
        for i in range(1, 6):
            if state[f"wagon_{i}_is_purchased"] and 0 < state[f"wagon_{i}_hp"] < 3:
                cost = int(ge.REPAIR_WAGON * state['modifiers']['repair_cost_multiplier'])
                cols = st.columns([3, 2]);
                cols[0].markdown(f"**{ge.WAGON_INFO[i]['name']}** нуждается в ремонте.")
                if cols[1].button(f"Ремонт ({cost}₽)", key=f"depot_repair_wagon_{i}"):
                    if state['money'] >= cost:
                        st.session_state.game_state = ge.perform_action(state, "repair_wagon", wagon_index=i)
                        st.rerun()
                    else:
                        st.error("Недостаточно денег!")
    st.markdown("---")

# Блок взятия контрактов (виден только в начале раунда)
if state['moves_made_this_round'] == 0:
    st.subheader("Взять новый контракт")
    if len(state['active_contracts']) >= 4:
        st.warning("Вы не можете взять больше 4 контрактов одновременно.")
    else:
        contract_cols = st.columns(3)
        can_take = state['modifiers']['can_take_contracts']
        s_pool = [c for c in state['contracts_pool'] if c['id'].startswith('P')]
        m_pool = [c for c in state['contracts_pool'] if c['id'].startswith('M')]
        h_pool = [c for c in state['contracts_pool'] if c['id'].startswith('S')]

        if contract_cols[0].button(f"Простой ({len(s_pool)} шт.)", disabled=(not s_pool or not can_take)):
            st.session_state.game_state = ge.perform_action(state, "take_contract", ctype='P')
            st.rerun()
        if contract_cols[1].button(f"Средний ({len(m_pool)} шт.)", disabled=(not m_pool or not can_take)):
            st.session_state.game_state = ge.perform_action(state, "take_contract", ctype='M')
            st.rerun()
        if contract_cols[2].button(f"Сложный ({len(h_pool)} шт.)", disabled=(not h_pool or not can_take)):
            st.session_state.game_state = ge.perform_action(state, "take_contract", ctype='S')
            st.rerun()
    st.markdown("---")

# Таблица "Активные контракты"
st.subheader("Активные контракты")
if not state['active_contracts']:
    st.info("У вас нет активных контрактов.")
else:
    act_header = st.columns([1, 2, 3, 1, 2]);
    act_header[0].markdown("**ID**");
    act_header[1].markdown("**Маршрут**");
    act_header[2].markdown("**Товары**");
    act_header[3].markdown("**Срок**");
    act_header[4].markdown("**Действие**")
    for contract in state['active_contracts']:
        act_cols = st.columns([1, 2, 3, 1, 2])
        goods_str = f"{contract['goods_1']}×{contract['qty_1']}"
        if contract['goods_2']: goods_str += f", {contract['goods_2']}×{contract['qty_2']}"
        if contract['goods_3']: goods_str += f", {contract['goods_3']}×{contract['qty_3']}"
        status_color = "lightgreen" if contract.get('is_loaded') else "orange"

        act_cols[0].markdown(f"**{contract['id']}**")
        act_cols[1].markdown(
            f"{contract['origin']} → {contract['destination']} <span style='color:{status_color};'>●</span>",
            unsafe_allow_html=True)
        act_cols[2].markdown(f"{goods_str} ({ge.calculate_current_price(contract)}₽)")
        act_cols[3].markdown(f"{contract['rounds_left']}")

        with act_cols[4]:
            loading_forbidden = (state['station'] == 'A' and state['moves_made_this_round'] >= 2)
            if not contract.get('is_loaded') and state['station'] == contract['origin'] and not loading_forbidden:
                if st.button("Погрузка", key=f"load_{contract['id']}"):
                    if ge.check_capacity_for_contract(state, contract):
                        st.session_state.game_state = ge.perform_action(state, "load_contract",
                                                                        contract_id=contract['id'])
                        st.rerun()
                    else:
                        st.error("Недостаточно места в вагонах!")

            if contract.get('is_loaded') and state['station'] == contract['destination']:
                if st.button("Разгрузка", key=f"unload_{contract['id']}"):
                    st.session_state.game_state = ge.perform_action(state, "unload_contract",
                                                                    contract_id=contract['id'])
                    st.rerun()
        st.markdown("<hr style='margin:0.2rem 0'>", unsafe_allow_html=True)
st.markdown("---")

# Основные действия по игре
st.subheader("Действия")
main_action_cols = st.columns(3)

if main_action_cols[0].button("Двигаться на другую станцию", disabled=(state['moves_made_this_round'] >= 2)):
    st.session_state.game_state = ge.perform_action(state, "move");
    st.rerun()

if main_action_cols[2].button("Конец раунда (следующий)", disabled=(state['station'] != 'A'),
                              help="Завершить раунд можно только на станции А."):
    st.session_state.game_state = ge.perform_action(state, "end_round");
    st.rerun()
