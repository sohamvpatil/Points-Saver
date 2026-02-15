import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE = "rummy_data.json"
MAX_POINTS = 151


class RummyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rummy 151 Score Sheet")
        self.root.geometry("430x760")

        self.players = {}
        self.rounds = []
        self.entry_widgets = {}

        self.load_data()
        self.create_ui()
        self.refresh_table()

    # ---------------- UI ---------------- #
    def create_ui(self):

        tk.Label(self.root, text="RUMMY 151 SCORE SHEET",
                 font=("Arial", 12, "bold")).pack(pady=5)

        # Top Controls
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)

        self.player_entry = tk.Entry(top_frame, width=12)
        self.player_entry.pack(side=tk.LEFT, padx=3)

        tk.Button(top_frame, text="Add",
                  command=self.add_player).pack(side=tk.LEFT)

        tk.Button(top_frame, text="Delete",
                  command=self.delete_player).pack(side=tk.LEFT, padx=3)

        tk.Button(top_frame, text="Reset Game",
                  command=self.reset_game).pack(side=tk.LEFT, padx=3)

        tk.Button(top_frame, text="Reset Players",
                  command=self.reset_players).pack(side=tk.LEFT)

        # Round Entry
        self.round_entry_frame = tk.Frame(self.root)
        self.round_entry_frame.pack(pady=5)

        tk.Button(self.root, text="Submit Round",
                  command=self.submit_round).pack(pady=5)

        # Scrollable Table
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container)
        self.v_scroll = tk.Scrollbar(container,
                                      orient="vertical",
                                      command=self.canvas.yview)
        self.h_scroll = tk.Scrollbar(container,
                                      orient="horizontal",
                                      command=self.canvas.xview)

        self.table_frame = tk.Frame(self.canvas)

        self.table_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0),
                                  window=self.table_frame,
                                  anchor="nw")

        self.canvas.configure(yscrollcommand=self.v_scroll.set,
                              xscrollcommand=self.h_scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")

    # ---------------- Add Player ---------------- #
    def add_player(self):
        name = self.player_entry.get().strip()
        if name and name not in self.players:
            self.players[name] = {"total": 0, "status": "ACTIVE"}
            self.player_entry.delete(0, tk.END)
            self.save_data()
            self.refresh_table()
        else:
            messagebox.showwarning("Error", "Invalid or duplicate name")

    # ---------------- Delete Player ---------------- #
    def delete_player(self):
        name = self.player_entry.get().strip()

        if name not in self.players:
            messagebox.showwarning("Error", "Player not found")
            return

        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Delete player {name}?")
        if confirm:
            del self.players[name]

            for rnd in self.rounds:
                rnd.pop(name, None)

            self.save_data()
            self.refresh_table()

    # ---------------- Reset Game ---------------- #
    def reset_game(self):
        confirm = messagebox.askyesno("Reset Game",
                                      "Reset all scores but keep players?")
        if confirm:
            for name in self.players:
                self.players[name]["total"] = 0
                self.players[name]["status"] = "ACTIVE"

            self.rounds = []
            self.save_data()
            self.refresh_table()

    # ---------------- Reset Players ---------------- #
    def reset_players(self):
        confirm = messagebox.askyesno("Reset Players",
                                      "Delete ALL players and rounds?")
        if confirm:
            self.players = {}
            self.rounds = []
            self.save_data()
            self.refresh_table()

    # ---------------- Submit Round ---------------- #
    def submit_round(self):

        if not self.players:
            messagebox.showwarning("Error", "Add players first")
            return

        round_data = {}
        lowest_score = None
        winner = None

        for name, entry in self.entry_widgets.items():
            try:
                score = int(entry.get())
            except:
                score = 0

            round_data[name] = score
            self.players[name]["total"] += score

            if lowest_score is None or score < lowest_score:
                lowest_score = score
                winner = name

            if self.players[name]["total"] >= MAX_POINTS:
                self.players[name]["status"] = "OUT"

        round_data["winner"] = winner
        self.rounds.append(round_data)

        self.save_data()
        self.refresh_table()

    # ---------------- Refresh Table ---------------- #
    def refresh_table(self):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        for widget in self.round_entry_frame.winfo_children():
            widget.destroy()

        self.entry_widgets = {}

        # Header
        tk.Label(self.table_frame, text="Rnd",
                 borderwidth=1, relief="solid",
                 width=4).grid(row=0, column=0)

        col = 1
        for name in self.players:
            tk.Label(self.table_frame, text=name,
                     borderwidth=1, relief="solid",
                     width=6).grid(row=0, column=col)
            col += 1

        # Entry Row
        tk.Label(self.round_entry_frame,
                 text="Enter:").grid(row=0, column=0)

        col = 1
        for name in self.players:
            entry = tk.Entry(self.round_entry_frame,
                             width=5)
            entry.grid(row=0, column=col, padx=2)
            self.entry_widgets[name] = entry
            col += 1

        # Rounds
        for i, rnd in enumerate(self.rounds):
            tk.Label(self.table_frame,
                     text=str(i+1),
                     borderwidth=1,
                     relief="solid",
                     width=4).grid(row=i+1,
                                   column=0)

            col = 1
            for name in self.players:
                score = rnd.get(name, "")
                text = str(score)

                if rnd.get("winner") == name:
                    text += "="

                tk.Label(self.table_frame,
                         text=text,
                         borderwidth=1,
                         relief="solid",
                         width=6).grid(row=i+1,
                                       column=col)
                col += 1

        # Total Row
        total_row = len(self.rounds) + 1

        tk.Label(self.table_frame,
                 text="Tot",
                 borderwidth=1,
                 relief="solid",
                 width=4).grid(row=total_row,
                               column=0)

        col = 1
        for name in self.players:
            total = self.players[name]["total"]
            text = str(total)

            if self.players[name]["status"] == "OUT":
                text += "X"

            tk.Label(self.table_frame,
                     text=text,
                     borderwidth=1,
                     relief="solid",
                     width=6).grid(row=total_row,
                                   column=col)
            col += 1

    # ---------------- Save & Load ---------------- #
    def save_data(self):
        data = {
            "players": self.players,
            "rounds": self.rounds
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.players = data.get("players", {})
                self.rounds = data.get("rounds", [])
        else:
            self.players = {}
            self.rounds = []


# ---------------- Run ---------------- #
root = tk.Tk()
app = RummyApp(root)
root.mainloop()