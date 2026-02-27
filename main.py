# -*- coding: utf-8 -*-
'''
贪吃蛇 - Android 版
使用 Kivy 框架开发
'''

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics import Line
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
import random

# 游戏设置
CELL_SIZE = 30
GRID_WIDTH = 12
GRID_HEIGHT = 18
GAME_WIDTH = CELL_SIZE * GRID_WIDTH
GAME_HEIGHT = CELL_SIZE * GRID_HEIGHT

# 颜色
COLOR_BG = (0.04, 0.04, 0.08, 1)
COLOR_SNAKE = (0, 1, 0.53, 1)
COLOR_SNAKE_DARK = (0, 0.8, 0.42, 1)
COLOR_FOOD = (1, 0.42, 0.42, 1)
COLOR_GRID = (0.16, 0.16, 0.24, 1)
COLOR_TEXT = (1, 1, 1, 1)


class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset_game()
        self._update_clock = None
        
    def reset_game(self):
        '''重置游戏'''
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.speed = 0.15  # 秒/帧
        
    def spawn_food(self):
        '''生成食物'''
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), 
                   random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake:
                return food
    
    def update(self, dt):
        '''游戏主循环'''
        if self.game_over or self.paused:
            return
            
        # 移动蛇
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # 检查碰撞
        if self.check_collision(new_head):
            self.game_over = True
            self.show_game_over()
            return
        
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
            # 加速
            if self.speed > 0.08:
                self.speed -= 0.005
        else:
            self.snake.pop()
        
        self.draw_game()
    
    def check_collision(self, pos):
        '''检查碰撞'''
        x, y = pos
        # 撞墙
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return True
        # 撞自己
        if pos in self.snake:
            return True
        return False
    
    def draw_game(self):
        '''绘制游戏画面'''
        self.canvas.clear()
        with self.canvas:
            # 背景
            Color(*COLOR_BG)
            Rectangle(pos=self.pos, size=self.size)
            
            # 网格
            Color(*COLOR_GRID)
            for i in range(GRID_WIDTH + 1):
                Line(points=[self.pos[0] + i * CELL_SIZE, self.pos[1],
                            self.pos[0] + i * CELL_SIZE, self.pos[1] + GAME_HEIGHT],
                    width=1)
            for j in range(GRID_HEIGHT + 1):
                Line(points=[self.pos[0], self.pos[1] + j * CELL_SIZE,
                            self.pos[0] + GAME_WIDTH, self.pos[1] + j * CELL_SIZE],
                    width=1)
            
            # 食物
            Color(*COLOR_FOOD)
            fx = self.pos[0] + self.food[0] * CELL_SIZE + CELL_SIZE // 2
            fy = self.pos[1] + self.food[1] * CELL_SIZE + CELL_SIZE // 2
            from kivy.graphics.ellipse import Ellipse
            Ellipse(pos=(fx - CELL_SIZE // 2 + 2, fy - CELL_SIZE // 2 + 2),
                   size=(CELL_SIZE - 4, CELL_SIZE - 4))
            
            # 蛇
            for i, segment in enumerate(self.snake):
                Color(*COLOR_SNAKE if i == 0 else COLOR_SNAKE_DARK)
                Rectangle(pos=(self.pos[0] + segment[0] * CELL_SIZE + 1,
                              self.pos[1] + segment[1] * CELL_SIZE + 1),
                         size=(CELL_SIZE - 2, CELL_SIZE - 2))
    
    def change_direction(self, new_dir):
        '''改变方向'''
        if self.game_over:
            return
        # 防止 180 度转向
        if (self.direction[0], self.direction[1]) != (-new_dir[0], -new_dir[1]):
            self.direction = new_dir
    
    def show_game_over(self):
        '''显示游戏结束'''
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        label = Label(text=f'游戏结束!\n得分：{self.score}', 
                     font_size='24sp', color=COLOR_TEXT)
        restart_btn = Button(text='重新开始', font_size='20sp', size_hint_y=None, height=50)
        restart_btn.bind(on_press=self.restart_game)
        
        layout.add_widget(label)
        layout.add_widget(restart_btn)
        
        popup = Popup(title='游戏结束', content=layout, size_hint=(0.8, 0.6),
                     background_color=(0, 0, 0, 0.8))
        popup.open()
    
    def restart_game(self, instance=None):
        '''重新开始游戏'''
        if hasattr(instance, 'parent') and hasattr(instance.parent, 'parent'):
            try:
                instance.parent.parent.dismiss()
            except:
                pass
        self.reset_game()
        self.speed = 0.15
        self.draw_game()
        if self._update_clock:
            self._update_clock.cancel()
        self._update_clock = Clock.schedule_interval(self.update, self.speed)
    
    def start_game(self):
        '''开始游戏'''
        self.draw_game()
        self._update_clock = Clock.schedule_interval(self.update, self.speed)


class SnakeApp(App):
    def build(self):
        Window.size = (GAME_WIDTH + 40, GAME_HEIGHT + 150)
        Window.clearcolor = (0.1, 0.1, 0.15, 1)
        
        layout = FloatLayout()
        
        # 游戏区域
        self.game = SnakeGame(size_hint=(None, None),
                             size=(GAME_WIDTH, GAME_HEIGHT),
                             pos=(20, 80))
        layout.add_widget(self.game)
        
        # 分数显示
        self.score_label = Label(text='得分：0', font_size='20sp',
                                size_hint=(None, None),
                                size=(150, 40),
                                pos=(20, 20),
                                color=COLOR_TEXT)
        layout.add_widget(self.score_label)
        
        # 控制按钮
        btn_size = (60, 60)
        btn_style = {'font_size': '24sp', 'size_hint': (None, None)}
        
        # 上
        up_btn = Button(text='⬆️', **btn_style, size=btn_size,
                       pos=(GAME_WIDTH // 2 - 30 + 20, GAME_HEIGHT + 80))
        up_btn.bind(on_press=lambda x: self.game.change_direction((0, 1)))
        layout.add_widget(up_btn)
        
        # 下
        down_btn = Button(text='⬇️', **btn_style, size=btn_size,
                         pos=(GAME_WIDTH // 2 - 30 + 20, 20))
        down_btn.bind(on_press=lambda x: self.game.change_direction((0, -1)))
        layout.add_widget(down_btn)
        
        # 左
        left_btn = Button(text='⬅️', **btn_style, size=btn_size,
                         pos=(20, GAME_HEIGHT // 2 - 30 + 20))
        left_btn.bind(on_press=lambda x: self.game.change_direction((-1, 0)))
        layout.add_widget(left_btn)
        
        # 右
        right_btn = Button(text='➡️', **btn_style, size=btn_size,
                          pos=(GAME_WIDTH - 80 + 20, GAME_HEIGHT // 2 - 30 + 20))
        right_btn.bind(on_press=lambda x: self.game.change_direction((1, 0)))
        layout.add_widget(right_btn)
        
        # 暂停按钮
        pause_btn = Button(text='⏸️', **btn_style, size=(50, 50),
                          pos=(GAME_WIDTH - 60, 20))
        pause_btn.bind(on_press=self.toggle_pause)
        layout.add_widget(pause_btn)
        
        return layout
    
    def toggle_pause(self, instance):
        self.game.paused = not self.game.paused
        instance.text = '▶️' if self.game.paused else '⏸️'
    
    def on_pause(self):
        self.game.paused = True
        return True


if __name__ == '__main__':
    SnakeApp().run()
