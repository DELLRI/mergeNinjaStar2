import json
import os

CONFIG_FILE = "artifact_data.json"

DEFAULT_CATEGORIES = [
    {"name": "던전 도전 횟수", "artifact_name": "마계의 바지 (던전)", "coef": 10, "default_daily": 15, "out_idx": 1},
    {"name": "드래곤 도전 횟수", "artifact_name": "드래곤 팔찌 (드래곤)", "coef": 10, "default_daily": 15, "out_idx": 2},
    {"name": "철광석 광산 입장 횟수", "artifact_name": "광산 곡괭이 (철광석 광산)", "coef": 10, "default_daily": 15, "out_idx": 5},
    {"name": "총력전 입장 횟수", "artifact_name": "해골 머리 (노멀 총력전)", "coef": 20, "default_daily": 15, "out_idx": 6},
    {"name": "하드 총력전 입장 횟수", "artifact_name": "마왕의 보주 (하드 총력전)", "coef": 14, "default_daily": 11, "out_idx": 8},
    {"name": "시간의방 입장 횟수", "artifact_name": "모래시계 (시간의방)", "coef": 10, "default_daily": 13, "out_idx": 7},
    {"name": "수중전 입장 횟수", "artifact_name": "수중 어뢰 (수중전)", "coef": 10, "default_daily": 15, "out_idx": 4},
    {"name": "추격전 입장 횟수", "artifact_name": "추격의 방패 (추격전)", "coef": 10, "default_daily": 15, "out_idx": 3},
    {"name": "별빛극장 입장 횟수", "artifact_name": "별빛 트럼펫 (별빛극장)", "coef": 2, "default_daily": 15, "out_idx": 9},
    {"name": "환영누각 입장 횟수", "artifact_name": "환영의 가위 (환영누각)", "coef": 2, "default_daily": 3, "out_idx": 10}
]

# ⭐ 입장 횟수와 레벨을 완벽히 분리한 최종 공식
DEFAULT_FORMULAS = {
    "efficiency": "entry_count / (coef * 10000.0)",
    "atk_pct": "rec_level * efficiency",
    "cost": "2500 * rec_level * (rec_level + 1)"
}

TEST_ENTRIES = {
    "던전 도전 횟수_입력": 7108,
    "드래곤 도전 횟수_입력": 7013,
    "철광석 광산 입장 횟수_입력": 5901,
    "총력전 입장 횟수_입력": 11610,
    "하드 총력전 입장 횟수_입력": 8377,
    "시간의방 입장 횟수_입력": 5051,
    "수중전 입장 횟수_입력": 5858,
    "추격전 입장 횟수_입력": 6773,
    "별빛극장 입장 횟수_입력": 600,
    "환영누각 입장 횟수_입력": 226,
    "다이아": 238560
}

def save_data(input_data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(input_data, f, indent=4, ensure_ascii=False)

def load_data():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "categories" not in data:
                    data["categories"] = DEFAULT_CATEGORIES
                if "formulas" not in data:
                    data["formulas"] = DEFAULT_FORMULAS
                return data
        except:
            pass
    return {"categories": DEFAULT_CATEGORIES, "formulas": DEFAULT_FORMULAS}

def reset_to_test_data():
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
        except Exception as e:
            print(f"JSON 파일 물리 삭제 오류: {e}")

    data = {
        "categories": DEFAULT_CATEGORIES,
        "formulas": DEFAULT_FORMULAS,
        "results": []
    }
    for key, val in TEST_ENTRIES.items():
        data[key] = val

    save_data(data)
    return data