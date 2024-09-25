import tkinter as tk
from tkinter import messagebox, simpledialog
import math
import random
import sys
import time

class SudokuGame:
    def __init__(self, master):
        self.master = master
        self.master.title("스도쿠 게임")

        # 캔버스 생성
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # 이벤트 바인딩
        self.master.bind("<Key>", self.on_key_press)
        self.master.bind('<Configure>', self.on_window_resize)

        # 게임 초기화
        self.create_game()

    def create_game(self):
        # 기존 캔버스 내용 삭제
        self.canvas.delete("all")

        # 게임 상태 초기화
        self.size = self.get_grid_size()
        if not self.size:
            sys.exit()

        self.level = self.get_difficulty_level()

        self.box_size = int(math.isqrt(self.size))
        if self.box_size ** 2 != self.size:
            messagebox.showerror("오류", "그리드 크기는 완전한 제곱수여야 합니다 (예: 9, 16, 25).")
            self.create_game()
            return

        self.start_time = time.time()
        self.solved = False
        self.board = [[0]*self.size for _ in range(self.size)]
        self.selected_cell = (0, 0)  # 선택된 셀의 위치 (i, j)

        # 퍼즐 생성
        self.generate_puzzle()

        # 그리드 그리기
        self.draw_grid()

    def get_grid_size(self):
        while True:
            try:
                size = simpledialog.askinteger("그리드 크기", "그리드 크기를 입력하세요 (9, 16, 25 중 하나):", minvalue=9, maxvalue=25)
                if size in [9, 16, 25]:
                    return size
                else:
                    messagebox.showerror("입력 오류", "9, 16, 25 중 하나를 입력해주세요.")
            except ValueError:
                messagebox.showerror("입력 오류", "유효한 정수를 입력해주세요.")

    def get_difficulty_level(self):
        while True:
            try:
                level = simpledialog.askinteger("난이도 선택", "난이도를 선택하세요 (1-4):\nLevel 1: 80% 채워짐\nLevel 2: 40% 채워짐\nLevel 3: 20% 채워짐\nLevel 4: 10% 채워짐", minvalue=1, maxvalue=4)
                if level in [1, 2, 3, 4]:
                    return level
                else:
                    messagebox.showerror("입력 오류", "1에서 4 사이의 정수를 입력해주세요.")
            except ValueError:
                messagebox.showerror("입력 오류", "유효한 정수를 입력해주세요.")

    def draw_grid(self):
        self.canvas.delete("all")
        self.cells = {}

        # 캔버스 크기 가져오기
        self.canvas.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 셀 크기 계산 (셀 크기를 동적으로 조절)
        max_cell_width = canvas_width / (self.size + 2)  # 좌우 여백을 고려하여 +2
        max_cell_height = canvas_height / (self.size + 2)  # 상하 여백을 고려하여 +2
        self.cell_size = min(max_cell_width, max_cell_height)
        if self.cell_size > 40:
            self.cell_size = 40  # 최대 셀 크기 제한

        # 폰트 크기 계산
        font_size = int(self.cell_size / 2)
        if font_size < 8:
            font_size = 8

        # 퍼즐의 전체 크기 계산
        puzzle_width = self.size * self.cell_size
        puzzle_height = self.size * self.cell_size

        # 퍼즐을 중앙에 배치하기 위한 오프셋 계산
        offset_x = (canvas_width - puzzle_width) / 2
        offset_y = (canvas_height - puzzle_height) / 2

        for i in range(self.size):
            for j in range(self.size):
                x0 = offset_x + j * self.cell_size
                y0 = offset_y + i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                if (i, j) == self.selected_cell:
                    fill_color = "red"
                else:
                    fill_color = "white"
                rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline="black")
                if self.board[i][j] != 0:
                    fixed = True
                    text_color = "black"
                else:
                    fixed = False
                    text_color = "blue"
                text = None
                if self.board[i][j] != 0:
                    text = self.canvas.create_text(x0 + self.cell_size/2, y0 + self.cell_size/2,
                                                   text=str(self.board[i][j]),
                                                   font=("Arial", font_size),
                                                   fill=text_color)
                self.cells[(i, j)] = {'rect': rect, 'text': text, 'fixed': fixed}

        self.highlight_selected_cell()

    def highlight_selected_cell(self):
        # 모든 셀의 배경색을 업데이트
        for (i, j), cell in self.cells.items():
            if (i, j) == self.selected_cell:
                self.canvas.itemconfig(cell['rect'], fill="red")
            else:
                self.canvas.itemconfig(cell['rect'], fill="white")

    def on_key_press(self, event):
        key = event.keysym
        i, j = self.selected_cell

        if key in ['Up', 'w', 'W']:
            if i > 0:
                self.selected_cell = (i - 1, j)
        elif key in ['Down', 's', 'S']:
            if i < self.size - 1:
                self.selected_cell = (i + 1, j)
        elif key in ['Left', 'a', 'A']:
            if j > 0:
                self.selected_cell = (i, j - 1)
        elif key in ['Right', 'd', 'D']:
            if j < self.size - 1:
                self.selected_cell = (i, j + 1)
        elif key.isdigit():
            if key == '0':
                return
            elif int(key) in range(1, self.size + 1):
                if not self.cells[(i, j)]['fixed']:
                    self.board[i][j] = int(key)
                    if self.cells[(i, j)]['text']:
                        self.canvas.delete(self.cells[(i, j)]['text'])
                    x0 = self.canvas.coords(self.cells[(i, j)]['rect'])[0]
                    y0 = self.canvas.coords(self.cells[(i, j)]['rect'])[1]
                    font_size = int(self.cell_size / 2)
                    if font_size < 8:
                        font_size = 8
                    text = self.canvas.create_text(x0 + self.cell_size/2,
                                                   y0 + self.cell_size/2,
                                                   text=key, font=("Arial", font_size), fill="blue")
                    self.cells[(i, j)]['text'] = text
                    if self.check_puzzle():
                        self.solved = True
                        end_time = time.time()
                        elapsed_time = end_time - self.start_time
                        minutes = int(elapsed_time // 60)
                        seconds = int(elapsed_time % 60)
                        messagebox.showinfo("퍼즐 완료", f"축하합니다! 퍼즐을 완성하셨습니다.\n소요 시간: {minutes}분 {seconds}초")
                        self.ask_new_game()
        elif key == 'BackSpace' or key == 'Delete':
            if not self.cells[(i, j)]['fixed']:
                self.board[i][j] = 0
                if self.cells[(i, j)]['text']:
                    self.canvas.delete(self.cells[(i, j)]['text'])
                    self.cells[(i, j)]['text'] = None

        self.highlight_selected_cell()

    def on_window_resize(self, event):
        if event.widget == self.master:
            self.draw_grid()

    def ask_new_game(self):
        result = messagebox.askquestion("새 게임", "새로운 게임을 시작하시겠습니까?")
        if result == 'yes':
            self.create_game()
        else:
            self.master.quit()

    def check_puzzle(self):
        # 사용자의 입력을 정답과 비교
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != self.solution[i][j]:
                    return False
        return True

    def generate_puzzle(self):
        # 새로운 퍼즐 생성 방식: 미리 정의된 패턴과 셔플을 사용하여 완성된 보드 생성

        base = self.box_size
        side = base * base

        # pattern for a baseline valid solution
        def pattern(r, c): return (base*(r % base)+r//base+c) % side

        # randomize rows, columns and numbers (of valid base pattern)
        from random import sample

        def shuffle(s): return sample(s, len(s))
        r_base = range(base)
        rows = [g*base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g*base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, side+1))

        # produce board using randomized baseline pattern
        self.solution = [[nums[pattern(r, c)] for c in cols] for r in rows]

        # copy solution to board
        self.board = [row[:] for row in self.solution]

        # 난이도에 따른 채워진 셀 비율 설정
        total_cells = self.size * self.size
        if self.level == 1:
            filled_percentage = 80
        elif self.level == 2:
            filled_percentage = 40
        elif self.level == 3:
            filled_percentage = 20
        elif self.level == 4:
            filled_percentage = 10

        cells_to_remove = total_cells * (100 - filled_percentage) // 100

        # 셀 제거
        while cells_to_remove > 0:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)
            if self.board[row][col] != 0:
                self.board[row][col] = 0
                cells_to_remove -= 1

    # 창 닫기 이벤트 처리
    def on_closing(self):
        self.master.quit()

def main():
    root = tk.Tk()
    game = SudokuGame(root)
    root.protocol("WM_DELETE_WINDOW", game.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
