#!/usr/bin/env python3
"""Snake de escritorio para Windows, construido con tkinter."""

import json
import os
import random
import tkinter as tk

CELL = 28
GRID = 20
BOARD = CELL * GRID
PROGRESS_FILE = os.path.join(os.path.expanduser("~"), ".snake_progress.json")

LEVELS = [
    {"speed": 150, "target": 8, "time": 60, "color": "#45e0a8", "obstacles": []},
    {"speed": 135, "target": 9, "time": 65, "color": "#41c7e8", "obstacles": [(3, 3), (16, 3), (3, 16), (16, 16)]},
    {"speed": 120, "target": 10, "time": 70, "color": "#f2d15b", "obstacles": [(6, 3), (13, 3), (6, 16), (13, 16), (3, 6), (16, 6), (3, 13), (16, 13)]},
    {"speed": 105, "target": 11, "time": 75, "color": "#ff6b6b", "obstacles": [(4, 5), (5, 5), (6, 5), (13, 5), (14, 5), (15, 5), (4, 14), (5, 14), (6, 14), (13, 14), (14, 14), (15, 14)]},
    {"speed": 92, "target": 12, "time": 80, "color": "#c48cff", "obstacles": [(7, 3), (8, 3), (9, 3), (10, 3), (7, 16), (8, 16), (9, 16), (10, 16), (3, 6), (3, 7), (16, 13), (16, 14)]},
    {"speed": 80, "target": 13, "time": 85, "color": "#73a7ff", "obstacles": [(5, y) for y in range(3, 8)] + [(14, y) for y in range(13, 18)] + [(10, 5), (11, 5), (4, 14), (5, 14)]},
    {"speed": 70, "target": 14, "time": 90, "color": "#f5f7fa", "obstacles": [(7, 3), (8, 3), (9, 3), (10, 3), (7, 16), (8, 16), (9, 16), (10, 16), (3, 6), (3, 7), (16, 13), (16, 14), (5, 5), (14, 14), (10, 8), (9, 12)]},
]


def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return {"unlocked": max(1, min(7, int(data.get("unlocked", 1)))), "best": data.get("best", {})}
    except (OSError, ValueError, TypeError):
        return {"unlocked": 1, "best": {}}


def save_progress(progress):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
            json.dump(progress, file)
    except OSError:
        pass


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake - 7 niveles")
        self.root.resizable(False, False)
        self.root.configure(bg="#10151d")
        self.progress = load_progress()
        self.after_id = None
        self.timer_id = None
        self.running = False
        self.build_menu()

    def clear(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.after_id = None
        self.timer_id = None
        self.running = False
        self.root.unbind("<KeyPress>")
        for widget in self.root.winfo_children():
            widget.destroy()

    def label(self, parent, text, size=12, color="#c7d0dc", bold=False):
        return tk.Label(parent, text=text, fg=color, bg="#10151d", font=("Segoe UI", size, "bold" if bold else "normal"))

    def build_menu(self):
        self.clear()
        panel = tk.Frame(self.root, bg="#10151d", padx=42, pady=30)
        panel.pack()
        self.label(panel, "S N A K E", 30, "#45e0a8", True).pack()
        self.label(panel, "7 niveles - desafio clasico", 12, "#8290a3").pack(pady=(2, 28))
        unlocked = self.progress["unlocked"]
        tk.Button(panel, text=f"JUGAR - NIVEL {unlocked}", command=lambda: self.start(unlocked), width=24, bg="#45e0a8", fg="#10151d", relief="flat", font=("Segoe UI", 12, "bold"), pady=8).pack(pady=5)
        tk.Button(panel, text="SELECCIONAR NIVEL", command=self.level_menu, width=24, bg="#25313d", fg="#e9eef4", relief="flat", font=("Segoe UI", 11, "bold"), pady=8).pack(pady=5)
        tk.Button(panel, text="COMO JUGAR", command=self.help_screen, width=24, bg="#25313d", fg="#e9eef4", relief="flat", font=("Segoe UI", 11, "bold"), pady=8).pack(pady=5)
        self.label(panel, "Flechas o W A S D - Esc para volver", 10, "#647386").pack(pady=(25, 0))

    def level_menu(self):
        self.clear()
        panel = tk.Frame(self.root, bg="#10151d", padx=38, pady=28)
        panel.pack()
        self.label(panel, "SELECCIONAR NIVEL", 21, "#f2d15b", True).pack(pady=(0, 18))
        for number, level in enumerate(LEVELS, 1):
            locked = number > self.progress["unlocked"]
            best = self.progress["best"].get(str(number), 0)
            text = f"{number}   NIVEL {number}   {'BLOQUEADO' if locked else f'MEJOR {best}'}"
            tk.Button(panel, text=text, command=lambda n=number: self.start(n), width=30, state="disabled" if locked else "normal", bg="#25313d", fg=level["color"], disabledforeground="#4d5966", relief="flat", font=("Segoe UI", 11, "bold"), pady=5).pack(pady=3)
        tk.Button(panel, text="VOLVER", command=self.build_menu, width=30, bg="#18212b", fg="#aeb9c7", relief="flat", pady=6).pack(pady=(18, 0))

    def help_screen(self):
        self.clear()
        panel = tk.Frame(self.root, bg="#10151d", padx=45, pady=30)
        panel.pack()
        self.label(panel, "COMO JUGAR", 22, "#41c7e8", True).pack(pady=(0, 18))
        instructions = ["Come la comida dorada para crecer.", "Evita los bordes, tu cuerpo y los obstaculos.", "Completa el objetivo antes de que termine el tiempo.", "Cada nivel es mas rapido y tiene nuevos obstaculos.", "ESC vuelve al menu; R reinicia la partida."]
        for line in instructions:
            self.label(panel, "- " + line, 12).pack(anchor="w", pady=4)
        tk.Button(panel, text="VOLVER", command=self.build_menu, width=24, bg="#25313d", fg="#e9eef4", relief="flat", pady=7).pack(pady=(22, 0))

    def start(self, level_number):
        self.clear()
        self.level_number = level_number
        self.level = LEVELS[level_number - 1]
        self.snake = [(5, 10), (4, 10), (3, 10)]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.food_count = 0
        self.time_left = self.level["time"]
        self.obstacles = set(self.level["obstacles"])
        self.food = self.spawn_food()
        self.running = True
        header = tk.Frame(self.root, bg="#10151d")
        header.pack(fill="x", padx=16, pady=(14, 8))
        self.status = self.label(header, "", 11, "#c7d0dc", True)
        self.status.pack(side="left")
        self.label(header, "ESC  MENU", 10, "#647386").pack(side="right")
        self.canvas = tk.Canvas(self.root, width=BOARD, height=BOARD, bg="#17212c", highlightthickness=1, highlightbackground="#30404e")
        self.canvas.pack(padx=16, pady=(0, 16))
        self.root.bind("<KeyPress>", self.key_pressed)
        self.root.focus_force()
        self.draw()
        self.tick()
        self.timer_id = self.root.after(1000, self.countdown)

    def spawn_food(self):
        free = [(x, y) for x in range(GRID) for y in range(GRID) if (x, y) not in self.snake and (x, y) not in self.obstacles]
        return random.choice(free)

    def key_pressed(self, event):
        key = event.keysym.lower()
        directions = {"up": (0, -1), "w": (0, -1), "down": (0, 1), "s": (0, 1), "left": (-1, 0), "a": (-1, 0), "right": (1, 0), "d": (1, 0)}
        if key == "escape":
            self.build_menu()
            return
        if key == "r":
            self.start(self.level_number)
            return
        new_direction = directions.get(key)
        if new_direction and new_direction != (-self.direction[0], -self.direction[1]):
            self.next_direction = new_direction

    def countdown(self):
        if not self.running:
            return
        self.time_left -= 1
        self.draw()
        if self.time_left <= 0:
            self.finish(False, "Se acabo el tiempo")
            return
        self.timer_id = self.root.after(1000, self.countdown)

    def tick(self):
        if not self.running:
            return
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        hit_body = new_head in self.snake[:-1]
        hit_wall = not (0 <= new_head[0] < GRID and 0 <= new_head[1] < GRID)
        if hit_body or new_head in self.obstacles or hit_wall:
            self.finish(False, "Has chocado")
            return
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.food_count += 1
            if self.food_count >= self.level["target"]:
                self.finish(True, "Nivel superado")
                return
            self.food = self.spawn_food()
        else:
            self.snake.pop()
        self.draw()
        self.after_id = self.root.after(self.level["speed"], self.tick)

    def draw(self):
        self.canvas.delete("all")
        for x, y in self.obstacles:
            self.cell(x, y, "#344352")
        fx, fy = self.food
        self.cell(fx, fy, "#f2d15b", oval=True)
        for index, (x, y) in enumerate(self.snake):
            self.cell(x, y, self.level["color"] if index == 0 else "#238f78", oval=True)
        self.status.config(text=f"NIVEL {self.level_number}    COMIDA {self.food_count}/{self.level['target']}    TIEMPO {self.time_left}s")

    def cell(self, x, y, color, oval=False):
        gap = 3
        box = (x * CELL + gap, y * CELL + gap, (x + 1) * CELL - gap, (y + 1) * CELL - gap)
        if oval:
            self.canvas.create_oval(*box, fill=color, outline="")
        else:
            self.canvas.create_rectangle(*box, fill=color, outline=color)

    def finish(self, won, reason):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        score = self.food_count * self.level_number * 10
        current_best = int(self.progress["best"].get(str(self.level_number), 0))
        if score > current_best:
            self.progress["best"][str(self.level_number)] = score
        if won and self.level_number == self.progress["unlocked"] and self.level_number < len(LEVELS):
            self.progress["unlocked"] += 1
        save_progress(self.progress)
        self.canvas.create_rectangle(55, 210, BOARD - 55, 350, fill="#10151d", outline="#45e0a8", width=2)
        title = "NIVEL SUPERADO" if won else "GAME OVER"
        self.canvas.create_text(BOARD // 2, 245, text=title, fill=self.level["color"], font=("Segoe UI", 22, "bold"))
        self.canvas.create_text(BOARD // 2, 280, text=f"{reason} - Puntaje: {score}", fill="#e9eef4", font=("Segoe UI", 11))
        self.canvas.create_text(BOARD // 2, 320, text="R: reintentar     ESC: menu", fill="#8290a3", font=("Segoe UI", 10))


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
