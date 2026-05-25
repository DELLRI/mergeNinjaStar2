def do_attendance(entries, dailies):
    updated = {}
    for key in entries:
        updated[key] = entries[key] + dailies.get(key, 0)
    return updated

def calculate_artifacts(entries, diamonds, categories, formulas, saved_levels):
    results = []
    artifact_states = []

    # 1. 초기 세팅 (효율 계산 및 현재 저장된 '기본 레벨' 장착)
    for item in categories:
        cat_name = item["name"]
        coef = item["coef"]
        entry_count = entries.get(cat_name, 0)
        base_level = saved_levels.get(cat_name, 0) # ⭐ 입장 횟수가 아닌 순수 저장된 레벨을 불러옵니다!

        context = {
            "entry_count": entry_count,
            "coef": coef,
            "int": int,
            "round": round
        }

        # 효율은 오직 순수 입장 횟수로만 계산됩니다.
        try: efficiency = eval(formulas.get("efficiency", "0"), {"__builtins__": None}, context)
        except: efficiency = 0
        context["efficiency"] = efficiency

        artifact_states.append({
            "name": cat_name,
            "coef": coef,
            "efficiency": efficiency,
            "level": base_level,
            "context": context
        })

    # 2. 다이아 최적화 분배
    current_diamonds = diamonds

    while True:
        best_artifact = None
        best_score = -1
        best_dia_req = 0

        for state in artifact_states:
            current_level = state["level"]
            next_level = current_level + 1

            state["context"]["rec_level"] = current_level
            try: cost_curr = eval(formulas.get("cost", "0"), {"__builtins__": None}, state["context"])
            except: cost_curr = 0

            state["context"]["rec_level"] = next_level
            try: cost_next = eval(formulas.get("cost", "0"), {"__builtins__": None}, state["context"])
            except: cost_next = 0

            # 다음 1레벨업에 필요한 다이아
            marginal_dia_cost = max(0, cost_next - cost_curr)

            if marginal_dia_cost <= current_diamonds and marginal_dia_cost > 0:
                # 1레벨 오를 때 오르는 공격력(효율값 그 자체)을 다이아로 나눈 가성비 점수
                score = state["efficiency"] / marginal_dia_cost

                if score > best_score:
                    best_score = score
                    best_artifact = state
                    best_dia_req = marginal_dia_cost

        if best_artifact is None:
            break

        current_diamonds -= best_dia_req
        best_artifact["level"] += 1

    # 3. 결과 정리
    for state in artifact_states:
        final_level = state["level"]
        state["context"]["rec_level"] = final_level

        try: final_atk = eval(formulas.get("atk_pct", "0"), {"__builtins__": None}, state["context"])
        except: final_atk = 0

        # 이번 '계산 버튼'을 통해 순수하게 추가로 소모된 다이아량 추적
        base_level = saved_levels.get(state["name"], 0)
        state["context"]["rec_level"] = base_level
        try: base_cost = eval(formulas.get("cost", "0"), {"__builtins__": None}, state["context"])
        except: base_cost = 0

        state["context"]["rec_level"] = final_level
        try: final_cost = eval(formulas.get("cost", "0"), {"__builtins__": None}, state["context"])
        except: final_cost = 0

        session_dia_cost = final_cost - base_cost

        results.append({
            "name": state["name"],
            "rec_level": final_level,
            "atk_pct": round(final_atk, 4),
            "coef": state["coef"],
            "efficiency": round(state["efficiency"], 4),
            "dia_cost": int(session_dia_cost)
        })

    return results