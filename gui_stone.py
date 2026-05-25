import tkinter as tk
from tkinter import messagebox, simpledialog
import logic_stone
import storage_stone

class StoneCalculatorTab:
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root

        self.stage_vars = {}
        self.stone_var = tk.StringVar(value="0")
        self.categories = []
        self.formulas = {}

        self.saved_data = {}
        self.current_results = {}
        self.level_vars = {}
        self.result_ui = {}
        self.is_applying = False
        self.saved_levels = {}

        self.setup_ui()
        self.load_initial_data()

        self.render_output_zone()
        self.display_saved_results()

    def setup_ui(self):
        # 상단 입력부
        top_frame = tk.Frame(self.parent, bg="#E9ECEF")
        top_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(top_frame, text="보유 스톤 🔮", font=("Arial", 14, "bold"), bg="#E9ECEF").pack(side="left", padx=5)
        stone_entry = tk.Entry(top_frame, textvariable=self.stone_var, font=("Arial", 14), justify="right", width=15, relief="solid", borderwidth=1, bg="#FFF2CC")
        stone_entry.pack(side="left", padx=5)
        self.bind_focus_events(stone_entry, self.stone_var)

        tk.Button(top_frame, text="계 산", font=("Arial", 14, "bold"), bg="#EAEAEA", command=self.on_calculate, width=10).pack(side="left", padx=20)
        tk.Button(top_frame, text="결과 적용 💾", font=("Arial", 12, "bold"), bg="#D4EDDA", command=self.on_apply_result).pack(side="left", padx=5)

        # 관리 메뉴
        manage_frame = tk.LabelFrame(self.parent, text="스톤 항목 관리", font=("Arial", 10, "bold"), padx=10, pady=10, bg="#E9ECEF")
        manage_frame.pack(anchor="w", fill="x", padx=10, pady=5)
        tk.Button(manage_frame, text="스톤 추가 (+)", bg="#D4EDDA", command=self.add_category, width=12).pack(side="left", padx=5)
        tk.Button(manage_frame, text="스톤 삭제 (-)", bg="#F8D7DA", command=self.delete_category, width=12).pack(side="left", padx=5)
        # ⭐ 신규 추가된 추천레벨 초기화 버튼
        tk.Button(manage_frame, text="추천레벨 초기화 🔄", bg="#FFF3CD", command=self.reset_recommend_levels, width=16).pack(side="left", padx=20)
        # 요약 정보
        self.summary_frame = tk.Frame(self.parent, bg="#E9ECEF")
        self.summary_frame.pack(fill="x", padx=10, pady=5)
        self.lbl_total_cost = tk.Label(self.summary_frame, text="총 소모 스톤: 0 🔮", font=("Arial", 12, "bold"), fg="#D32F2F", bg="#E9ECEF")
        self.lbl_total_cost.pack(side="left", padx=10)
        self.lbl_remain_stone = tk.Label(self.summary_frame, text="계산 후 잔여 스톤: 0 🔮", font=("Arial", 12, "bold"), fg="#1976D2", bg="#E9ECEF")
        self.lbl_remain_stone.pack(side="left", padx=10)

        # 테이블 영역
        self.table_frame = tk.Frame(self.parent, bg="#E9ECEF")
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.stone_var.trace_add("write", lambda *args: self.update_summary_labels())

    def bind_focus_events(self, widget, var):
        widget.last_valid_value = var.get()
        def on_focus_in(event):
            current = var.get().strip()
            if current: widget.last_valid_value = current
            var.set("")
        def on_focus_out(event):
            val = var.get().strip().replace(",", "")
            if not val or not val.isdigit() or val == "0":
                var.set(widget.last_valid_value if widget.last_valid_value else "0")
            else:
                var.set(f"{int(val):,}")
                widget.last_valid_value = f"{int(val):,}"
        def on_enter(event):
            self.root.focus_set()

        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)
        widget.bind("<Return>", on_enter)
        widget.bind("<KP_Enter>", on_enter)

    def render_output_zone(self):
        for widget in self.table_frame.winfo_children(): widget.destroy()

        # 스크린샷과 동일한 헤더
        headers = ["스톤", "최고 단계", "추천레벨", "적용 공격 증폭 (%)", "계수"]

        tk.Label(self.table_frame, text="※ 최고단계 입력", bg="yellow", fg="red", relief="solid", borderwidth=1, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="nsew")

        for col, h in enumerate(headers):
            tk.Label(self.table_frame, text=h, bg="#EAEAEA", relief="solid", borderwidth=1).grid(row=1, column=col, sticky="nsew", ipadx=10, ipady=5)
            self.table_frame.grid_columnconfigure(col, weight=1)

        self.result_ui = {}

        for i, item in enumerate(self.categories):
            name = item["name"]
            row = i + 2

            if name not in self.stage_vars: self.stage_vars[name] = tk.StringVar(value="0")
            if name not in self.level_vars: self.level_vars[name] = tk.StringVar(value="0")

            tk.Label(self.table_frame, text=name, relief="solid", borderwidth=1, bg="white").grid(row=row, column=0, sticky="nsew")

            # 최고 단계 입력창 (노란색 배경)
            stage_entry = tk.Entry(self.table_frame, textvariable=self.stage_vars[name], justify="center", font=("Arial", 10), relief="solid", borderwidth=1, bg="#FFF2CC")
            stage_entry.grid(row=row, column=1, sticky="nsew")
            self.bind_focus_events(stage_entry, self.stage_vars[name])

            # 추천레벨 (수동 수정 가능)
            lvl_entry = tk.Entry(self.table_frame, textvariable=self.level_vars[name],
                                 justify="center", font=("Arial", 10, "bold"),
                                 relief="solid", borderwidth=1, bg="white") # 배경색을 white로 변경하여 입력 가능함 표시
            lvl_entry.grid(row=row, column=2, sticky="nsew")
            self.bind_focus_events(lvl_entry, self.level_vars[name])

            # 입력값이 변경될 때마다 자동 재계산 실행
            self.level_vars[name].trace_add("write", lambda *args, c=name: self.recalc_atk_for_manual_level(c))

            self.stage_vars[name].trace_add("write", lambda *args, c=name: self.recalc_atk_for_manual_level(c))

            atk_lbl = tk.Label(self.table_frame, text="0.0000", relief="solid", borderwidth=1, bg="white")
            atk_lbl.grid(row=row, column=3, sticky="nsew")

            coef_lbl = tk.Label(self.table_frame, text=str(item["coef"]), relief="solid", borderwidth=1, bg="white")
            coef_lbl.grid(row=row, column=4, sticky="nsew")

            self.result_ui[name] = {"level_var": self.level_vars[name], "atk_lbl": atk_lbl, "coef_lbl": coef_lbl}

    def update_summary_labels(self):
        if self.is_applying: return
        total_cost = sum(data.get("stone_cost", 0) for data in self.current_results.values())
        current_stone = self.get_int_value(self.stone_var)
        remain_stone = current_stone - total_cost

        self.lbl_total_cost.config(text=f"총 소모 스톤: {int(total_cost):,} 🔮")
        self.lbl_remain_stone.config(text=f"계산 후 잔여 스톤: {int(remain_stone):,} 🔮")
        self.lbl_remain_stone.config(fg="red" if remain_stone < 0 else "#1976D2")

    def on_apply_result(self):
        total_cost = sum(data.get("stone_cost", 0) for data in self.current_results.values())
        current_stone = self.get_int_value(self.stone_var)
        remain_stone = current_stone - total_cost

        if total_cost == 0:
            return messagebox.showinfo("안내", "소모된 스톤이 없거나 이미 적용된 상태입니다.")
        if remain_stone < 0:
            return messagebox.showwarning("경고", "잔여 스톤이 부족하여 결과를 적용할 수 없습니다.")

        if messagebox.askyesno("결과 적용 확정", f"총 {total_cost:,} 🔮을 소모하여 레벨을 확정하시겠습니까?\n달성한 추천레벨이 저장됩니다."):
            self.is_applying = True
            self.stone_var.set(f"{int(remain_stone):,}")

            for item in self.categories:
                name = item["name"]
                if name in self.current_results and self.current_results[name].get("stone_cost", 0) > 0:
                    self.saved_levels[name] = self.current_results[name]["rec_level"]
                    self.current_results[name]["stone_cost"] = 0

            self.lbl_total_cost.config(text="총 소모 스톤: 0 🔮")
            self.lbl_remain_stone.config(text=f"계산 후 잔여 스톤: {int(remain_stone):,} 🔮", fg="#1976D2")

            self.save_current_data()
            self.is_applying = False
            messagebox.showinfo("성공", "스톤 추천레벨이 확정되었습니다!")

    def recalc_atk_for_manual_level(self, name):
        # 1. 항목 데이터를 안전하게 가져옵니다. (계산 버튼을 안 눌러도 작동)
        item_data = next((item for item in self.categories if item["name"] == name), None)
        if not item_data: return

        try:
            # 2. 값 가져오기
            val_str = self.level_vars[name].get().strip().replace(",", "")
            new_level = int(val_str) if val_str and val_str.isdigit() else 0

            stage_val = self.get_int_value(self.stage_vars[name])
            coef_val = item_data["coef"]

            # 3. 공격력 재계산
            new_atk = new_level * stage_val * coef_val

            # 4. 비용 계산
            base_level = self.saved_levels.get(name, 0)
            new_cost = logic_stone.get_cost_for_level(new_level)
            base_cost = logic_stone.get_cost_for_level(base_level)

            # 5. 결과 업데이트
            if name not in self.current_results:
                self.current_results[name] = {}

            self.current_results[name]["rec_level"] = new_level
            self.current_results[name]["atk_pct"] = new_atk
            self.current_results[name]["stone_cost"] = max(0, new_cost - base_cost)
            self.current_results[name]["coef"] = coef_val # 로직 연결 유지

            # 6. 화면 반영
            self.result_ui[name]["atk_lbl"].config(text=f"{new_atk:.4f}")
            self.update_summary_labels()

        except Exception as e:
            print(f"수동 계산 오류: {e}")
            pass

    def get_int_value(self, str_var):
        val = str_var.get().strip().replace(",", "")
        return int(val) if val.isdigit() else 0

    def load_initial_data(self):
        self.saved_data = storage_stone.load_data()
        self.categories = self.saved_data.get("categories", [])
        self.formulas = self.saved_data.get("formulas", storage_stone.DEFAULT_FORMULAS)
        self.saved_levels = {}

        for item in self.categories:
            name = item["name"]
            self.saved_levels[name] = self.saved_data.get(f"{name}_저장레벨", 0)
            if name not in self.stage_vars: self.stage_vars[name] = tk.StringVar(value="0")

            if f"{name}_최고단계" in self.saved_data: self.stage_vars[name].set(f"{self.saved_data[f'{name}_최고단계']:,}")
        if "스톤" in self.saved_data: self.stone_var.set(f"{self.saved_data['스톤']:,}")

    def sync_ui_from_current_results(self):
        for name, data in self.current_results.items():
            if name in self.result_ui:
                self.result_ui[name]["level_var"].set(f"{data['rec_level']:,}")
                self.result_ui[name]["atk_lbl"].config(text=f"{data['atk_pct']:.4f}")
        self.update_summary_labels()

    def display_saved_results(self):
        results = self.saved_data.get("results", [])
        if results and len(results) == len(self.categories) and "stone_cost" in results[0]:
            for res in results: self.current_results[res["name"]] = res
            self.sync_ui_from_current_results()
        else:
            self.on_calculate()

    def save_current_data(self):
        saved_results_list = [self.current_results[item["name"]] for item in self.categories if item["name"] in self.current_results]
        data = {
            "categories": self.categories, "formulas": self.formulas,
            "스톤": self.get_int_value(self.stone_var), "results": saved_results_list
        }
        for item in self.categories:
            name = item["name"]
            data[f"{name}_최고단계"] = self.get_int_value(self.stage_vars[name])
            data[f"{name}_저장레벨"] = self.saved_levels.get(name, 0)
        storage_stone.save_data(data)

    def add_category(self):
        name = simpledialog.askstring("항목 추가", "신규 스톤 이름을 입력하세요:")
        if not name: return
        coef_str = simpledialog.askstring("계수 입력", "계수를 입력하세요 (예: 0.0005):")
        try: coef = float(coef_str)
        except: coef = 0.0001

        self.categories.append({"name": name, "coef": coef})
        self.stage_vars[name] = tk.StringVar(value="0")
        self.level_vars[name] = tk.StringVar(value="0")
        self.saved_levels[name] = 0
        self.render_output_zone()
        self.on_calculate()

    def delete_category(self):
        if not self.categories: return
        pop = tk.Toplevel(self.root)
        pop.title("스톤 삭제")
        pop.geometry("300x400")
        pop.grab_set()

        listbox = tk.Listbox(pop, selectmode="single", font=("Arial", 10))
        listbox.pack(fill="both", expand=True, padx=20, pady=20)
        for item in self.categories: listbox.insert(tk.END, item["name"])

        def do_delete():
            if not listbox.curselection(): return
            idx = listbox.curselection()[0]
            if messagebox.askyesno("삭제 확인", "정말 삭제하시겠습니까?", parent=pop):
                name = self.categories.pop(idx)["name"]
                for d in [self.stage_vars, self.level_vars, self.current_results, self.saved_levels]:
                    if name in d: del d[name]
                self.render_output_zone()
                self.on_calculate()
                pop.destroy()
        tk.Button(pop, text="삭제", command=do_delete, bg="#DC3545", fg="white").pack(fill="x", padx=20, pady=15)

    def on_calculate(self):
        stages = {item["name"]: self.get_int_value(self.stage_vars[item["name"]]) for item in self.categories}
        stones = self.get_int_value(self.stone_var)
        results = logic_stone.calculate_stones(stages, stones, self.categories, self.formulas, self.saved_levels)
        for res in results: self.current_results[res["name"]] = res
        self.sync_ui_from_current_results()
        self.save_current_data()



    def reset_recommend_levels(self):
        """추천레벨을 0으로 초기화하고 즉시 파일에 저장합니다."""
        if messagebox.askyesno("초기화 확인", "모든 스톤의 추천레벨을 0으로 초기화하시겠습니까?"):
            for name in self.level_vars:
                # 1. 입력창 값 0으로 세팅
                self.level_vars[name].set("0")

                # 2. 결과 데이터 초기화
                if name in self.current_results:
                    self.current_results[name]["rec_level"] = 0
                    self.current_results[name]["atk_pct"] = 0.0
                    self.current_results[name]["stone_cost"] = 0

                # 3. 로컬 저장 데이터(saved_levels)도 0으로 동기화
                self.saved_levels[name] = 0

                # 4. 화면 UI 갱신
                if name in self.result_ui:
                    self.result_ui[name]["atk_lbl"].config(text="0.0000")

            # 5. 요약 정보 업데이트
            self.update_summary_labels()

            # ⭐ 6. 변경된 데이터를 즉시 JSON 파일에 저장
            self.save_current_data()

            messagebox.showinfo("완료", "추천레벨이 초기화되어 파일에 저장되었습니다.")