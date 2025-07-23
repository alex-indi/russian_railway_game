# game_engine.py
import random
from config import CONTRACTS, EVENTS


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДВИЖКА ---
def _deepcopy_state(state):
    """Безопасная и быстрая функция глубокого копирования для состояния игры."""
    new_state = {}
    for key, value in state.items():
        if isinstance(value, list):
            new_state[key] = [item.copy() for item in value]
        elif isinstance(value, dict):
            new_state[key] = value.copy()
        else:
            new_state[key] = value
    return new_state


def contract_price(contract, state):
    s = 0;
    prices = state['settings']['GOODS_PRICES']
    for g, q in [(contract["goods_1"], contract["qty_1"]), (contract["goods_2"], contract["qty_2"]),
                 (contract["goods_3"], contract["qty_3"])]:
        if g and q: s += prices.get(g, 0) * q
    return s


def calculate_current_price(contract, state):
    base_price = contract_price(contract, state)
    rounds_left = contract.get('rounds_left', contract['max_rounds'])
    if contract['id'].startswith('P'):
        if rounds_left <= 0: return int(base_price * 0.4)
        if rounds_left == 1: return int(base_price * 0.6)
        if rounds_left == 2: return int(base_price * 0.8)
    elif contract['id'].startswith('M'):
        if rounds_left <= 0: return int(base_price * 0.4)
        if rounds_left == 1: return int(base_price * 0.6)
    elif contract['id'].startswith('S'):
        if rounds_left <= 0: return int(base_price * 0.5)
    return base_price


def get_current_capacity(state, wagon_index):
    hp = state[f"wagon_{wagon_index}_hp"]
    wagon_type = state['settings']['WAGON_INFO'][wagon_index]["type"]
    if hp <= 0: return 0
    if wagon_type == "platform":
        return hp
    else:
        if hp == 3: return 6
        if hp == 2: return 4
        if hp == 1: return 2
    return 0


def check_capacity_for_contract(state, contract):
    goods_to_load = []
    for g, q in [(contract["goods_1"], contract["qty_1"]), (contract["goods_2"], contract["qty_2"]),
                 (contract["goods_3"], contract["qty_3"])]:
        if g and q: goods_to_load.extend([g] * q)
    available_space = {i: get_current_capacity(state, i) - len(state[f"wagon_{i}_contents"]) for i in range(1, 6) if
                       state[f"wagon_{i}_is_purchased"]}
    gondola_type = {i: state[f"wagon_{i}_contents"][0]['good'] for i in available_space if
                    state['settings']['WAGON_INFO'][i]["type"] == "gondola" and state[f"wagon_{i}_contents"]}
    for good in goods_to_load:
        found_slot = False;
        compatible_wagon_type = state['settings']['GOOD_COMPATIBILITY'][good]
        for i in sorted(available_space.keys()):
            if state['settings']['WAGON_INFO'][i]["type"] == compatible_wagon_type and available_space[i] > 0:
                if compatible_wagon_type == "gondola":
                    if i in gondola_type and gondola_type[i] != good: continue
                    if i not in gondola_type: gondola_type[i] = good
                available_space[i] -= 1;
                found_slot = True;
                break
        if not found_slot: return False
    return True


def apply_event_effect(state, event):
    event_id = event['id']
    if event_id in ["E01", "E11"]:
        if state['loco_hp'] > 0:
            state['loco_hp'] -= 1
            if state['loco_hp'] <= 0: state['game_over'], state['game_over_reason'] = True, "Локомотив сломан!"
    elif event_id in ["E02", "E10"]:
        state['loco_hp'] = min(3, state['loco_hp'] + 1)
        for i in range(1, 6):
            if state[f"wagon_{i}_is_purchased"]: state[f"wagon_{i}_hp"] = min(3, state[f"wagon_{i}_hp"] + 1)
    elif event_id in ["E03", "E09"]:
        state['time'], state['money'] = max(0, state['time'] - 1), state['money'] - 500
    elif event_id == "E05":
        state['money'] -= 1000
    elif event_id == "E06":
        state['modifiers']["revenue_multiplier"] = 0.5
    elif event_id == "E07":
        state['loco_hp'] = 3
        for i in range(1, 6):
            if state[f"wagon_{i}_is_purchased"]: state[f"wagon_{i}_hp"] = 3
    elif event_id == "E08":
        state['modifiers']["repair_cost_multiplier"] = 0.5
    elif event_id == "E12":
        state['money'] -= 800
    elif event_id in ["P01", "P07", "P10"]:
        state['time'] = max(0, state['time'] - 2)
    elif event_id in ["P02", "P09"]:
        state['time'] = max(0, state['time'] - 1)
        if random.randint(1, 6) == 1 and state['loco_hp'] > 0:
            state['loco_hp'] -= 1
            if state['loco_hp'] <= 0: state['game_over'], state[
                'game_over_reason'] = True, "Локомотив сломан в снегопад!"
        for i in range(1, 6):
            if state[f"wagon_{i}_is_purchased"] and state[f"wagon_{i}_hp"] > 0 and random.randint(1, 6) == 1:
                state[f"wagon_{i}_hp"] -= 1
                if state[f"wagon_{i}_hp"] <= 0:
                    state[f"wagon_{i}_is_purchased"], state[f"wagon_{i}_contents"] = False, []
    elif event_id in ["P03", "P08"]:
        state['time'] = max(0, state['time'] - 1)
    elif event_id == "P06":
        state['modifiers']["load_unload_time_cost"] = 2
    elif event_id == "H01":
        state['modifiers']["move_time_cost"] = 4
    elif event_id == "H02":
        state['modifiers']["load_unload_time_cost"] = 2
    elif event_id == "H03":
        state['modifiers']["can_take_contracts"] = False
    elif event_id == "H04":
        state['repaired_this_round'] = True
    elif event_id == "H05":
        state['money'] += 1000
    elif event_id == "H06":
        state['modifiers']["move_time_cost"] = 0
    elif event_id == "H08":
        state['money'] -= 500
    if state['money'] < 0: state['game_over'], state[
        'game_over_reason'] = True, f"Банкротство из-за события «{event['name']}»!"


def _load_goods(state, contract_id):
    for c in state['active_contracts']:
        if c['id'] == contract_id:
            goods_to_load = []
            for g, q in [(c["goods_1"], c["qty_1"]), (c["goods_2"], c["qty_2"]), (c["goods_3"], c["qty_3"])]:
                if g and q: goods_to_load.extend([{"good": g, "contract_id": c['id']}] * q)
            for item in goods_to_load:
                ctype = state['settings']['GOOD_COMPATIBILITY'][item['good']]
                for i in range(1, 6):
                    if state[f"wagon_{i}_is_purchased"] and state['settings']['WAGON_INFO'][i]['type'] == ctype and len(
                            state[f"wagon_{i}_contents"]) < get_current_capacity(state, i):
                        if ctype == "gondola" and state[f"wagon_{i}_contents"] and state[f"wagon_{i}_contents"][0][
                            'good'] != item['good']: continue
                        state[f"wagon_{i}_contents"].append(item)
                        break
            c['is_loaded'] = True
            break
    return state


def initialize_state(settings):
    state = {
        "round": 1, "time": 10, "money": settings['STARTING_MONEY'], "station": "A", "loco_hp": 3,
        "contracts_pool": [c.copy() for c in CONTRACTS], "active_contracts": [], "completed_contracts": [],
        "moves_made_this_round": 0, "events_pool": [e.copy() for e in EVENTS], "current_event": None,
        "game_over": False, "game_over_reason": "", "repaired_this_round": False,
        "settings": settings,
        "modifiers": {"repair_cost_multiplier": 1.0, "move_time_cost": 2, "load_unload_time_cost": 1,
                      "can_take_contracts": True, "revenue_multiplier": 1.0}
    }
    for i in range(1, 6):
        state[f"wagon_{i}_is_purchased"] = i <= 2
        state[f"wagon_{i}_hp"] = 3 if i <= 2 else 0
        state[f"wagon_{i}_contents"] = []
    return state


def perform_action(state, action, **kwargs):
    if state['game_over']: return state
    new_state = _deepcopy_state(state)

    time_cost_move = new_state['modifiers']['move_time_cost']
    time_cost_load = new_state['modifiers']['load_unload_time_cost']

    if action == "move" and new_state['moves_made_this_round'] < 2 and new_state['time'] >= time_cost_move:
        new_state['station'] = "A" if new_state['station'] == "B" else "B"
        new_state['time'] -= time_cost_move
        new_state['moves_made_this_round'] += 1

    elif action == "load_contract" and new_state['time'] >= time_cost_load:
        new_state = _load_goods(new_state, kwargs['contract_id'])
        new_state['time'] -= time_cost_load

    elif action == "unload_contract" and new_state['time'] >= time_cost_load:
        contract_id = kwargs['contract_id']
        price = 0
        contract_to_remove = next((c for c in new_state['active_contracts'] if c['id'] == contract_id), None)
        if contract_to_remove:
            for i in range(1, 6):
                if new_state[f"wagon_{i}_is_purchased"]:
                    new_state[f"wagon_{i}_contents"] = [item for item in new_state[f"wagon_{i}_contents"] if
                                                        item['contract_id'] != contract_id]

            # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
            price = calculate_current_price(contract_to_remove, new_state)  # Передаем new_state
            # --- КОНЕЦ ИСПРАВЛЕНИЯ ---

            new_state['completed_contracts'].append(contract_to_remove)
            new_state['active_contracts'].remove(contract_to_remove)
        revenue = int(price * new_state['modifiers']["revenue_multiplier"])
        new_state['money'] += revenue
        new_state['time'] -= time_cost_load

    elif action == "buy_wagon":
        wagon_index = kwargs['wagon_index']
        price = new_state['settings']['WAGON_PRICES'][wagon_index]
        new_state['money'] -= price
        new_state[f"wagon_{wagon_index}_is_purchased"] = True
        new_state[f"wagon_{wagon_index}_hp"] = 3

    elif action == "repair_loco" or action == "repair_wagon":
        if not new_state['repaired_this_round']:
            if new_state['time'] >= 1:
                new_state['time'] -= 1;
                new_state['repaired_this_round'] = True
            else:
                return new_state
        if action == "repair_loco":
            cost = int(new_state['settings']['REPAIR_LOCO'] * new_state['modifiers']['repair_cost_multiplier'])
            new_state['money'] -= cost;
            new_state['loco_hp'] = 3
        else:
            wagon_index = kwargs['wagon_index']
            cost = int(new_state['settings']['REPAIR_WAGON'] * new_state['modifiers']['repair_cost_multiplier'])
            new_state['money'] -= cost;
            new_state[f"wagon_{wagon_index}_hp"] = 3

    elif action == "take_contract":
        ctype = kwargs['ctype']
        contract_pool = [c for c in new_state['contracts_pool'] if c['id'].startswith(ctype)]
        if contract_pool and len(new_state['active_contracts']) < 4:
            chosen_contract_orig = random.choice(contract_pool)
            chosen_contract = chosen_contract_orig.copy()
            chosen_contract['is_loaded'], chosen_contract['rounds_left'] = False, chosen_contract['max_rounds']
            new_state['active_contracts'].append(chosen_contract)
            new_state['contracts_pool'] = [c for c in new_state['contracts_pool'] if
                                           c['id'] != chosen_contract_orig['id']]

    elif action == "end_round":
        new_state['round'] += 1;
        new_state['time'] = 10;
        new_state['moves_made_this_round'] = 0;
        new_state['repaired_this_round'] = False
        new_state['modifiers'] = {"repair_cost_multiplier": 1.0, "move_time_cost": 2, "load_unload_time_cost": 1,
                                  "can_take_contracts": True, "revenue_multiplier": 1.0}
        if not new_state['events_pool']: new_state['events_pool'] = [e.copy() for e in EVENTS]
        event_index = random.randrange(len(new_state['events_pool']));
        new_event = new_state['events_pool'].pop(event_index)
        new_state['current_event'] = new_event
        apply_event_effect(new_state, new_event)
        if new_state['game_over']: return new_state
        for c in new_state['active_contracts']: c['rounds_left'] -= 1
        if random.randint(1, 6) == 1 and new_state['loco_hp'] > 0:
            new_state['loco_hp'] -= 1
            if new_state['loco_hp'] <= 0: new_state['game_over'], new_state[
                'game_over_reason'] = True, "Износ локомотива."; return new_state
        for i in range(1, 6):
            if new_state[f"wagon_{i}_is_purchased"] and new_state[f"wagon_{i}_hp"] > 0 and random.randint(1, 6) == 1:
                new_state[f"wagon_{i}_hp"] -= 1
                if new_state[f"wagon_{i}_hp"] <= 0: new_state[f"wagon_{i}_is_purchased"], new_state[
                    f"wagon_{i}_contents"] = False, []

    if new_state['time'] <= 0 and new_state['station'] == "B":
        new_state['game_over'], new_state['game_over_reason'] = True, "Время истекло на станции Б."

    return new_state