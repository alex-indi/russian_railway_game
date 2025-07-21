# app.py (Новая, 3-колоночная версия)
import streamlit as st
from config import *  # Импортируем все данные и параметры
import game_engine as ge  # Импортируем наш игровой движок


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ UI ---
def get_wagon_fill_html(contents, capacity):
    html = ''
    for i in range(capacity):
        html += GOODS_HTML.get(contents[i]['good'] if i < len(contents) else None, GOODS_HTML[None])
    return html


def get_platform_fill_html(contents, capacity):
    html = ''
    for i in range(capacity):
        html += PLATFORM_FULL if i < len(contents) else PLATFORM_EMPTY
    return html


# --- ИНИЦИАЛИЗАЦИЯ ИГРЫ ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = ge.initialize_state()

# --- ОСНОВНОЙ КОД ОТРИСОВКИ ИНТЕРФЕЙСА ---
st.set_page_config(layout="wide")
st.title("Железные дороги России")

# Блок "Игра окончена"
if st.session_state.game_state['game_over']:
    st.error(f"**ИГРА ОКОНЧЕНА!**\n\nПричина: {st.session_state.game_state['game_over_reason']}")
    if st.button("Начать новую игру"):
        st.session_state.game_state = ge.initialize_state();
        st.rerun()
    st.stop()

state = st.session_state.game_state

# --- ВЕРХНЯЯ ИНФОРМАЦИОННАЯ ПАНЕЛЬ ---
cols = st.columns([2, 2, 2, 3, 1])
# Задаем стиль в одной переменной для удобства
font_style = "font-size: 18px; font-weight: bold;" # Можете изменить 18px на 20px, 22px и т.д.

# Применяем стиль к каждому элементу
cols[0].markdown(f'<div style="{font_style}">Раунд: {state["round"]}</div>', unsafe_allow_html=True)
cols[1].markdown(f'<div style="{font_style}">Время: {state["time"]}</div>', unsafe_allow_html=True)
cols[2].markdown(f'<div style="{font_style}">Деньги: {state["money"]} ₽</div>', unsafe_allow_html=True)
cols[3].markdown(f'<div style="{font_style}">Станция: {state["station"]}</div>', unsafe_allow_html=True)
if cols[4].button("Новая игра", type="secondary"): st.session_state.confirm_restart = True

if st.session_state.get("confirm_restart", False):
    st.warning("**Вы уверены, что хотите начать новую игру?**")
    c1, c2 = st.columns(2)
    if c1.button("Да, начать заново", type="primary"):
        st.session_state.game_state = ge.initialize_state();
        st.session_state.confirm_restart = False;
        st.rerun()
    if c2.button("Нет, отмена"):
        st.session_state.confirm_restart = False;
        st.rerun()

# Отображение события раунда
if state['current_event']:
    with st.container(border=True):
        st.markdown(f"**Событие раунда: {state['current_event']['name']}** — *{state['current_event']['description']}*")
st.markdown("---")

# --- ОСНОВНЫЕ КОЛОНКИ ИНТЕРФЕЙСА ---
col1, col2, col3 = st.columns([3, 3, 2])  # 3 части под поезд, 3 под контракты, 2 под действия

with col1:
    # --- ЛЕВАЯ КОЛОНКА: ПОЕЗД И ОБСЛУЖИВАНИЕ ---
    st.markdown("#### Состав поезда")
    header_cols = st.columns([2, 1, 3, 2]);
    header_cols[0].markdown("**Состав**");
    header_cols[1].markdown("**Тех. состояние**");
    header_cols[2].markdown("**Заполненность**");
    header_cols[3].markdown("**Действие**")
    loco_cols = st.columns([2, 1, 3, 2]);
    loco_cols[0].markdown("Локомотив");
    loco_cols[1].markdown(
        f'<span style="color:red; font-size:20px;">{"♥ " * state["loco_hp"]}</span><span style="color:lightgrey; font-size:20px;">{"♥ " * (3 - state["loco_hp"])}</span>',
        unsafe_allow_html=True)
    st.markdown("<hr style='margin:0.1rem 0'>", unsafe_allow_html=True)
    for i in range(1, 6):
        row_cols = st.columns([2, 1, 3, 2])
        if state[f"wagon_{i}_is_purchased"]:
            capacity = ge.get_current_capacity(state, i)
            fill_html = get_platform_fill_html(state[f"wagon_{i}_contents"], capacity) if WAGON_INFO[i][
                                                                                              'type'] == 'platform' else get_wagon_fill_html(
                state[f"wagon_{i}_contents"], capacity)
            row_cols[0].markdown(WAGON_INFO[i]["name"])
            row_cols[1].markdown(
                f'<span style="color:red; font-size:20px;">{"♥ " * state[f"wagon_{i}_hp"]}</span><span style="color:lightgrey; font-size:20px;">{"♥ " * (3 - state[f"wagon_{i}_hp"])}</span>',
                unsafe_allow_html=True)
            row_cols[2].markdown(fill_html, unsafe_allow_html=True)
        else:  # Если вагон не куплен
            row_cols[0].markdown(f"<span style='color:grey;'>{WAGON_INFO[i]['name']}</span>", unsafe_allow_html=True)
            row_cols[1].markdown("<span style='color:grey;'>-</span>", unsafe_allow_html=True)
            row_cols[2].markdown("<span style='color:grey;'>Не куплен</span>", unsafe_allow_html=True)

            # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
            # Кнопка "Купить" отображается только в начале раунда на станции А ("в депо")
            if state['moves_made_this_round'] == 0 and state['station'] == 'A':
                price = WAGON_PRICES[i]
                if row_cols[3].button(f"Купить ({price}₽)", key=f"buy_wagon_{i}"):
                    if state['money'] >= price:
                        st.session_state.game_state = ge.perform_action(state, "buy_wagon", wagon_index=i)
                        st.rerun()
                    else:
                        st.error("Недостаточно денег для покупки!")
        st.markdown("<hr style='margin:0.1rem 0'>", unsafe_allow_html=True)

    st.markdown("")  # Вертикальный отступ
    # Блок обслуживания (виден только в начале раунда на станции А)
    if state['moves_made_this_round'] == 0 and state['station'] == 'A':
        with st.container(border=True):
            st.markdown("##### Предрейсовое обслуживание")
            needs_repair = False
            if 0 < state['loco_hp'] < 3:
                needs_repair = True
                cost = int(REPAIR_LOCO * state['modifiers']['repair_cost_multiplier'])
                cols = st.columns(2);
                cols[0].markdown("**Локомотив**")
                if cols[1].button(f"Ремонт ({cost}₽)", key="depot_repair_loco", use_container_width=True):
                    if state['money'] >= cost:
                        st.session_state.game_state = ge.perform_action(state, "repair_loco");
                        st.rerun()
                    else:
                        st.error("Недостаточно денег!")
            for i in range(1, 6):
                if state[f"wagon_{i}_is_purchased"] and 0 < state[f"wagon_{i}_hp"] < 3:
                    needs_repair = True
                    cost = int(REPAIR_WAGON * state['modifiers']['repair_cost_multiplier'])
                    cols = st.columns(2);
                    cols[0].markdown(f"**{WAGON_INFO[i]['name']}**")
                    if cols[1].button(f"Ремонт ({cost}₽)", key=f"depot_repair_wagon_{i}", use_container_width=True):
                        if state['money'] >= cost:
                            st.session_state.game_state = ge.perform_action(state, "repair_wagon", wagon_index=i);
                            st.rerun()
                        else:
                            st.error("Недостаточно денег!")
            if not needs_repair:
                st.info("Весь состав в отличном состоянии.")

with col2:
    # --- ЦЕНТРАЛЬНАЯ КОЛОНКА: КОНТРАКТЫ ---
    st.markdown("#### Активные контракты")
    if not state['active_contracts']:
        st.info("У вас нет активных контрактов.")
    else:
        act_header = st.columns([1, 2, 4, 1, 2]);
        act_header[0].markdown("**ID**");
        act_header[1].markdown("**Маршрут**");
        act_header[2].markdown("**Товары**");
        act_header[3].markdown("**Срок**");
        act_header[4].markdown("**Действие**")
        for contract in state['active_contracts']:
            act_cols = st.columns([1, 2, 4, 1, 2])
            goods_str = f"{contract['goods_1']}×{contract['qty_1']}";
            if contract['goods_2']: goods_str += f", {contract['goods_2']}×{contract['qty_2']}";
            if contract['goods_3']: goods_str += f", {contract['goods_3']}×{contract['qty_3']}"
            status_color = "lightgreen" if contract.get('is_loaded') else "orange"
            act_cols[0].markdown(f"**{contract['id']}**");
            act_cols[1].markdown(
                f"{contract['origin']}→{contract['destination']} <span style='color:{status_color};'>●</span>",
                unsafe_allow_html=True)
            act_cols[2].markdown(f"{goods_str} ({ge.calculate_current_price(contract)}₽)");
            act_cols[3].markdown(f"{contract['rounds_left']}")
            with act_cols[4]:
                loading_forbidden = (state['station'] == 'A' and state['moves_made_this_round'] >= 2)
                if not contract.get('is_loaded') and state['station'] == contract['origin'] and not loading_forbidden:
                    if st.button("Погрузка", key=f"load_{contract['id']}"):
                        if ge.check_capacity_for_contract(state, contract):
                            st.session_state.game_state = ge.perform_action(state, "load_contract",
                                                                            contract_id=contract['id']);
                            st.rerun()
                        else:
                            st.error("Недостаточно места!")
                if contract.get('is_loaded') and state['station'] == contract['destination']:
                    if st.button("Разгрузка", key=f"unload_{contract['id']}"):
                        st.session_state.game_state = ge.perform_action(state, "unload_contract",
                                                                        contract_id=contract['id']);
                        st.rerun()

    st.markdown("")  # Вертикальный отступ
    # Блок взятия контрактов (виден только в начале раунда)
    if state['moves_made_this_round'] == 0:
        with st.container(border=True):
            st.markdown("##### Взять новый контракт")
            if len(state['active_contracts']) >= 4:
                st.warning("Максимум 4 контракта.")
            else:
                contract_cols = st.columns(3)
                can_take = state['modifiers']['can_take_contracts']
                s_pool = [c for c in state['contracts_pool'] if c['id'].startswith('P')];
                m_pool = [c for c in state['contracts_pool'] if c['id'].startswith('M')];
                h_pool = [c for c in state['contracts_pool'] if c['id'].startswith('S')]
                if contract_cols[0].button(f"Простой ({len(s_pool)})", disabled=(not s_pool or not can_take),
                                           use_container_width=True):
                    st.session_state.game_state = ge.perform_action(state, "take_contract", ctype='P');
                    st.rerun()
                if contract_cols[1].button(f"Средний ({len(m_pool)})", disabled=(not m_pool or not can_take),
                                           use_container_width=True):
                    st.session_state.game_state = ge.perform_action(state, "take_contract", ctype='M');
                    st.rerun()
                if contract_cols[2].button(f"Сложный ({len(h_pool)})", disabled=(not h_pool or not can_take),
                                           use_container_width=True):
                    st.session_state.game_state = ge.perform_action(state, "take_contract", ctype='S');
                    st.rerun()

with col3:
    # --- ПРАВАЯ КОЛОНКА: ПАНЕЛЬ УПРАВЛЕНИЯ ---
    with st.container(border=True):
        st.markdown("##### Панель управления")
        if st.button("Двигаться", disabled=(state['moves_made_this_round'] >= 2), use_container_width=True):
            st.session_state.game_state = ge.perform_action(state, "move");
            st.rerun()
        if st.button("Конец раунда", disabled=(state['station'] != 'A'),
                     help="Завершить раунд можно только на станции А.", use_container_width=True):
            st.session_state.game_state = ge.perform_action(state, "end_round");
            st.rerun()