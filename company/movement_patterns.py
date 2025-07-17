import pygame
import random
import math

class MovingPoint:
    def __init__(self, x, y, image_path, speed, screen_width, screen_height, cm_to_pixels):
        self.x = float(x)
        self.y = float(y)
        
        loaded_image = pygame.image.load(image_path).convert()

        # 画像の左上ピクセルを透明色として設定
        background_color = loaded_image.get_at((0, 0))
        loaded_image.set_colorkey(background_color)

        new_width =  3 * cm_to_pixels
        new_height = 1 * cm_to_pixels
        
        self.image = pygame.transform.scale(loaded_image, (new_width, new_height))
        
        # 描画の際に常に元の画像を使用するためにコピーを保存
        self.original_image = self.image.copy()
        
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.angle = 0
        self.flip_h = False

        # 初期速度をランダムに設定
        self.dx = random.choice([-1, 1]) * self.speed
        self.dy = random.choice([-1, 1]) * self.speed

    def update_random(self):
        # 画面の端で跳ね返る
        # if self.rect.left <= 0 or self.rect.right >= self.screen_width:
        if self.rect.left <= 0 or self.rect.right >= self.screen_width-200:
            self.dx *= -1
        # if self.rect.top <= 100 or self.rect.bottom >= self.screen_height:
        if self.rect.top <= 100 or self.rect.bottom >= self.screen_height:
            self.dy *= -1
            
        # 座標を更新
        self.x += self.dx
        self.y += self.dy
        
        # 進行方向に基づいて回転角度を計算 (Pygameのy軸は下向きなので、yの符号を反転)
        angle_rad = math.atan2(-self.dy, self.dx)
        self.angle = math.degrees(angle_rad)
        
        # 進行方向が左向きの場合は水平反転し、180度オフセットを加える
        if self.dx < 0:
            self.flip_h = True
            self.angle += 180
        else:
            self.flip_h = False
        
        self.rect.center = (int(self.x), int(self.y))
        
    def update_up_to_down(self):
        # 画面の端で移動方向を反転
        if self.rect.bottom >= self.screen_height or self.rect.top <= 0:
            self.speed *= -1
            
        # 移動方向（speedの符号）に基づいて画像の向きを更新
        if self.speed > 0:
            # 下方向への移動。右端が下を向くように回転。
            self.angle = -90
        else:
            # 上方向への移動。右端が上を向くように回転。
            self.angle = 90
            
        self.flip_h = False
        
        # 座標を更新
        self.y += self.speed
        
        self.rect.center = (int(self.x), int(self.y))
        
    def update_down_to_up(self):
        # 画面の端で移動方向を反転
        if self.rect.top <= 0 or self.rect.bottom >= self.screen_height:
            self.speed *= -1
            
        # 移動方向（speedの符号）に基づいて画像の向きを更新
        if self.speed > 0:
            # 上方向への移動。右端が上を向くように回転。
            self.angle = 90
        else:
            # 下方向への移動。右端が下を向くように回転。
            self.angle = -90
            
        self.flip_h = False
        
        # 座標を更新
        self.y -= self.speed
        
        self.rect.center = (int(self.x), int(self.y))

    def update_right_to_left(self):
        # 画面の端で移動方向を反転
        if self.rect.left <= 0 or self.rect.right >= self.screen_width:
            self.speed *= -1
            
        # 移動方向（speedの符号）に基づいて画像の向きを更新
        if self.speed > 0:
            # 左方向への移動
            self.angle = 0
            self.flip_h = True
        else:
            # 右方向への移動
            self.angle = 0
            self.flip_h = False
            
        # 座標を更新
        self.x -= self.speed
            
        self.rect.center = (int(self.x), int(self.y))

    def update_left_to_right(self):
        # 画面の端で移動方向を反転
        if self.rect.right >= self.screen_width or self.rect.left <= 0:
            self.speed *= -1
            
        # 移動方向（speedの符号）に基づいて画像の向きを更新
        if self.speed > 0:
            # 右方向への移動
            self.angle = 0
            self.flip_h = False
        else:
            # 左方向への移動
            self.angle = 0
            self.flip_h = True
        
        # 座標を更新
        self.x += self.speed
        
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        # 水平反転を適用する
        flipped_image = pygame.transform.flip(self.original_image, self.flip_h, False)
        
        # 水平反転後の画像に対して回転を適用する
        rotated_image = pygame.transform.rotate(flipped_image, self.angle)
        
        # 回転後の画像のrectを取得し、元の中心座標に合わせる
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect)