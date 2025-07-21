# test_runner.py
import random
from datetime import datetime
import pandas as pd
from tqdm import tqdm

# Импортируем движок для логики и конфиг для констант
import game_engine as ge
from config import REPAIR_LOCO, REPAIR_WAGON, WAGON_PRICES, WAGON_INFO, GOOD_COMPATIBILITY

# --- 1. ПАРАМЕТРЫ СИМУЛЯЦИИ ---
NUM_SIMULATIONS_PER_STRATEGY = 1000  # Количество игр для каждой стратегии


# --- 2. БЛОК СТРАТЕГИЙ ПРИНЯТИЯ РЕШЕНИЙ (AI для каждой роли) ---

def can_fulfill_contract_requirements(state, contract):
    """Проверяет, есть ли у игрока нужные типы вагонов для КАЖДОГО товара в контракте."""
    goods_needed = [good for good in [contract.get("goods_1"), contract.get("goods_2"), contract.get("goods_3")] if
                    good]
    owned_wagon_types = {WAGON_INFO[i]['type'] for i in range(1, 6) if state[f"wagon_{i}_is_purchased"]}
    for good in set(goods_needed):
        if GOOD_COMPATIBILITY.get(good) not in owned_wagon_types:
            return False
    return True


def make_decision_adult(state):
    """СТРАТЕГИЯ: Взрослый (осторожный)"""
    if any(c.get('is_loaded') and state['station'] == c['destination'] for c in state['active_contracts']):
        return "unload_contract", {"contract_id": next(
            c['id'] for c in state['active_contracts'] if c.get('is_loaded') and state['station'] == c['destination'])}
    if any(c.get('is_loaded') for c in state['active_contracts']) and state['moves_made_this_round'] < 2:
        return "move", {}
    if state['moves_made_this_round'] == 0 and state['station'] == 'A':
        cost_loco = int(REPAIR_LOCO * state['modifiers']['repair_cost_multiplier'])
        if state['loco_hp'] <= 2 and state['loco_hp'] > 0 and state['money'] >= cost_loco:
            return "repair_loco", {}
        for i in range(1, 6):
            if state[f"wagon_{i}_is_purchased"] and 0 < state[f"wagon_{i}_hp"] <= 2:
                cost_wagon = int(REPAIR_WAGON * state['modifiers']['repair_cost_multiplier'])
                if state['money'] >= cost_wagon:
                    return "repair_wagon", {"wagon_index": i}
    loading_forbidden = (state['station'] == 'A' and state['moves_made_this_round'] >= 2)
    if not loading_forbidden:
        for c in state['active_contracts']:
            if not c.get('is_loaded') and state['station'] == c['origin'] and ge.check_capacity_for_contract(state, c):
                return "load_contract", {"contract_id": c['id']}
    if state['moves_made_this_round'] < 2 and any(not c.get('is_loaded') for c in state['active_contracts']):
        return "move", {}
    if state['moves_made_this_round'] == 0 and len(state['active_contracts']) < 4 and state['modifiers'][
        'can_take_contracts']:
        return "take_contract", {"ctype": 'P'}
    if state['station'] == 'A':
        return "end_round", {}
    elif state['moves_made_this_round'] < 2:
        return "move", {}
    return "end_round", {}


def make_decision_kid(state):
    """СТРАТЕГИЯ: Ребенок (импульсивный)"""
    if state['moves_made_this_round'] == 0 and len(state['active_contracts']) < 4 and state['modifiers'][
        'can_take_contracts']:
        return "take_contract", {"ctype": random.choice(['P', 'M'])}
    if any(c.get('is_loaded') and state['station'] == c['destination'] for c in state['active_contracts']):
        return "unload_contract", {"contract_id": next(
            c['id'] for c in state['active_contracts'] if c.get('is_loaded') and state['station'] == c['destination'])}
    for c in state['active_contracts']:
        if not c.get('is_loaded') and state['station'] == c['origin'] and ge.check_capacity_for_contract(state, c):
            return "load_contract", {"contract_id": c['id']}
    if state['moves_made_this_round'] == 0:
        for i in range(1, 6):
            if not state[f"wagon_{i}_is_purchased"] and state['money'] >= WAGON_PRICES[i]:
                return "buy_wagon", {"wagon_index": i}
    if state['moves_made_this_round'] < 2: return "move", {}
    if state['loco_hp'] == 1 and state['money'] >= int(REPAIR_LOCO * state['modifiers']['repair_cost_multiplier']):
        return "repair_loco", {}
    if state['station'] == 'A': return "end_round", {}
    return "move", {}


def make_decision_exploiter(state):
    """СТРАТЕГИЯ: Эксплойтер (рисковый)"""
    if state['current_event'] and state['current_event']['id'] == 'E08' and state['moves_made_this_round'] == 0:
        if state['loco_hp'] < 3 and state['money'] >= int(REPAIR_LOCO * 0.5): return "repair_loco", {}
        for i in range(1, 6):
            if state[f"wagon_{i}_is_purchased"] and state[f"wagon_{i}_hp"] < 3 and state['money'] >= int(
                    REPAIR_WAGON * 0.5):
                return "repair_wagon", {"wagon_index": i}
    if any(c.get('is_loaded') and state['station'] == c['destination'] for c in state['active_contracts']):
        return "unload_contract", {"contract_id": next(
            c['id'] for c in state['active_contracts'] if c.get('is_loaded') and state['station'] == c['destination'])}
    if state['moves_made_this_round'] == 0 and state['station'] == 'A':
        for c_type in ['S', 'M', 'P']:
            for contract in [c for c in state['contracts_pool'] if c['id'].startswith(c_type)]:
                if not can_fulfill_contract_requirements(state, contract):
                    for good in [contract['goods_1'], contract['goods_2'], contract['goods_3']]:
                        if not good: continue
                        req_wagon_type = GOOD_COMPATIBILITY[good]
                        for i in range(1, 6):
                            if WAGON_INFO[i]['type'] == req_wagon_type and not state[f"wagon_{i}_is_purchased"]:
                                price = WAGON_PRICES[i]
                                if state['money'] >= price: return "buy_wagon", {"wagon_index": i}
                                break
                    break
    if state['moves_made_this_round'] == 0 and state['station'] == 'A':
        cost = int(REPAIR_LOCO * state['modifiers']['repair_cost_multiplier'])
        if state['loco_hp'] == 1 and state['money'] >= cost: return "repair_loco", {}
    for c in state['active_contracts']:
        if not c.get('is_loaded') and state['station'] == c['origin'] and ge.check_capacity_for_contract(state, c):
            return "load_contract", {"contract_id": c['id']}
    if state['moves_made_this_round'] == 0 and len(state['active_contracts']) < 4 and state['modifiers'][
        'can_take_contracts']:
        for c_type in ['S', 'M', 'P']:
            pool = [c for c in state['contracts_pool'] if c['id'].startswith(c_type)]
            if any(can_fulfill_contract_requirements(state, c) for c in pool):
                return "take_contract", {"ctype": c_type}
    if state['moves_made_this_round'] < 2: return "move", {}
    if state['station'] == 'A': return "end_round", {}
    return "move", {}


def make_decision_erratic(state):
    """СТРАТЕГИЯ: Игрок, допускающий ошибки"""
    if random.random() > 0.15:  # 85% шанс действовать оптимально
        if any(c.get('is_loaded') and state['station'] == c['destination'] for c in state['active_contracts']):
            return "unload_contract", {"contract_id": next(c['id'] for c in state['active_contracts'] if
                                                           c.get('is_loaded') and state['station'] == c['destination'])}
    if state['station'] == 'A' and random.random() < 0.10: return "end_round", {}
    if state['moves_made_this_round'] < 2: return "move", {}
    if state['moves_made_this_round'] == 0 and len(state['active_contracts']) < 4 and state['modifiers'][
        'can_take_contracts']:
        return "take_contract", {"ctype": random.choice(['P', 'M', 'S'])}
    if state['station'] == 'A': return "end_round", {}
    return "move", {}


# --- 3. ФУНКЦИИ ЗАПУСКА И АНАЛИЗА ---

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
    STRATEGIES = {
        "Взрослый (осторожный)": make_decision_adult,
        "Ребенок (импульсивный)": make_decision_kid,
        # "Эксплойтер (рисковый)": make_decision_exploiter,
        # "Ошибающийся игрок": make_decision_erratic,
    }

    # --- БЛОК ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА В ФАЙЛ ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"simulation_report_{timestamp}.txt"
    print(f"Запуск симуляций... Отчет будет сохранен в файл: {report_filename}")

    with open(report_filename, 'w', encoding='utf-8') as f:
        all_results = []
        for name, strategy_func in STRATEGIES.items():
            # tqdm будет писать в консоль, что очень удобно
            results = [run_simulation_for_strategy(strategy_func) for _ in
                       tqdm(range(NUM_SIMULATIONS_PER_STRATEGY), desc=f"Simulating '{name}'")]
            for res in results: res['strategy'] = name
            all_results.extend(results)

        f.write("=" * 80 + "\n")
        f.write(f"АНАЛИЗ РЕЗУЛЬТАТОВ СИМУЛЯЦИИ ({NUM_SIMULATIONS_PER_STRATEGY} игр на каждую стратегию)\n")
        f.write(f"Отчет сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n")

        df = pd.DataFrame(all_results)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)

        f.write("\n\n--- 📈 1. КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ ЭФФЕКТИВНОСТИ ---\n\n")
        grouped = df.groupby('strategy')
        survival_rate = grouped['game_over_reason'].apply(lambda x: (x == 'Max steps reached').sum() / len(x) * 100)
        summary_df = pd.DataFrame({
            'Средний доход (₽)': grouped['final_money'].mean().round(0).astype(int),
            'Медианный доход (₽)': grouped['final_money'].median().round(0).astype(int),
            'Макс. доход (₽)': grouped['final_money'].max().astype(int),
            'Средняя длина игры (раунды)': grouped['final_round'].mean().round(1),
            'Процент выживаемости': survival_rate.apply(lambda x: f"{x:.1f}%")
        }).sort_values('Средний доход (₽)', ascending=False)
        f.write(summary_df.to_string())

        f.write("\n\n\n" + "-" * 80)
        f.write("\n--- 💰 2. ДЕТАЛЬНАЯ СТАТИСТИКА ПО ФИНАЛЬНОМУ ДОХОДУ ---\n")
        f.write("(25%, 50%, 75% - перцентили, показывающие доход 'слабых', 'средних' и 'сильных' игроков)\n\n")
        money_stats = grouped['final_money'].describe(percentiles=[.25, .5, .75]).round(0).astype(int)
        money_stats = money_stats.drop(columns=['count', 'mean'])
        f.write(money_stats.to_string())

        f.write("\n\n\n" + "-" * 80)
        f.write("\n--- 📉 3. ПРИЧИНЫ ОКОНЧАНИЯ ИГРЫ (% от общего числа игр) ---\n\n")
        reason_crosstab_percent = pd.crosstab(index=df['strategy'], columns=df['game_over_reason'],
                                              normalize='index').applymap(lambda x: f"{x:.1%}")
        f.write(reason_crosstab_percent.to_string())

        f.write("\n\n\n" + "-" * 80)
        f.write("\n--- 🔢 4. ПРИЧИНЫ ОКОНЧАНИЯ ИГРЫ (абсолютное количество игр) ---\n\n")
        reason_crosstab_absolute = pd.crosstab(index=df['strategy'], columns=df['game_over_reason'])
        f.write(reason_crosstab_absolute.to_string())

        f.write("\n\n" + "=" * 80)
        f.write("\nАНАЛИЗ ЗАВЕРШЕН\n")
        f.write("=" * 80)

    print(f"\nАнализ завершен. Подробный отчет сохранен в файл: {report_filename}")