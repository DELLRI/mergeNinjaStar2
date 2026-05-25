def get_cost_for_level(level):
    """L레벨까지 찍는 데 필요한 총 스톤 누적합을 계산합니다."""
    total_cost = 0
    current_level_cost = 100
    increment = 10

    for l in range(1, level + 1):
        # 10레벨마다 증가분(increment)이 10씩 커짐
        if l > 1 and (l - 1) % 10 == 0:
            increment += 10

        total_cost += current_level_cost
        current_level_cost += increment
    return total_cost

def calculate_stones(max_stages, owned_stones, categories, formulas, saved_levels):
    results = []
    stone_states = []

    for item in categories:
        name = item["name"]
        coef = item["coef"]
        stage = max_stages.get(name, 0)
        base_level = saved_levels.get(name, 0)

        stone_states.append({
            "name": name, "coef": coef, "stage": stage, "level": base_level
        })

    current_stones = owned_stones

    while True:
        best_stone = None
        best_score = -1
        best_cost_req = 0

        for state in stone_states:
            # 다음 레벨을 찍기 위한 한계 비용 계산
            cost_curr = get_cost_for_level(state["level"])
            cost_next = get_cost_for_level(state["level"] + 1)
            marginal_cost = cost_next - cost_curr

            if marginal_cost <= current_stones:
                # 효율 = (계수 * 최고단계) / 비용
                score = (state["coef"] * state["stage"]) / marginal_cost
                if score > best_score:
                    best_score = score
                    best_stone = state
                    best_cost_req = marginal_cost

        if best_stone is None: break
        current_stones -= best_cost_req
        best_stone["level"] += 1

    for state in stone_states:
        final_level = state["level"]
        final_atk = final_level * state["stage"] * state["coef"]
        base_cost = get_cost_for_level(saved_levels.get(state["name"], 0))
        final_cost = get_cost_for_level(final_level)

        results.append({
            "name": state["name"],
            "rec_level": final_level,
            "atk_pct": round(final_atk, 4),
            "stone_cost": int(final_cost - base_cost)
        })
    return results