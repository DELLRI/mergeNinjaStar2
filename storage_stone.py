import json
import os

CONFIG_FILE = "stone_data.json"

DEFAULT_CATEGORIES = [
    {"name": "라스트", "coef": 0.0008},
    {"name": "던전", "coef": 0.0002},
    {"name": "드래곤", "coef": 0.0001},
    {"name": "에어", "coef": 0.0002},
    {"name": "추격", "coef": 0.0002},
    {"name": "아쿠아", "coef": 0.0003},
    {"name": "악몽의 탑", "coef": 0.0005},
    {"name": "블랙 드래곤", "coef": 0.0002},
    {"name": "크리스탈 드래곤", "coef": 0.0005},
    {"name": "별빛극장 스톤", "coef": 0.0004}
]

DEFAULT_FORMULAS = {
    "atk_pct": "rec_level * max_stage * coef",
    "cost_logic": "step_cost" # 복잡한 로직은 로직 파일에서 처리
}

def save_data(input_data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(input_data, f, indent=4, ensure_ascii=False)

def load_data():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "categories" not in data: data["categories"] = DEFAULT_CATEGORIES
                if "formulas" not in data: data["formulas"] = DEFAULT_FORMULAS
                return data
        except:
            pass
    return {"categories": DEFAULT_CATEGORIES, "formulas": DEFAULT_FORMULAS}