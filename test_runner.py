# test_runner.py
import game_engine as ge
import pandas as pd
from tqdm import tqdm
import random

NUM_SIMULATIONS_PER_STRATEGY = 1000  # Количество игр для каждой стратегии


# ==============================================================================
# --- БЛОК СТРАТЕГИЙ ПРИНЯТИЯ РЕШЕНИЙ (AI для каждой роли) ---
# ==============================================================================

def make_decision_adult(state):
    """
    СТРАТЕГИЯ 1: Взрослый игрок (30 лет) - БАЗОВАЯ
    Логика: Рациональный, сбалансированный, не склонный к риску.
    - Ремонтируется заранее (при 2 HP).
    - Выполняет действия в логическом порядке для получения прибыли.
    - Старается не рисковать.
    """
    # Приоритет 1: Разгрузка для получения прибыли
    for contract in state['active_contracts']:
        if contract.get('is_loaded') and state['station'] == contract['destination']:
            return "unload_contract", {"contract_id": contract['id']}

    # Приоритет 2: Движение к цели, если что-то загружено
    if any(c.get('is_loaded') for c in state['active_contracts']) and state['moves_made_this_round'] < 2:
        return "move", {}

    # Приоритет 3: Обслуживание в депо (начало раунда)
    if state['moves_made_this_round'] == 0 and state['station'] == 'A':
        cost_loco = int(ge.REPAIR_LOCO * state['modifiers']['repair_cost_multiplier'])
        if state['loco_hp'] <= 2 and state['money'] >= cost_loco:  # Ремонтируется при 2 и 1 HP
            return "repair_loco", {}
        for i in range(1, 6):
            if state[f"wagon_{i}_is_purchased"] and state[f"wagon_{i}_hp"] <= 2 and state[f"wagon_{i}_hp"] > 0:
                cost_wagon = int(ge.REPAIR_WAGON * state['modifiers']['repair_cost_multiplier'])
                if state['money'] >= cost_wagon:
                    return "repair_wagon", {"wagon_index": i}

    # Приоритет 4: Погрузка доступных контрактов
    if not (state['station'] == 'A' and state['moves_made_this_round'] >= 2):
        for contract in state['active_contracts']:
            if not contract.get('is_loaded') and state['station'] == contract['origin']:
                if ge.check_capacity_for_contract(state, contract):
                    return "load_contract", {"contract_id": contract['id']}

    # Приоритет 5: Движение на станцию отправления для погрузки
    if state['moves_made_this_round'] < 2:
        for contract in state['active_contracts']:
            if not contract.get('is_loaded') and state['station'] != contract['origin']:
                return "move", {}

    # Приоритет 6: Взять новый контракт в начале раунда
    if state['moves_made_this_round'] == 0 and len(state['active_contracts']) < 4 and state['modifiers'][
        'can_take_contracts']:
        return "take_contract", {"ctype": 'P'}  # Начинает с простых

    # Последний вариант: завершить раунд, если на станции А
    if state['station'] == 'A':
        return "end_round", {}
    elif state['moves_made_this_round'] < 2:  # Или вернуться на базу
        return "move", {}

    return "end_round", {}  # Запасной вариант


def make_decision_kid(state):
    """
    СТРАТЕГИЯ 2: Ребенок (10 лет)
    Логика: Импульсивный, хочет всего и сразу, игнорирует обслуживание.
    - Ремонтируется только в самом крайнем случае (при 1 HP).
    - Пытается взять как можно больше контрактов.
    - Может купить вагон, даже если он не очень нужен.
    """
    # Приоритет 1: Взять много контрактов
    if state['moves_made_this_round'] == 0 and len(state['active_contracts']) < 4 and state['modifiers'][
        'can_take_contracts']:
        return "take_contract", {"ctype": random.choice(['P', 'M'])}

    # Приоритет 2: Разгрузка, чтобы увидеть деньги
    for contract in state['active_contracts']:
        if contract.get('is_loaded') and state['station'] == contract['destination']:
            return "unload_contract", {"contract_id": contract['id']}

    # Приоритет 3: Погрузить что-нибудь
    for contract in state['active_contracts']:
        if not contract.get('is_loaded') and state['station'] == contract['origin']:
            if ge.check_capacity_for_contract(state, contract):
                return "load_contract", {"contract_id": contract['id']}

    # Приоритет 4: Купить новый вагон, если есть деньги
    if state['moves_made_this_round'] == 0:
        for i in range(1, 6):
            if not state[f"wagon_{i}_is_purchased"] and state['money'] >= ge.WAGON_PRICES[i]:
                return "buy_wagon", {"wagon_index": i}

    # Приоритет 5: Двигаться
    if state['moves_made_this_round'] < 2:
        return "move", {}

    # Ремонт - самый низкий приоритет
    if state['loco_hp'] == 1 and state['money'] >= int(ge.REPAIR_LOCO * state['modifiers']['repair_cost_multiplier']):
        return "repair_loco", {}

    if state['station'] == 'A':
        return "end_round", {}

    return "move", {}  # Если застрял, просто пытается ехать


def can_fulfill_contract_requirements(state, contract):
    """
    Новая вспомогательная функция.
    Проверяет, есть ли у игрока в наличии хотя бы один нужный тип вагона для КАЖДОГО товара в контракте.
    """
    goods_needed = []
    if contract.get("goods_1") and contract.get("qty_1", 0) > 0: goods_needed.append(contract["goods_1"])
    if contract.get("goods_2") and contract.get("qty_2", 0) > 0: goods_needed.append(contract["goods_2"])
    if contract.get("goods_3") and contract.get("qty_3", 0) > 0: goods_needed.append(contract["goods_3"])

    # Получаем список типов вагонов, которые есть у игрока
    owned_wagon_types = set()
    for i in range(1, 6):
        if state[f"wagon_{i}_is_purchased"]:
            owned_wagon_types.add(ge.WAGON_INFO[i]['type'])

    # Проверяем, есть ли для каждого необходимого товара подходящий вагон
    for good in set(goods_needed):  # set() чтобы не проверять дубликаты
        required_wagon_type = ge.GOOD_COMPATIBILITY.get(good)
        if required_wagon_type not in owned_wagon_types:
            return False  # Если для хотя бы одного товара нет вагона, контракт невыполним

    return True


def make_decision_exploiter(state):
    """
    СТРАТЕГИЯ 3: Эксплойтер / Мин-максер (УЛУЧШЕННАЯ ВЕРСЯ)
    Логика: Анализирует свои возможности, целенаправленно инвестирует в нужные активы,
    ищет максимальную выгоду и использует лазейки.
    """
    # 0. Особая логика для событий (высший приоритет)
    if state['current_event']:
        # Если скидка на ремонт, чиним всё, что можно, чтобы сэкономить
        if state['current_event']['id'] == 'E08' and state['moves_made_this_round'] == 0:
            if state['loco_hp'] < 3 and state['money'] >= int(ge.REPAIR_LOCO * 0.5):
                return "repair_loco", {}
            for i in range(1, 6):
                if state[f"wagon_{i}_is_purchased"] and state[f"wagon_{i}_hp"] < 3 and state['money'] >= int(
                        ge.REPAIR_WAGON * 0.5):
                    return "repair_wagon", {"wagon_index": i}

    # 1. Разгрузка для получения прибыли (всегда выгодно)
    for contract in state['active_contracts']:
        if contract.get('is_loaded') and state['station'] == contract['destination']:
            return "unload_contract", {"contract_id": contract['id']}

    # 2. Целенаправленная покупка вагонов в депо
    if state['moves_made_this_round'] == 0 and state['station'] == 'A':
        # Ищем самый дорогой контракт в пуле, который мы НЕ МОЖЕМ выполнить из-за отсутствия вагона
        for c_type in ['S', 'M', 'P']:
            for contract in [c for c in state['contracts_pool'] if c['id'].startswith(c_type)]:
                if not can_fulfill_contract_requirements(state, contract):
                    # Определяем, какой вагон нужен
                    for good in [contract['goods_1'], contract['goods_2'], contract['goods_3']]:
                        if not good: continue
                        req_wagon_type = ge.GOOD_COMPATIBILITY[good]
                        # Находим конкретный номер вагона, которого не хватает
                        for i in range(1, 6):
                            if ge.WAGON_INFO[i]['type'] == req_wagon_type and not state[f"wagon_{i}_is_purchased"]:
                                price = ge.WAGON_PRICES[i]
                                # Если хватает денег, покупаем для будущей прибыли
                                if state['money'] >= price:
                                    return "buy_wagon", {"wagon_index": i}
                                break  # Проверили этот тип вагона, идем дальше
                    break  # Проверили этот контракт, идем дальше

    # 3. Ремонт, только если критично (1 HP)
    if state['moves_made_this_round'] == 0 and state['station'] == 'A':
        cost = int(ge.REPAIR_LOCO * state['modifiers']['repair_cost_multiplier'])
        if state['loco_hp'] == 1 and state['money'] >= cost:
            return "repair_loco", {}

    # 4. Погрузка готовых контрактов
    if not (state['station'] == 'A' and state['moves_made_this_round'] >= 2):
        for contract in state['active_contracts']:
            if not contract.get('is_loaded') and state['station'] == contract[
                'origin'] and ge.check_capacity_for_contract(state, contract):
                return "load_contract", {"contract_id": contract['id']}

    # 5. Умный выбор контракта (самый сложный из ВЫПОЛНИМЫХ)
    if state['moves_made_this_round'] == 0 and len(state['active_contracts']) < 4 and state['modifiers'][
        'can_take_contracts']:
        for c_type in ['S', 'M', 'P']:
            contract_pool = [c for c in state['contracts_pool'] if c['id'].startswith(c_type)]
            if contract_pool:
                # Проверяем, можем ли мы В ПРИНЦИПЕ выполнить контракт
                for contract in sorted(contract_pool, key=ge.contract_price, reverse=True):
                    if can_fulfill_contract_requirements(state, contract):
                        return "take_contract", {"ctype": c_type}

    # 6. Движение (к цели или за грузом)
    if state['moves_made_this_round'] < 2: return "move", {}

    # 7. Завершение раунда
    if state['station'] == 'A': return "end_round", {}

    return "move", {}  # Запасной вариант - вернуться на базу


def make_decision_erratic(state):
    """
    СТРАТЕГИЯ 4: Игрок, допускающий ошибки
    Логика: В основном действует рационально (как "Взрослый"), но с некоторым шансом совершает ошибку.
    - Может забыть разгрузиться.
    - Может завершить раунд, хотя еще есть время и действия.
    - Может взять не тот контракт.
    """
    # Шанс 15% совершить неоптимальное действие (пропустить приоритет)
    if random.random() < 0.15:
        # "Забываем" про самый важный приоритет и переходим к следующему
        pass  # Просто позволяем коду идти дальше по списку
    else:
        # Если не ошибаемся, делаем самое важное действие
        for contract in state['active_contracts']:
            if contract.get('is_loaded') and state['station'] == contract['destination']:
                return "unload_contract", {"contract_id": contract['id']}

    # Шанс 10% просто закончить раунд, если это возможно
    if state['station'] == 'A' and random.random() < 0.10:
        return "end_round", {}

    # В остальном логика похожа на "Взрослого"
    if state['moves_made_this_round'] < 2:
        return "move", {}

    if state['moves_made_this_round'] == 0 and len(state['active_contracts']) < 4 and state['modifiers'][
        'can_take_contracts']:
        # Берет случайный контракт, а не самый логичный
        return "take_contract", {"ctype": random.choice(['P', 'M', 'S'])}

    if state['station'] == 'A':
        return "end_round", {}

    return "move", {}


# ==============================================================================
# --- ОСНОВНОЙ БЛОК ЗАПУСКА И АНАЛИЗА ---
# ==============================================================================

def run_simulation_for_strategy(strategy_func):
    """Прогоняет одну полную игру до конца, используя переданную стратегию."""
    state = ge.initialize_state()
    max_steps = 500
    for _ in range(max_steps):
        if state['game_over']:
            break
        action, kwargs = strategy_func(state)
        state = ge.perform_action(state, action, **kwargs)
    return {
        "final_round": state['round'],
        "final_money": state['money'],
        "game_over_reason": state['game_over_reason'] or "Max steps reached"
    }


if __name__ == "__main__":
    # --- БЛОК ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА В ФАЙЛ ---
    import sys
    from datetime import datetime

    # Создаем уникальное имя файла с датой и временем
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"simulation_report_{timestamp}.txt"

    # Сохраняем оригинальный стандартный вывод
    original_stdout = sys.stdout

    print(f"Запуск симуляций... Отчет будет сохранен в файл: {report_filename}")

    # Открываем файл для записи и назначаем его как стандартный вывод
    with open(report_filename, 'w', encoding='utf-8') as f:
        sys.stdout = f

        # --- ВСЯ ВАША СТАРАЯ ЛОГИКА ТЕПЕРЬ НАХОДИТСЯ ЗДЕСЬ ---
        # Все команды print() теперь будут писать в файл, а не в консоль.

        STRATEGIES = {
            "Взрослый (осторожный)": make_decision_adult,
            "Ребенок (импульсивный)": make_decision_kid,
            # "Эксплойтер (рисковый)": make_decision_exploiter,
            # "Ошибающийся игрок": make_decision_erratic,
        }

        all_results = []

        # Запускаем симуляции для каждой стратегии
        # tqdm будет писать в консоль, так как он использует stderr по умолчанию, что нам и нужно.
        for name, strategy_func in STRATEGIES.items():
            # Мы не можем использовать print здесь, так как он пишет в файл.
            # tqdm справится с отображением прогресса в консоли.
            results = [run_simulation_for_strategy(strategy_func) for _ in
                       tqdm(range(NUM_SIMULATIONS_PER_STRATEGY), desc=f"Simulating '{name}'")]
            for res in results:
                res['strategy'] = name
            all_results.extend(results)

        print("=" * 80)
        print(f"АНАЛИЗ РЕЗУЛЬТАТОВ СИМУЛЯЦИИ ({NUM_SIMULATIONS_PER_STRATEGY} игр на каждую стратегию)")
        print(f"Отчет сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        df = pd.DataFrame(all_results)

        # Настройка pandas для полного вывода без урезания
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)  # Большая ширина для широких таблиц

        # Таблица 1: Ключевые показатели эффективности
        print("\n\n--- 📈 1. КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ ЭФФЕКТИВНОСТИ ---\n")
        grouped = df.groupby('strategy')
        survival_rate = grouped['game_over_reason'].apply(lambda x: (x == 'Max steps reached').sum() / len(x) * 100)
        summary_df = pd.DataFrame({
            'Средний доход (₽)': grouped['final_money'].mean().round(0).astype(int),
            'Медианный доход (₽)': grouped['final_money'].median().round(0).astype(int),
            'Макс. доход (₽)': grouped['final_money'].max().astype(int),
            'Средняя длина игры (раунды)': grouped['final_round'].mean().round(1),
            'Процент выживаемости': survival_rate.apply(lambda x: f"{x:.1f}%")
        }).sort_values('Средний доход (₽)', ascending=False)
        print(summary_df.to_string())  # Используем to_string() для гарантированного полного вывода

        # Таблица 2: Подробная статистика по финальному доходу
        print("\n\n" + "-" * 80)
        print("--- 💰 2. ДЕТАЛЬНАЯ СТАТИСТИКА ПО ФИНАЛЬНОМУ ДОХОДУ ---")
        print("(25%, 50%, 75% - перцентили, показывающие доход 'слабых', 'средних' и 'сильных' игроков)\n")
        money_stats = grouped['final_money'].describe(percentiles=[.25, .5, .75]).round(0).astype(int)
        money_stats = money_stats.drop(columns=['count', 'mean'])
        print(money_stats.to_string())

        # Таблица 3: Причины поражения в процентах от всех игр
        print("\n\n" + "-" * 80)
        print("--- 📉 3. ПРИЧИНЫ ОКОНЧАНИЯ ИГРЫ (% от общего числа игр) ---\n")
        reason_crosstab_percent = pd.crosstab(index=df['strategy'], columns=df['game_over_reason'],
                                              normalize='index').applymap(lambda x: f"{x:.1%}")
        print(reason_crosstab_percent.to_string())

        # Таблица 4: Причины поражения в абсолютных числах
        print("\n\n" + "-" * 80)
        print("--- 🔢 4. ПРИЧИНЫ ОКОНЧАНИЯ ИГРЫ (абсолютное количество игр) ---\n")
        reason_crosstab_absolute = pd.crosstab(index=df['strategy'], columns=df['game_over_reason'])
        print(reason_crosstab_absolute.to_string())

        print("\n" + "=" * 80)
        print("АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 80)

    # --- ВОЗВРАЩАЕМ СТАНДАРТНЫЙ ВЫВОД ОБРАТНО В КОНСОЛЬ ---
    sys.stdout = original_stdout
    print(f"\nАнализ завершен. Подробный отчет сохранен в файл: {report_filename}")