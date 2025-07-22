# app.py
import streamlit as st
import config as cfg
import game_engine as ge


def get_wagon_fill_html(contents, capacity):
    """Генерирует HTML для отображения заполненности вагона."""
    html = ''
    for i in range(capacity):
        html += cfg.GOODS_HTML.get(contents[i]['good'] if i < len(contents) else None, cfg.GOODS_HTML[None])
    return html


def get_platform_fill_html(contents, capacity):
    """Генерирует HTML для отображения заполненности платформы."""
    html = ''
    for i in range(capacity):
        html += cfg.PLATFORM_FULL if i < len(contents) else cfg.PLATFORM_EMPTY
    return html


# --- ИНИЦИАЛИЗАЦИЯ ИГРЫ И НАСТРОЕК ---
if 'game_settings' not in st.session_state:
    st.session_state.game_settings = {
        'STARTING_MONEY': cfg.STARTING_MONEY, 'REPAIR_LOCO': cfg.REPAIR_LOCO,
        'REPAIR_WAGON': cfg.REPAIR_WAGON, 'GOODS_PRICES': cfg.GOODS_PRICES.copy(),
        'WAGON_PRICES': cfg.WAGON_PRICES.copy(), 'WAGON_INFO': cfg.WAGON_INFO,
        'GOOD_COMPATIBILITY': cfg.GOOD_COMPATIBILITY,
    }
if 'game_state' not in st.session_state:
    st.session_state.game_state = ge.initialize_state(st.session_state.game_settings)

# --- ОСНОВНОЙ КОД ОТРИСОВКИ ---
st.set_page_config(layout="wide")
st.title("Железные дороги России")
tab_game, tab_instruction, tab_settings = st.tabs(["🕹️ Игра", "📖 Инструкция", "⚙️ Настройки"])

# --- ВКЛАДКА "ИГРА" ---
with tab_game:
    state = st.session_state.game_state
    if state['game_over']:
        st.error(f"**ИГРА ОКОНЧЕНА!**\n\nПричина: {state['game_over_reason']}")
        if st.button("Начать новую игру (с текущими настройками)"):
            st.session_state.game_state = ge.initialize_state(st.session_state.game_settings);
            st.rerun()
        st.stop()

    # Верхняя панель (упрощена)
    cols = st.columns(4);
    cols[0].markdown(f"**Раунд:** {state['round']}");
    cols[1].markdown(f"**Время:** {state['time']}");
    cols[2].markdown(f"**Деньги:** {state['money']} ₽");
    cols[3].markdown(f"**Станция:** {state['station']}")
    if state['current_event']:
        with st.container(border=True): st.markdown(
            f"**Событие раунда: {state['current_event']['name']}** — *{state['current_event']['description']}*")
    st.markdown("---")

    col1, col2, col3 = st.columns([3, 3, 2])
    with col1:  # КОЛОНКА ПОЕЗДА И РЕМОНТА
        st.markdown("#### Состав поезда")
        # ... (Код отрисовки состава поезда, без изменений) ...
        header_cols = st.columns([2, 1, 3, 2]);
        header_cols[0].markdown("**Состав**");
        header_cols[1].markdown("**Здоровье**");
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
            wagon_info = state['settings']['WAGON_INFO'][i]
            if state[f"wagon_{i}_is_purchased"]:
                capacity = ge.get_current_capacity(state, i)
                fill_html = get_platform_fill_html(state[f"wagon_{i}_contents"], capacity) if wagon_info[
                                                                                                  'type'] == 'platform' else get_wagon_fill_html(
                    state[f"wagon_{i}_contents"], capacity)
                row_cols[0].markdown(wagon_info["name"]);
                row_cols[1].markdown(
                    f'<span style="color:red; font-size:20px;">{"♥ " * state[f"wagon_{i}_hp"]}</span><span style="color:lightgrey; font-size:20px;">{"♥ " * (3 - state[f"wagon_{i}_hp"])}</span>',
                    unsafe_allow_html=True);
                row_cols[2].markdown(fill_html, unsafe_allow_html=True)
            else:
                row_cols[0].markdown(f"<span style='color:grey;'>{wagon_info['name']}</span>", unsafe_allow_html=True);
                row_cols[1].markdown("<span style='color:grey;'>-</span>", unsafe_allow_html=True);
                row_cols[2].markdown("<span style='color:grey;'>Не куплен</span>", unsafe_allow_html=True)
                if state['moves_made_this_round'] == 0 and state['station'] == 'A':
                    price = state['settings']['WAGON_PRICES'][i]
                    if row_cols[3].button(f"Купить ({price}₽)", key=f"buy_wagon_{i}"):
                        if state['money'] >= price:
                            st.session_state.game_state = ge.perform_action(state, "buy_wagon",
                                                                            wagon_index=i); st.rerun()
                        else:
                            st.error("Недостаточно денег!")
            st.markdown("<hr style='margin:0.1rem 0'>", unsafe_allow_html=True)

        st.markdown("")
        if state['moves_made_this_round'] == 0 and state['station'] == 'A':
            with st.container(border=True):
                st.markdown("##### Предрейсовое обслуживание");
                needs_repair = False
                if 0 < state['loco_hp'] < 3:
                    needs_repair = True;
                    cost = int(state['settings']['REPAIR_LOCO'] * state['modifiers']['repair_cost_multiplier'])
                    cols = st.columns(2);
                    cols[0].markdown("**Локомотив**")
                    if cols[1].button(f"Ремонт ({cost}₽)", key="depot_repair_loco", use_container_width=True):
                        if state['money'] >= cost:
                            st.session_state.game_state = ge.perform_action(state, "repair_loco"); st.rerun()
                        else:
                            st.error("Недостаточно денег!")
                for i in range(1, 6):
                    if state[f"wagon_{i}_is_purchased"] and 0 < state[f"wagon_{i}_hp"] < 3:
                        needs_repair = True;
                        cost = int(state['settings']['REPAIR_WAGON'] * state['modifiers']['repair_cost_multiplier'])
                        cols = st.columns(2);
                        cols[0].markdown(f"**{state['settings']['WAGON_INFO'][i]['name']}**")
                        if cols[1].button(f"Ремонт ({cost}₽)", key=f"depot_repair_wagon_{i}", use_container_width=True):
                            if state['money'] >= cost:
                                st.session_state.game_state = ge.perform_action(state, "repair_wagon",
                                                                                wagon_index=i); st.rerun()
                            else:
                                st.error("Недостаточно денег!")
                if not needs_repair: st.info("Весь состав в отличном состоянии.")

    with col2:  # КОЛОНКА КОНТРАКТОВ
        st.markdown("#### Активные контракты")
        # ... (Код отрисовки активных контрактов, без изменений) ...
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
                act_cols = st.columns([1, 2, 4, 1, 2]);
                goods_str = f"{contract['goods_1']}×{contract['qty_1']}";
                if contract['goods_2']: goods_str += f", {contract['goods_2']}×{contract['qty_2']}";
                if contract['goods_3']: goods_str += f", {contract['goods_3']}×{contract['qty_3']}"
                status_color = "lightgreen" if contract.get('is_loaded') else "orange"
                act_cols[0].markdown(f"**{contract['id']}**");
                act_cols[1].markdown(
                    f"{contract['origin']}→{contract['destination']} <span style='color:{status_color};'>●</span>",
                    unsafe_allow_html=True)
                act_cols[2].markdown(f"{goods_str} ({ge.calculate_current_price(contract, state)}₽)");
                act_cols[3].markdown(f"{contract['rounds_left']}")
                with act_cols[4]:
                    loading_forbidden = (state['station'] == 'A' and state['moves_made_this_round'] >= 2)
                    if not contract.get('is_loaded') and state['station'] == contract[
                        'origin'] and not loading_forbidden:
                        if st.button("Погрузка", key=f"load_{contract['id']}"):
                            if ge.check_capacity_for_contract(state, contract):
                                st.session_state.game_state = ge.perform_action(state, "load_contract",
                                                                                contract_id=contract['id']); st.rerun()
                            else:
                                st.error("Недостаточно места!")
                    if contract.get('is_loaded') and state['station'] == contract['destination']:
                        if st.button("Разгрузка", key=f"unload_{contract['id']}"):
                            st.session_state.game_state = ge.perform_action(state, "unload_contract",
                                                                            contract_id=contract['id']);
                            st.rerun()
        st.markdown("")
        if state['moves_made_this_round'] == 0:
            with st.container(border=True):
                st.markdown("##### Взять новый контракт")
                if len(state['active_contracts']) >= 4:
                    st.warning("Максимум 4 контракта.")
                else:
                    contract_cols = st.columns(3);
                    can_take = state['modifiers']['can_take_contracts']
                    s_pool = [c for c in state['contracts_pool'] if c['id'].startswith('P')];
                    m_pool = [c for c in state['contracts_pool'] if c['id'].startswith('M')];
                    h_pool = [c for c in state['contracts_pool'] if c['id'].startswith('S')]
                    if contract_cols[0].button(f"Простой ({len(s_pool)})", disabled=(not s_pool or not can_take),
                                               use_container_width=True): st.session_state.game_state = ge.perform_action(
                        state, "take_contract", ctype='P'); st.rerun()
                    if contract_cols[1].button(f"Средний ({len(m_pool)})", disabled=(not m_pool or not can_take),
                                               use_container_width=True): st.session_state.game_state = ge.perform_action(
                        state, "take_contract", ctype='M'); st.rerun()
                    if contract_cols[2].button(f"Сложный ({len(h_pool)})", disabled=(not h_pool or not can_take),
                                               use_container_width=True): st.session_state.game_state = ge.perform_action(
                        state, "take_contract", ctype='S'); st.rerun()

    with col3:  # КОЛОНКА ДЕЙСТВИЙ
        with st.container(border=True):
            st.markdown("##### Панель управления")
            if st.button("Двигаться", disabled=(state['moves_made_this_round'] >= 2), use_container_width=True):
                st.session_state.game_state = ge.perform_action(state, "move");
                st.rerun()
            if st.button("Конец раунда", disabled=(state['station'] != 'A'),
                         help="Завершить раунд можно только на станции А.", use_container_width=True):
                st.session_state.game_state = ge.perform_action(state, "end_round");
                st.rerun()

            # --- ИЗМЕНЕНИЕ: Кнопка "Новая игра" возвращена сюда ---
            st.markdown("---")
            if st.button("Начать новую игру", type="secondary", use_container_width=True):
                st.session_state.confirm_restart_ingame = True

            if st.session_state.get("confirm_restart_ingame", False):
                st.warning("**Сбросить текущий прогресс?**")
                c1, c2 = st.columns(2)
                if c1.button("Да", type="primary", use_container_width=True):
                    st.session_state.game_state = ge.initialize_state(st.session_state.game_settings)
                    st.session_state.confirm_restart_ingame = False;
                    st.rerun()
                if c2.button("Нет", use_container_width=True):
                    st.session_state.confirm_restart_ingame = False;
                    st.rerun()

with tab_instruction:
    st.header("📖 Инструкция по игре «Железные дороги России»")
    st.markdown("---")

    st.subheader("🚂 Привет, будущий начальник поездов!")
    st.markdown("""
    **Твоя цель** — стать самым успешным и богатым владельцем железной дороги! Ты будешь перевозить разные грузы, выполнять задания (контракты), чинить свой поезд и покупать новые вагоны. Чем больше денег ты заработаешь, тем лучше!
    """)

    st.subheader("👀 Твой первый взгляд на игру")
    st.markdown("""
    На игровом экране ты увидишь несколько важных частей:

    - **Верхняя панель:** Здесь твои самые главные цифры:
        - **Раунд:** Считай, что это один игровой день.
        - **Время (⏰):** Твои "очки действий" на раунд. Почти всё, что ты делаешь, тратит время!
        - **Деньги (💰):** Твоя копилка. Трать с умом!
        - **Станция:** Показывает, где сейчас твой поезд: на **Станции А** (твоя база) или на **Станции Б**.

    - **Событие раунда:** В начале каждого "дня" (раунда) случается что-то неожиданное. Это может быть хорошо (премия!) или плохо (поломка!). Всегда читай, что произошло!

    - **Состав поезда:** Это твой главный инструмент!
        - **Здоровье (❤️):** Показывает, насколько цел твой локомотив или вагон. 3 сердечка — идеально! Если сердечек станет 0, вагон сломается, а если сломается локомотив — это конец игры!
        - **Заполненность (🔲):** Показывает, сколько места в вагоне и что в нём лежит.

    - **Активные контракты:** Это твои текущие задания. Здесь видно, какой груз, откуда и куда нужно отвезти.

    - **Панель управления:** Здесь находятся все кнопки для управления игрой.
    """)

    st.subheader("⚙️ Как устроен игровой раунд (один день из жизни)")
    st.markdown("""
    Каждый раунд — это как один рейс. Ты всегда начинаешь и заканчиваешь его на **Станции А**.

    **Этап 1: Подготовка в Депо (только в начале раунда на Станции А)**
    Пока твой поезд стоит на базе и ты еще никуда не поехал, ты можешь:
    1.  **Починить поезд:** Если у локомотива или вагонов меньше 3-х сердечек, их можно починить. Ремонт стоит денег и **1 единицу времени** (только за первый ремонт в раунде).
    2.  **Купить новые вагоны:** Если хватает денег, можно расширить свой состав.
    3.  **Взять новые контракты:** Выбери задания, которые кажутся тебе выгодными. Ты можешь иметь до 4-х контрактов одновременно.

    **Этап 2: Рейс!**
    Когда ты готов, начинается самое интересное:
    1.  **Погрузка:** Нажми кнопку "Погрузка" на контракте. Товары волшебным образом окажутся в нужных вагонах. Это стоит 1 единицу времени.
    2.  **Движение:** Нажми кнопку "Двигаться". Твой поезд поедет на другую станцию (из А в Б, или из Б в А). Это стоит 2 единицы времени. За один раунд можно съездить только "туда и обратно" (всего 2 раза).
    3.  **Разгрузка:** Когда ты приехал на станцию назначения, нажми "Разгрузка". Товар исчезнет, а ты получишь свои честно заработанные деньги! Это стоит 1 единицу времени.

    **Этап 3: Возвращение и конец раунда**
    Твоя главная задача — **вернуться на Станцию А до того, как закончится время!**
    Когда ты вернулся на Станцию А, нажми "Конец раунда". Начинается новый "день", время восполняется, но будь готов:
    - **Сроки контрактов уменьшаются!** Не успел — получишь меньше денег.
    - **Поезд изнашивается:** Есть шанс, что локомотив или один из вагонов получит повреждение (потеряет 1 сердечко).
    """)

    st.subheader("🛠️ Секреты успешного машиниста (Важные правила!)",)

    st.markdown("**1. Меньше сердечек — меньше места в вагоне!**")
    st.markdown("Поврежденный вагон не может везти столько же груза, сколько новый. Это самое важное правило!")
    st.table({
        "Здоровье (❤️)": ["❤️❤️❤️ (3)", "❤️❤️💔 (2)", "❤️💔💔 (1)"],
        "Вместимость Полувагона/Контейнера": ["6 мест", "4 места", "2 места"],
        "Вместимость Платформы": ["3 места", "2 места", "1 место"]
    })

    st.markdown("**2. Почему важно не опаздывать (Штрафы за просрочку)**")
    st.markdown(
        "Каждый раз, когда ты заканчиваешь раунд, у всех твоих активных контрактов уменьшается 'срок годности'. Если ты привезешь груз с опозданием, он будет стоить намного дешевле.")
    st.table({
        "Тип контракта": ["Простой (3 раунда)", "Средний (2 раунда)", "Сложный (1 раунд)"],
        "Опоздание на 1 раунд": ["Получишь 90% цены", "Получишь 70% цены", "Получишь 40% цены"],
        "Опоздание на 2+ раунда": ["Получишь всего 20-60% цены", "Получишь всего 30% цены",
                                   "Контракт почти ничего не стоит"]
    })

    st.markdown("**3. Каждому грузу — свой вагон!**")
    st.markdown("Ты не можешь положить уголь в вагон для ящиков! Это как пытаться налить суп в карман.")
    st.markdown("""
    - **Уголь и Щебень** — только в **Полувагоны**. Причем в один полувагон нельзя одновременно грузить и уголь, и щебень.
    - **Цветные ящики** (Желтый, Зеленый, Синий) — только в **Контейнеры**.
    - **Металл** — только на **Платформу**.
    """)

    st.subheader("🏆 Как стать лучшим? Советы и хитрости")
    st.markdown("""
    - **Стратегия «Осторожный начальник»:** Не рискуй! Всегда чини свой поезд, если у него 2 сердечка. Начинай с простых и средних контрактов, чтобы накопить денег. Покупай новые вагоны, только когда у тебя есть хороший запас в копилке. Медленно, но верно ты станешь богачом!

    - **Стратегия «Рисковый бизнесмен»:** Большой риск — большие деньги! Как можно скорее накопи денег, чтобы купить Платформу. Контракты на Металл самые дорогие! Но будь готов, что твой поезд будет часто ломаться, так как ты будешь экономить на ремонте. Эта стратегия может сделать тебя очень богатым или очень быстро привести к проигрышу!

    - **Всегда проверяй совместимость!** Прежде чем брать контракт, убедись, что у тебя есть подходящий вагон. Нет смысла брать контракт на Металл, если у тебя нет Платформы.
    """)

    st.subheader("📜 Пример первых двух раундов")
    with st.expander("Нажми, чтобы прочитать подробный пример", expanded=True):
        st.markdown("""
        **Раунд 1: Отличный старт!**
        - **Начало:** У тебя 2000₽, 10 времени, 2 вагона с 3-мя сердечками. Ты на Станции А.
        - **Событие:** "Ясная погода". Ура, никаких проблем!
        - **Твои действия:**
            1.  Ремонт не нужен, все целое.
            2.  Берем простой контракт "P1: Уголь x6" (А → Б).
            3.  Нажимаем "Погрузка". Уголь загружается в Полувагон. **Время: 9.**
            4.  Нажимаем "Двигаться". Поезд едет на Станцию Б. **Время: 7.**
            5.  Нажимаем "Разгрузка". Уголь исчезает, а ты получаешь, скажем, 720₽. **Время: 6.** Твои деньги: 2720₽.
            6.  Нажимаем "Двигаться". Поезд возвращается на Станцию А. **Время: 4.**
            7.  Больше ничего не успеть. Нажимаем "Конец раунда".
        - **Итог раунда:** Ты в плюсе! Но в конце раунда твой локомотив от износа теряет 1 сердечко (теперь у него ❤️❤️💔).

        **Раунд 2: Первая проблема**
        - **Начало:** У тебя 2720₽, 10 времени. Ты на Станции А. Локомотив поврежден!
        - **Событие:** "Поломка пути". О нет! Ты теряешь 500₽ и 1 времени. **Деньги: 2220₽, Время: 9.**
        - **Твои действия:**
            1.  **СНАЧАЛА РЕМОНТ!** Твой локомотив поврежден. Заходим в "Предрейсовое обслуживание" и чиним его за 500₽. Это также тратит 1 времени. **Деньги: 1720₽, Время: 8.**
            2.  Теперь можно брать контракты. Возьмем "P3: Желтый x6" (Б → А).
            3.  Нам нужно сначала доехать до груза. Нажимаем "Двигаться". Поезд едет на Станцию Б. **Время: 6.**
            4.  На Станции Б нажимаем "Погрузка". Ящики в Контейнере. **Время: 5.**
            5.  Нажимаем "Двигаться". Возвращаемся на Станцию А. **Время: 3.**
            6.  На Станции А нажимаем "Разгрузка". Получаем деньги! **Время: 2.**
            7.  Нажимаем "Конец раунда".
        - **Итог раунда:** Ты справился с трудностями и снова в плюсе!
        """)

    st.subheader("☠️ Когда игра заканчивается?")
    st.warning("""
    Будь осторожен! Твоя карьера начальника поездов закончится, если:
    1.  **Локомотив сломается полностью** (здоровье упадет до 0).
    2.  **Твои деньги уйдут в минус** (ты станешь банкротом).
    3.  **Время закончится (станет 0), а твой поезд будет на Станции Б.** Ты не успел вернуться на базу!
    """)

with tab_settings:
    st.header("Настройки баланса игры")
    st.info("Изменения вступят в силу после нажатия кнопки 'Применить' внизу.")
    with st.expander("Основные экономические параметры", expanded=True):
        st.session_state.game_settings['STARTING_MONEY'] = st.number_input("Стартовые деньги (₽)", 0, step=500,
                                                                           value=st.session_state.game_settings[
                                                                               'STARTING_MONEY'])
        st.session_state.game_settings['REPAIR_LOCO'] = st.number_input("Стоимость ремонта локомотива (₽)", 0, step=50,
                                                                        value=st.session_state.game_settings[
                                                                            'REPAIR_LOCO'])
        st.session_state.game_settings['REPAIR_WAGON'] = st.number_input("Стоимость ремонта вагона (₽)", 0, step=50,
                                                                         value=st.session_state.game_settings[
                                                                             'REPAIR_WAGON'])
    st.subheader("Цены на покупку вагонов")
    cols = st.columns(2)
    for i in range(1, 6):
        wagon_name = cfg.WAGON_INFO[i]['name']
        st.session_state.game_settings['WAGON_PRICES'][i] = cols[(i - 1) % 2].number_input(f"Цена '{wagon_name}'", 0,
                                                                                           step=100, value=
                                                                                           st.session_state.game_settings[
                                                                                               'WAGON_PRICES'][i])
    st.subheader("Цены на товары (влияют на стоимость контрактов)")
    cols = st.columns(3)
    good_keys = list(cfg.GOODS_PRICES.keys())
    for i, good in enumerate(good_keys):
        st.session_state.game_settings['GOODS_PRICES'][good] = cols[i % 3].number_input(f"Цена '{good}'", 0, step=10,
                                                                                        value=
                                                                                        st.session_state.game_settings[
                                                                                            'GOODS_PRICES'][good])
    st.markdown("---")
    if st.button("Применить настройки и начать новую игру", type="primary"):
        st.session_state.game_state = ge.initialize_state(st.session_state.game_settings)
        st.success("Настройки применены! Новая игра началась на вкладке 'Игра'.")
        st.balloons()  # <-- Добавлена яркая обратная связь!
        # st.rerun() # rerun здесь может быть избыточным, так как смена виджетов его вызовет