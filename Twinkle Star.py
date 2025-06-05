import tkinter as tk
import time
import random

# -----------------------------
# 參數設定
# -----------------------------
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 500
BASKET_WIDTH = 80
BASKET_HEIGHT = 20
STAR_SIZE = 15
FRAME_DELAY = 30            # 毫秒為單位（約 0.03 秒）
TOTAL_FRAMES = 300          # 共 300 個畫面，約 9 秒（300 * 0.03 ≈ 9s）
STAR_SPAWN_CHANCE = 1 / 20  # 每個畫面有 5% 機率出現新星星


class CatchStarsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Catch the Falling Stars!")

        # 建立 Canvas
        self.canvas = tk.Canvas(
            root,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="navy"
        )
        self.canvas.pack()

        # 遊戲狀態
        self.score = 0
        self.game_frame = 0
        self.stars = []  # 每個星星紀錄字典：{'id': CanvasItemId, 'x': float, 'y': float, 'color': str, 'speed': int}

        # 籃子位置
        self.basket_x = (CANVAS_WIDTH - BASKET_WIDTH) // 2
        self.basket_y = CANVAS_HEIGHT - 40

        # 用來顯示倒數時間／分數的文字物件 ID
        self.score_text_id = None
        self.time_text_id = None

        # 先顯示標題畫面
        self.show_title_screen()

    def show_title_screen(self):
        """顯示遊戲標題並等候玩家點擊開始"""
        self.canvas.delete("all")
        # 深色背景
        self.canvas.create_rectangle(
            0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="navy", outline="navy"
        )
        # 顯示文字
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 150, text="Catch the Falling Stars!", fill="yellow", font=("Arial", 32)
        )
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 200, text="Move your mouse to control the basket", fill="white", font=("Arial", 16)
        )
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 230, text="Catch yellow stars (+10 points)", fill="yellow", font=("Arial", 14)
        )
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 250, text="Avoid red stars (-5 points)", fill="red", font=("Arial", 14)
        )
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 300, text="Click to start!", fill="white", font=("Arial", 20)
        )

        # 綁定滑鼠點擊，開始遊戲
        self.canvas.bind("<Button-1>", self.start_game)

    def start_game(self, event=None):
        """點擊後初始化遊戲變數並開始主迴圈"""

        # 取消標題畫面綁定的點擊事件，避免重複觸發
        self.canvas.unbind("<Button-1>")

        # 1. **先把整個 Canvas 清空（包含標題文字）**
        self.canvas.delete("all")

        # 2. 重置遊戲狀態
        self.score = 0
        self.game_frame = 0
        # 如果有剩餘的星星，先清空它們
        for star in self.stars:
            try:
                self.canvas.delete(star['id'])
                if star['sparkle_id'] is not None:
                    self.canvas.delete(star['sparkle_id'])
            except:
                pass
        self.stars.clear()

        # 3. 綁定滑鼠移動來控制籃子位置
        self.root.bind("<Motion>", self.on_mouse_move)

        # 4. 在畫面上建立分數與時間的文字（此時畫面已是空白）
        self.score_text_id = self.canvas.create_text(
            50, 30, text=f"Score: {self.score}", fill="white", font=("Arial", 18)
        )
        self.time_text_id = self.canvas.create_text(
            CANVAS_WIDTH - 80, 30, text=f"Time: {self.get_time_left()}s", fill="white", font=("Arial", 18)
        )

        # 5. 立刻執行第一幀
        self.game_loop()


    def on_mouse_move(self, event):
        """滑鼠移動時更新籃子水平座標（event.x 給出滑鼠在 Canvas 上的 x 座標）"""
        new_x = event.x - BASKET_WIDTH // 2
        # 限制在左右邊界內
        new_x = max(0, min(new_x, CANVAS_WIDTH - BASKET_WIDTH))
        self.basket_x = new_x

    def get_time_left(self):
        """計算剩餘秒數"""
        frames_left = max(0, TOTAL_FRAMES - self.game_frame)
        # 每 10 幀視為 1 秒（因為 10 * 0.03 ≈ 0.3 秒，這裡只是和原本邏輯對應，顯示為整秒）
        # 你可以依需求調整顯示方式
        # 這裡用整除 10 讓它跟原先程式的 (300 - game_time)//10 一致
        return frames_left // 10

    def game_loop(self):
        """每一幀的更新函式，使用 after() 週期呼叫自己"""
        # 如果遊戲尚未結束，繼續更新
        if self.game_frame < TOTAL_FRAMES:
            # 1. 清除畫面（我們只刪除星星與籃子，分數和時間文字保留並更新）
            self.canvas.delete("basket")   # 標籤為 "basket" 的物件會被刪除
            # 刪掉所有標籤為 "star" 的物件
            #self.canvas.delete("star")
            # 先畫一個深藍背景（避免閃爍，我們這次改用底色一次畫滿，之後不再每幀重畫背景）
            # 因為我們已經在 Canvas 初始化時設為 bg="navy"，所以這裡可省略

            # 2. 隨機產生新星星（大約 5% 機率）
            if random.random() < STAR_SPAWN_CHANCE:
                star_x = random.randint(STAR_SIZE, CANVAS_WIDTH - STAR_SIZE)
                star_type = "yellow" if random.random() < 0.75 else "red"
                speed = random.randint(3, 7)
                # 先畫一個圓形代表星星，之後移動這個物件
                color = star_type
                # create_oval 回傳一個物件 ID，用來後續移動或刪除
                star_id = self.canvas.create_oval(
                    star_x - STAR_SIZE // 2, 0 - STAR_SIZE // 2,
                    star_x + STAR_SIZE // 2, 0 + STAR_SIZE // 2,
                    fill=color, outline=color, tags="star"
                )
                # 如果是黃色，在元件上疊一個小白點做閃爍效果
                if star_type == "yellow":
                    sparkle_id = self.canvas.create_oval(
                        star_x - 2, 0 - 2, star_x + 2, 0 + 2,
                        fill="white", outline="white", tags="star"
                    )
                    # 我們可以把 sparkle_id 一併存在同一星星的紀錄裡，方便一起 delete
                    self.stars.append({
                        'id': star_id,
                        'sparkle_id': sparkle_id,
                        'x': star_x,
                        'y': 0,
                        'color': star_type,
                        'speed': speed
                    })
                else:
                    self.stars.append({
                        'id': star_id,
                        'sparkle_id': None,
                        'x': star_x,
                        'y': 0,
                        'color': star_type,
                        'speed': speed
                    })

            # 3. 更新並繪出所有星星
            to_remove = []
            for star in self.stars:
                # 把星星移動到新的 y 座標
                star['y'] += star['speed']
                # 更新對應的畫布物件座標
                self.canvas.coords(
                    star['id'],
                    star['x'] - STAR_SIZE // 2, star['y'] - STAR_SIZE // 2,
                    star['x'] + STAR_SIZE // 2, star['y'] + STAR_SIZE // 2
                )
                # 如果有 sparkle，就一併移動它
                if star['sparkle_id'] is not None:
                    self.canvas.coords(
                        star['sparkle_id'],
                        star['x'] - 2, star['y'] - 2,
                        star['x'] + 2, star['y'] + 2
                    )

                # 4. 檢查星星是否撞到籃子
                if (star['y'] + STAR_SIZE // 2 >= self.basket_y and
                        self.basket_x <= star['x'] <= self.basket_x + BASKET_WIDTH):
                    # 遇到黃色星星 +10 分，紅色 -5 分
                    if star['color'] == "yellow":
                        self.score += 10
                        self.show_score_popup(star['x'], star['y'], "+10", "green")
                    else:
                        self.score -= 5
                        self.show_score_popup(star['x'], star['y'], "-5", "red")
                    to_remove.append(star)

                # 5. 如果掉出畫面底部，也要移除
                elif star['y'] - STAR_SIZE // 2 > CANVAS_HEIGHT:
                    to_remove.append(star)

            # 6. 移除要刪掉的星星
            for star in to_remove:
                try:
                    self.canvas.delete(star['id'])
                    if star['sparkle_id'] is not None:
                        self.canvas.delete(star['sparkle_id'])
                except:
                    pass
                if star in self.stars:
                    self.stars.remove(star)

            # 7. 繪製籃子（畫一個矩形，標籤為 "basket"）
            self.canvas.create_rectangle(
                self.basket_x, self.basket_y,
                self.basket_x + BASKET_WIDTH, self.basket_y + BASKET_HEIGHT,
                fill="brown", outline="black", tags="basket"
            )

            # 8. 更新分數與剩餘時間文字
            self.canvas.itemconfigure(self.score_text_id, text=f"Score: {self.score}")
            self.canvas.itemconfigure(self.time_text_id, text=f"Time: {self.get_time_left()}s")

            # 9. 下一幀
            self.game_frame += 1
            self.root.after(FRAME_DELAY, self.game_loop)

        else:
            # 遊戲結束
            self.end_game() 

    def show_score_popup(self, x, y, text, color):
        """顯示一個短暫出現的分數提示，約 0.3 秒後自動消失"""
        popup = self.canvas.create_text(
            x, y - 20, text=text, fill=color, font=("Arial", 14)
        )
        # 0.3 秒後把這個文字刪掉
        self.root.after(300, lambda: self.canvas.delete(popup))

    def end_game(self):
        """顯示遊戲結束畫面，並等候玩家點擊重新開始"""
        # 先把剩餘的星星與籃子刪除
        self.canvas.delete("star")
        self.canvas.delete("basket")
        # 停掉滑鼠移動綁定
        self.root.unbind("<Motion>")

        # 深藍背景
        self.canvas.create_rectangle(
            0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="navy", outline="navy"
        )
        # 顯示 Game Over 文字
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 150, text="Game Over!", fill="white", font=("Arial", 36)
        )
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 200, text=f"Final Score: {self.score}", fill="yellow", font=("Arial", 24)
        )

        # 根據得分顯示不同訊息
        if self.score >= 100:
            message = "Excellent! You're a star catcher!"
            msg_color = "gold"
        elif self.score >= 50:
            message = "Great job! Keep practicing!"
            msg_color = "lime"
        elif self.score >= 0:
            message = "Good effort! Try again!"
            msg_color = "cyan"
        else:
            message = "Watch out for those red stars!"
            msg_color = "orange"

        self.canvas.create_text(
            CANVAS_WIDTH // 2, 250, text=message, fill=msg_color, font=("Arial", 18)
        )
        self.canvas.create_text(
            CANVAS_WIDTH // 2, 320, text="Click to play again!", fill="white", font=("Arial", 16)
        )

        # 綁定畫面點擊來重啟遊戲
        self.canvas.bind("<Button-1>", self.on_restart_click)

    def on_restart_click(self, event=None):
        """點擊後解除綁定並重新顯示標題畫面"""
        self.canvas.unbind("<Button-1>")
        self.show_title_screen()


if __name__ == "__main__":
    root = tk.Tk()
    game = CatchStarsGame(root)
    root.mainloop()
