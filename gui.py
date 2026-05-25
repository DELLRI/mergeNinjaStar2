import tkinter as tk
from tkinter import messagebox, simpledialog
import logic
import storage

class ArtifactCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("고급 유물 계산기 ")
        self.root.geometry("850x850")
        self.root.resizable(True, True)

        self.entry_vars = {}
        self.daily_vars = {}
        self.diamond_var = tk.StringVar(value="0")
        self.categories = []
        self.formulas = {}

        self.saved_data = {}
        self.current_results = {}
        self.level_vars = {}
        self.result_ui = {}
        self.is_applying = False

        # ⭐ [핵심] 유물별로 확정(저장)된 레벨을 보관합니다.
        self.saved_levels = {}

        self.setup_ui()
        self.load_initial_data()

        self.render_input_zone()
        self.render_output_zone()
        self.display_saved_results()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        tk.Label(self.root, text="고급 유물 계산기", font=("Arial", 20, "bold"), anchor="w").pack(fill="x", padx=10, pady=10)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10)

        self.left_frame = tk.Frame(main_frame)
        self.left_frame.pack(side="left", fill="y", padx=(0, 20))

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="y")

        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(anchor="w", pady=(10, 10))
        tk.Button(btn_frame, text="출석체크", font=("Arial", 12, "bold"), command=self.on_attendance, width=10).pack(side="left", padx=(0, 10))
        tk.Label(btn_frame, text="'출석체크'를 누르시면\n일일입장 횟수만큼\n입장횟수가 증가합니다.", justify="left", bg="#FFF2CC", relief="solid", borderwidth=1, padx=10, pady=5).pack(side="left")

        info_text = "※ 하단 표의 '추천레벨'은 직접 수정 가능합니다.\n\n노란 배경색의 수치만 변경해주세요.\n'입장 횟수'와 '다이아'를 입력 후\n'계산'을 누르세요."
        tk.Label(right_frame, text=info_text, justify="left", bg="#FFF2CC", relief="solid", borderwidth=1, padx=10, pady=15).pack(anchor="w", fill="x", pady=5)

        tk.Button(right_frame, text="최적화 계산 🚀", font=("Arial", 14, "bold"), bg="#EAEAEA", command=self.on_calculate, width=15).pack(pady=5)

        tk.Button(right_frame, text="결과 적용 💾", font=("Arial", 14, "bold"), bg="#D4EDDA", command=self.on_apply_result, width=15).pack(pady=5)

        manage_frame = tk.LabelFrame(right_frame, text="항목 관리", font=("Arial", 10, "bold"), padx=10, pady=10)
        manage_frame.pack(anchor="w", fill="x", pady=15)
        tk.Button(manage_frame, text="항목 추가 (+)", bg="#D4EDDA", command=self.add_category, width=10).pack(side="left", padx=5)
        tk.Button(manage_frame, text="항목 삭제 (-)", bg="#F8D7DA", command=self.delete_category, width=10).pack(side="left", padx=5)

        tk.Button(manage_frame, text="초기화/테스트 불러오기 🔄", bg="#FFF3CD", command=self.reset_data_to_test, width=22).pack(side="left", padx=10)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(fill="both", expand=True, padx=10, pady=20)

        self.summary_frame = tk.Frame(self.bottom_frame)
        self.summary_frame.pack(fill="x", pady=(0, 10))

        self.lbl_total_cost = tk.Label(self.summary_frame, text="총 소모 다이아: 0 💎", font=("Arial", 12, "bold"), fg="#D32F2F")
        self.lbl_total_cost.pack(side="left", padx=10)

        self.lbl_remain_dia = tk.Label(self.summary_frame, text="계산 후 잔여 다이아: 0 💎", font=("Arial", 12, "bold"), fg="#1976D2")
        self.lbl_remain_dia.pack(side="left", padx=10)

        self.table_frame = tk.Frame(self.bottom_frame)
        self.table_frame.pack(fill="both", expand=True)

    def bind_focus_events(self, widget, var):
        widget.last_valid_value = var.get()

        def on_focus_in(event):
            current = var.get().strip()
            if current:
                widget.last_valid_value = current
            var.set("")

        def on_focus_out(event):
            val = var.get().strip().replace(",", "")
            if not val or not val.isdigit() or val == "0":
                restore_val = widget.last_valid_value if widget.last_valid_value else "0"
                var.set(restore_val)
            else:
                formatted = f"{int(val):,}"
                var.set(formatted)
                widget.last_valid_value = formatted

        def on_enter(event):
            self.root.focus_set()

        widget.bind("<FocusIn>", on_focus_in)
        widget.bind("<FocusOut>", on_focus_out)
        widget.bind("<Return>", on_enter)
        widget.bind("<KP_Enter>", on_enter)

    def render_input_zone(self):
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        tk.Label(self.left_frame, text="콘텐츠명", width=25, relief="solid", borderwidth=1, bg="#EAEAEA").grid(row=0, column=0, sticky="nsew")
        tk.Label(self.left_frame, text="※ 입장횟수 입력", bg="yellow", fg="red", relief="solid", borderwidth=1).grid(row=0, column=1, sticky="nsew")
        tk.Label(self.left_frame, text="※ 일일입장 횟수", bg="yellow", fg="red", relief="solid", borderwidth=1).grid(row=0, column=2, sticky="nsew")

        for i, item in enumerate(self.categories):
            cat = item["name"]
            row = i + 1
            default_daily = item.get("default_daily", 0)

            if cat not in self.entry_vars: self.entry_vars[cat] = tk.StringVar(value="0")
            if cat not in self.daily_vars: self.daily_vars[cat] = tk.StringVar(value=str(default_daily))

            tk.Label(self.left_frame, text=cat, fg="black", anchor="w", relief="solid", borderwidth=1).grid(row=row, column=0, sticky="nsew", ipadx=5)

            e_entry = tk.Entry(self.left_frame, textvariable=self.entry_vars[cat], bg="#FFF2CC", justify="right", relief="solid", borderwidth=1)
            e_entry.grid(row=row, column=1, sticky="nsew")
            self.bind_focus_events(e_entry, self.entry_vars[cat])

            d_entry = tk.Entry(self.left_frame, textvariable=self.daily_vars[cat], bg="#FFF2CC", justify="right", relief="solid", borderwidth=1)
            d_entry.grid(row=row, column=2, sticky="nsew")
            self.bind_focus_events(d_entry, self.daily_vars[cat])

        last_row = len(self.categories) + 1
        tk.Label(self.left_frame, text="보유 다이아 💎", anchor="w", relief="solid", borderwidth=1, bg="#EAEAEA").grid(row=last_row, column=0, sticky="nsew", ipadx=5)

        dia_entry = tk.Entry(self.left_frame, textvariable=self.diamond_var, bg="#FFF2CC", justify="right", relief="solid", borderwidth=1)
        dia_entry.grid(row=last_row, column=1, columnspan=2, sticky="nsew")
        self.bind_focus_events(dia_entry, self.diamond_var)

        self.diamond_var.trace_add("write", lambda *args: self.update_summary_labels())

    def render_output_zone(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["유물", "추천레벨 (수동수정 가능)", "적용 공격력 (%)", "계수", "레벨당효율"]
        for col, h in enumerate(headers):
            tk.Label(self.table_frame, text=h, bg="#EAEAEA", relief="solid", borderwidth=1).grid(row=0, column=col, sticky="nsew", ipadx=10, ipady=2)
            self.table_frame.grid_columnconfigure(col, weight=1)

        self.result_ui = {}
        sorted_categories = sorted(self.categories, key=lambda x: x.get("out_idx", 999))

        for i, item in enumerate(sorted_categories):
            cat = item["name"]
            art_name = item.get("artifact_name", cat)
            row = i + 1

            name_lbl = tk.Label(self.table_frame, text=art_name, relief="solid", borderwidth=1, bg="white")
            name_lbl.grid(row=row, column=0, sticky="nsew")

            if cat not in self.level_vars:
                self.level_vars[cat] = tk.StringVar(value="0")

            lvl_entry = tk.Entry(self.table_frame, textvariable=self.level_vars[cat], justify="center", font=("Arial", 10, "bold"), relief="solid", borderwidth=1, bg="#FFF2CC")
            lvl_entry.grid(row=row, column=1, sticky="nsew")
            self.bind_focus_events(lvl_entry, self.level_vars[cat])

            def on_level_edit(*args, c=cat):
                self.recalc_atk_for_manual_level(c)
            self.level_vars[cat].trace_add("write", on_level_edit)

            atk_lbl = tk.Label(self.table_frame, text="0.0000", relief="solid", borderwidth=1, bg="white")
            atk_lbl.grid(row=row, column=2, sticky="nsew")

            coef_lbl = tk.Label(self.table_frame, text="0", relief="solid", borderwidth=1, bg="white")
            coef_lbl.grid(row=row, column=3, sticky="nsew")

            eff_lbl = tk.Label(self.table_frame, text="0.0000", relief="solid", borderwidth=1, bg="white")
            eff_lbl.grid(row=row, column=4, sticky="nsew")

            self.result_ui[cat] = {
                "level_var": self.level_vars[cat],
                "atk_lbl": atk_lbl,
                "coef_lbl": coef_lbl,
                "eff_lbl": eff_lbl
            }

    def update_summary_labels(self):
        if self.is_applying: return

        total_cost = sum(data.get("dia_cost", 0) for data in self.current_results.values())
        current_dia = self.get_int_value(self.diamond_var)
        remain_dia = current_dia - total_cost

        self.lbl_total_cost.config(text=f"총 소모 다이아: {int(total_cost):,} 💎")
        self.lbl_remain_dia.config(text=f"계산 후 잔여 다이아: {int(remain_dia):,} 💎")

        if remain_dia < 0:
            self.lbl_remain_dia.config(fg="red")
        else:
            self.lbl_remain_dia.config(fg="#1976D2")

    def on_apply_result(self):
        total_cost = sum(data.get("dia_cost", 0) for data in self.current_results.values())
        current_dia = self.get_int_value(self.diamond_var)
        remain_dia = current_dia - total_cost

        if total_cost == 0:
            messagebox.showinfo("안내", "소모된 다이아가 없거나 이미 적용된 상태입니다.")
            return

        if remain_dia < 0:
            messagebox.showwarning("경고", "잔여 다이아가 부족하여 결과를 적용할 수 없습니다.")
            return

        confirm_msg = f"총 {total_cost:,} 💎을 소모하여 유물 레벨을 인게임에 확정하시겠습니까?\n\n- 다이아가 {remain_dia:,} 💎으로 차감됩니다.\n- 달성한 추천레벨이 저장되어 다음 레벨업의 기반이 됩니다."

        if messagebox.askyesno("결과 적용 확정", confirm_msg):
            self.is_applying = True

            self.diamond_var.set(f"{int(remain_dia):,}")

            # ⭐ 입장 횟수는 절대로 건드리지 않고, 도달한 "추천레벨" 숫자만 저장합니다!
            for item in self.categories:
                cat = item["name"]
                if cat in self.current_results:
                    dia_spent = self.current_results[cat].get("dia_cost", 0)
                    if dia_spent > 0:
                        self.saved_levels[cat] = self.current_results[cat]["rec_level"]

                    self.current_results[cat]["dia_cost"] = 0

            self.lbl_total_cost.config(text="총 소모 다이아: 0 💎")
            self.lbl_remain_dia.config(text=f"계산 후 잔여 다이아: {int(remain_dia):,} 💎")
            self.lbl_remain_dia.config(fg="#1976D2")

            self.save_current_data()

            self.is_applying = False
            messagebox.showinfo("성공", "추천레벨이 확정되었습니다!\n입력창의 '입장 횟수'나 '효율'은 전혀 변하지 않으며 완벽한 정확도를 유지합니다.")

    def recalc_atk_for_manual_level(self, cat):
        if cat not in self.current_results:
            return
        try:
            val_str = self.level_vars[cat].get().strip().replace(",", "")
            new_level = int(val_str) if val_str else 0

            context = {
                "entry_count": self.get_int_value(self.entry_vars[cat]),
                "coef": self.current_results[cat]["coef"],
                "efficiency": self.current_results[cat]["efficiency"],
                "int": int, "round": round
            }

            # 수동 입력 시, 해당 레벨로 공격력 계산
            context["rec_level"] = new_level
            new_atk = eval(self.formulas.get("atk_pct"), {"__builtins__": None}, context)

            # 저장된 레벨과 비교하여 다이아 차액 계산
            base_level = self.saved_levels.get(cat, 0)
            context["rec_level"] = base_level
            base_cost = eval(self.formulas.get("cost"), {"__builtins__": None}, context)

            context["rec_level"] = new_level
            new_cost = eval(self.formulas.get("cost"), {"__builtins__": None}, context)

            new_dia_cost = max(0, new_cost - base_cost)

            self.current_results[cat]["rec_level"] = new_level
            self.current_results[cat]["atk_pct"] = new_atk
            self.current_results[cat]["cost"] = new_cost
            self.current_results[cat]["dia_cost"] = new_dia_cost
            self.result_ui[cat]["atk_lbl"].config(text=f"{new_atk:.4f}")

            self.update_summary_labels()
        except:
            pass

    def get_int_value(self, str_var):
        val = str_var.get().strip().replace(",", "")
        return int(val) if val.isdigit() else 0

    def load_initial_data(self):
        self.saved_data = storage.load_data()
        self.categories = self.saved_data.get("categories", [])
        self.formulas = self.saved_data.get("formulas", storage.DEFAULT_FORMULAS)

        for item in self.categories:
            cat = item["name"]
            default_daily = item.get("default_daily", 0)

            # ⭐ 저장된 레벨(Base 레벨)을 불러옵니다.
            self.saved_levels[cat] = self.saved_data.get(f"{cat}_저장레벨", 0)

            if cat not in self.entry_vars: self.entry_vars[cat] = tk.StringVar(value="0")
            if cat not in self.daily_vars: self.daily_vars[cat] = tk.StringVar(value=str(default_daily))

            if f"{cat}_입력" in self.saved_data:
                self.entry_vars[cat].set(f"{self.saved_data[f'{cat}_입력']:,}")
            if f"{cat}_일일" in self.saved_data:
                self.daily_vars[cat].set(f"{self.saved_data[f'{cat}_일일']:,}")
        if "다이아" in self.saved_data:
            self.diamond_var.set(f"{self.saved_data['다이아']:,}")

    def sync_ui_from_current_results(self):
        for cat, data in self.current_results.items():
            if cat in self.result_ui:
                self.result_ui[cat]["level_var"].set(f"{data['rec_level']:,}")
                self.result_ui[cat]["atk_lbl"].config(text=f"{data['atk_pct']:.4f}")
                self.result_ui[cat]["coef_lbl"].config(text=data["coef"])
                self.result_ui[cat]["eff_lbl"].config(text=f"{data['efficiency']:.4f}")
        self.update_summary_labels()

    def display_saved_results(self):
        results = self.saved_data.get("results", [])
        if results and len(results) == len(self.categories) and "dia_cost" in results[0]:
            for res in results:
                self.current_results[res["name"]] = res
            self.sync_ui_from_current_results()
        else:
            self.on_calculate()

    def save_current_data(self):
        saved_results_list = [self.current_results[item["name"]] for item in self.categories if item["name"] in self.current_results]

        data = {
            "categories": self.categories,
            "formulas": self.formulas,
            "다이아": self.get_int_value(self.diamond_var),
            "results": saved_results_list
        }
        for item in self.categories:
            cat = item["name"]
            data[f"{cat}_입력"] = self.get_int_value(self.entry_vars[cat])
            data[f"{cat}_일일"] = self.get_int_value(self.daily_vars[cat])
            # ⭐ 저장된 레벨을 JSON 파일에 기록합니다.
            data[f"{cat}_저장레벨"] = self.saved_levels.get(cat, 0)

        storage.save_data(data)

    def reset_data_to_test(self):
        if messagebox.askyesno("초기화 확인", "기존 저장된 JSON 파일과 커스텀 공식이 디스크에서 완전히 제거되고,\n테스트용 클린 데이터로 리셋됩니다. 진행하시겠습니까?"):
            storage.reset_to_test_data()

            self.entry_vars.clear()
            self.daily_vars.clear()
            self.level_vars.clear()
            self.current_results.clear()
            self.saved_levels.clear() # 저장 레벨도 완벽하게 클리어

            self.load_initial_data()
            self.render_input_zone()
            self.render_output_zone()
            self.on_calculate()
            messagebox.showinfo("성공", "JSON 파일을 깨끗하게 재생성하고 테스트 데이터 초기화를 완료했습니다!")

    def add_category(self):
        name = simpledialog.askstring("항목 추가", "추가할 신규 콘텐츠(왼쪽 위 입력창 이름)를 입력하세요:")
        if not name: return
        if any(item["name"] == name for item in self.categories):
            messagebox.showwarning("경고", "이미 존재하는 항목 이름입니다.")
            return

        art_name = simpledialog.askstring("유물 이름", f"'{name}'의 하단 표 유물 이름을 입력하세요:\n(빈칸으로 두시면 콘텐츠명과 똑같이 표시됩니다)")
        if not art_name: art_name = name

        coef_str = simpledialog.askstring("계수 입력", f"'{name}' 항목의 계수를 입력하세요 (숫자만):")
        coef = int(coef_str) if (coef_str and coef_str.isdigit()) else 10

        out_idx = len(self.categories) + 1
        self.categories.append({"name": name, "artifact_name": art_name, "coef": coef, "default_daily": 0, "out_idx": out_idx})
        self.entry_vars[name] = tk.StringVar(value="0")
        self.daily_vars[name] = tk.StringVar(value="0")
        self.level_vars[name] = tk.StringVar(value="0")
        self.saved_levels[name] = 0

        self.render_input_zone()
        self.render_output_zone()
        self.on_calculate()
        messagebox.showinfo("성공", f"'{name}' 항목이 추가되었습니다.")

    def delete_category(self):
        if not self.categories: return

        pop = tk.Toplevel(self.root)
        pop.title("항목 삭제 선택")
        pop.geometry("300x400")
        pop.grab_set()

        tk.Label(pop, text="삭제할 항목을 선택하고\n아래 삭제 버튼을 눌러주세요.", justify="center").pack(pady=10)
        listbox = tk.Listbox(pop, selectmode="single", font=("Arial", 10))
        listbox.pack(fill="both", expand=True, padx=20, pady=5)

        for item in self.categories:
            listbox.insert(tk.END, item["name"])

        def do_delete():
            selected = listbox.curselection()
            if not selected: return

            idx = selected[0]
            target_item = self.categories[idx]

            if messagebox.askyesno("삭제 확인", f"'{target_item['name']}'을(를) 삭제하시겠습니까?", parent=pop):
                name = target_item["name"]
                self.categories.pop(idx)
                if name in self.entry_vars: del self.entry_vars[name]
                if name in self.daily_vars: del self.daily_vars[name]
                if name in self.level_vars: del self.level_vars[name]
                if name in self.current_results: del self.current_results[name]
                if name in self.saved_levels: del self.saved_levels[name]

                self.render_input_zone()
                self.render_output_zone()
                self.on_calculate()
                pop.destroy()

        tk.Button(pop, text="선택 항목 삭제", command=do_delete, bg="#DC3545", fg="white", font=("Arial", 11, "bold"), pady=5).pack(fill="x", padx=20, pady=15)

    def on_attendance(self):
        entries = {item["name"]: self.get_int_value(self.entry_vars[item["name"]]) for item in self.categories}
        dailies = {item["name"]: self.get_int_value(self.daily_vars[item["name"]]) for item in self.categories}

        updated = logic.do_attendance(entries, dailies)
        for item in self.categories:
            cat = item["name"]
            self.entry_vars[cat].set(f"{updated[cat]:,}")

        self.on_calculate()
        messagebox.showinfo("완료", "출석체크 완료! 입장 횟수와 유물 정보가 갱신되었습니다.")

    def on_calculate(self):
        entries = {item["name"]: self.get_int_value(self.entry_vars[item["name"]]) for item in self.categories}
        diamonds = self.get_int_value(self.diamond_var)

        results = logic.calculate_artifacts(entries, diamonds, self.categories, self.formulas, self.saved_levels)

        for res in results:
            self.current_results[res["name"]] = res

        self.sync_ui_from_current_results()
        self.save_current_data()

    def on_closing(self):
        try:
            self.root.focus_set()
            self.save_current_data()
        except Exception as e:
            print(f"자동 저장 중 오류 발생: {e}")
        finally:
            self.root.destroy()