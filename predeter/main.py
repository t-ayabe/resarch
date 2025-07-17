import pygame
import random
import math
import colors
import os
from movement_patterns import MovingPoint

# Pygameの初期化
pygame.init()
pygame.font.init()

# スクリーン設定 (全画面表示のため、現在の解像度を取得)
SUB_MONITOR_X_POS = 1920 # メインモニターの幅
SUB_MONITOR_Y_POS = 0    # サブモニターのY座標
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{SUB_MONITOR_X_POS},{SUB_MONITOR_Y_POS}"
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# 全画面表示でスクリーンを作成
dis = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF)
pygame.display.set_caption("Random Movement Game")

# 1cmをピクセルに変換 (ここではDPIを96と仮定。実際のDPIに合わせて調整してください)
# 1インチ = 2.54 cm
# 1cm = 1 / 2.54 インチ
# 1cm のピクセル幅 = (1 / 2.54) * DPI
# 例えば、DPI=96の場合: (1 / 2.54) * 96 = 約 37.795 ピクセル
inch = 17.3
dpi = (SCREEN_HEIGHT**2+SCREEN_WIDTH**2)**(1/2)/inch
CM_TO_PIXELS = dpi/2.54 # 1cmあたりのピクセル数

# フォントの設定
# 日本語フォントのパスを指定
JAPANESE_FONT_PATH = 'C:/Windows/Fonts/meiryo.ttc'

# フォントがロードできない場合のためにフォールバックも検討
try:
    font_title = pygame.font.Font(JAPANESE_FONT_PATH, 60)
    font_message = pygame.font.Font(JAPANESE_FONT_PATH, 30)
    font_input = pygame.font.Font(JAPANESE_FONT_PATH, 30)
except FileNotFoundError:
    print(f"Warning: Japanese font not found at {JAPANESE_FONT_PATH}. Using default font.")
    font_title = pygame.font.Font(None, 72)
    font_message = pygame.font.Font(None, 36)
    font_input = pygame.font.Font(None, 30)

# ゲームの状態
GAME_STATE_START_MENU = 0
GAME_STATE_PLAYING = 1

# スタートメニュー内のサブ状態
START_MENU_MAIN = 0
START_MENU_MOVEMENT_PICKER = 2

current_game_state = GAME_STATE_START_MENU
current_start_menu_sub_state = START_MENU_MAIN

# 速度入力用
selected_speed_str = "5"
speed_input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 150, 150, 40)
active_input = False

# Movement pattern selection
movement_patterns = {
    "ランダム": "random",
    "上から下": "up_to_down",
    "右から左": "right_to_left"
}
selected_movement_pattern_key = "ランダム" # Default to random
selected_movement_pattern_value = movement_patterns[selected_movement_pattern_key]


# ボタンRects
start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 250, 200, 60)
movement_button_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 80, 140, 40) # New button for movement (位置を調整する可能性あり)
back_to_main_menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 250, 200, 60)

# --- 映像用の変数 ---
moving_point = None
FISH_IMAGE_PATH = './predeter/tagame.png' # 魚の画像パス


# スタート画面の描画関数
def draw_start_menu():
    dis.fill(colors.LIGHT_GRAY)

    if current_start_menu_sub_state == START_MENU_MAIN:
        title_text = font_title.render("Random Movement Game", True, colors.BLACK)
        dis.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4 - 50))

        # 速度入力ボックス
        speed_label = font_input.render("Speed (1-10):", True, colors.BLACK)
        dis.blit(speed_label, (speed_input_rect.x - speed_label.get_width() - 10, speed_input_rect.centery - speed_label.get_height() // 2))
        pygame.draw.rect(dis, colors.WHITE, speed_input_rect)
        pygame.draw.rect(dis, colors.BLACK, speed_input_rect, 2)
        speed_surface = font_input.render(selected_speed_str, True, colors.BLACK)
        dis.blit(speed_surface, (speed_input_rect.x + 5, speed_input_rect.y + 5))

        # 選択された動きのパターンを表示
        movement_label = font_input.render(f"Movement: {selected_movement_pattern_key}", True, colors.BLACK)
        dis.blit(movement_label, (SCREEN_WIDTH // 2 - movement_label.get_width() // 2, SCREEN_HEIGHT // 2 + 200))


        # スタートボタン
        pygame.draw.rect(dis, colors.GREEN, start_button_rect)
        start_text = font_title.render("START", True, colors.BLACK)
        dis.blit(start_text, (start_button_rect.x + (start_button_rect.width - start_text.get_width()) // 2,
                                    start_button_rect.y + (start_button_rect.height - start_text.get_height()) // 2))
        
        # Movement Picker Button
        pygame.draw.rect(dis, colors.GRAY, movement_button_rect)
        movement_button_text = font_input.render("Movement", True, colors.BLACK)
        dis.blit(movement_button_text, (movement_button_rect.x + (movement_button_rect.width - movement_button_text.get_width()) // 2,
                                          movement_button_rect.y + (movement_button_rect.height - movement_button_text.get_height()) // 2))

    elif current_start_menu_sub_state == START_MENU_MOVEMENT_PICKER:
        title_text = font_title.render("Movement Pattern", True, colors.BLACK)
        dis.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4 - 50))

        y_offset = SCREEN_HEIGHT // 2 - 100
        for i, (pattern_name, pattern_value) in enumerate(movement_patterns.items()):
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset + i * 60, 300, 50)
            color = colors.GREEN if selected_movement_pattern_key == pattern_name else colors.GRAY
            pygame.draw.rect(dis, color, button_rect)
            pygame.draw.rect(dis, colors.BLACK, button_rect, 2)
            pattern_text = font_message.render(pattern_name, True, colors.BLACK)
            dis.blit(pattern_text, (button_rect.x + (button_rect.width - pattern_text.get_width()) // 2,
                                     button_rect.y + (button_rect.height - pattern_text.get_height()) // 2))
        
        # メインメニューに戻るボタン
        pygame.draw.rect(dis, colors.GRAY, back_to_main_menu_button_rect)
        back_text = font_message.render("Back to Main Menu", True, colors.BLACK)
        dis.blit(back_text, (back_to_main_menu_button_rect.x + (back_to_main_menu_button_rect.width - back_text.get_width()) // 2,
                                    back_to_main_menu_button_rect.y + (back_to_main_menu_button_rect.height - back_text.get_height()) // 2))


# メインゲームループ
def loop():
    global current_game_state, current_start_menu_sub_state
    global selected_speed_str, active_input
    global selected_movement_pattern_key, selected_movement_pattern_value
    global moving_point

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_game_state == GAME_STATE_PLAYING:
                        current_game_state = GAME_STATE_START_MENU
                        current_start_menu_sub_state = START_MENU_MAIN
                        active_input = False
                    elif current_game_state == GAME_STATE_START_MENU:
                        if current_start_menu_sub_state == START_MENU_MOVEMENT_PICKER:
                            current_start_menu_sub_state = START_MENU_MAIN
                        else:
                            pygame.quit()
                            return
                elif event.key == pygame.K_q and current_game_state == GAME_STATE_PLAYING:
                    pygame.quit()
                    return
                
                # 速度入力処理 (メインメニューのみ)
                if current_game_state == GAME_STATE_START_MENU and current_start_menu_sub_state == START_MENU_MAIN and active_input:
                    if event.key == pygame.K_RETURN:
                        active_input = False
                    elif event.key == pygame.K_BACKSPACE:
                        selected_speed_str = selected_speed_str[:-1]
                    else:
                        if event.unicode.isdigit() and len(selected_speed_str) < 2:
                            selected_speed_str += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_game_state == GAME_STATE_START_MENU:
                    if current_start_menu_sub_state == START_MENU_MAIN:

                        # 速度入力ボックスのクリック判定
                        if speed_input_rect.collidepoint(event.pos):
                            active_input = not active_input
                        else:
                            active_input = False

                        # スタートボタンのクリック判定
                        if start_button_rect.collidepoint(event.pos):
                            try:
                                temp_speed = int(selected_speed_str)
                                if 1 <= temp_speed <= 10:
                                    point_speed = temp_speed
                                else:
                                    point_speed = 5
                                    selected_speed_str = "5"
                            except ValueError:
                                point_speed = 5
                                selected_speed_str = "5"
                            
                            # Initialize MovingPoint object with image path
                            moving_point = MovingPoint(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                                                       FISH_IMAGE_PATH, point_speed, 
                                                       SCREEN_WIDTH, SCREEN_HEIGHT, CM_TO_PIXELS)
                            
                            current_game_state = GAME_STATE_PLAYING
                            pygame.mouse.set_visible(False)
                            
                        # Movement Picker Button
                        if movement_button_rect.collidepoint(event.pos):
                            current_start_menu_sub_state = START_MENU_MOVEMENT_PICKER

                    elif current_start_menu_sub_state == START_MENU_MOVEMENT_PICKER:
                        y_offset = SCREEN_HEIGHT // 2 - 100
                        for i, (pattern_name, pattern_value) in enumerate(movement_patterns.items()):
                            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset + i * 60, 300, 50)
                            if button_rect.collidepoint(event.pos):
                                selected_movement_pattern_key = pattern_name
                                selected_movement_pattern_value = pattern_value
                                break # Exit loop once a button is clicked
                        
                        # メインメニューに戻るボタン
                        if back_to_main_menu_button_rect.collidepoint(event.pos):
                            current_start_menu_sub_state = START_MENU_MAIN

        # 描画処理
        if current_game_state == GAME_STATE_START_MENU:
            draw_start_menu()
            pygame.mouse.set_visible(True)

        elif current_game_state == GAME_STATE_PLAYING:
            dis.fill(colors.LIGHT_GRAY) # ゲームプレイ中の背景色

            # Update the moving point based on the selected pattern
            if selected_movement_pattern_value == "random":
                moving_point.update_random()
            elif selected_movement_pattern_value == "up_to_down":
                moving_point.update_up_to_down()
            elif selected_movement_pattern_value == "right_to_left":
                moving_point.update_right_to_left()

            moving_point.draw(dis)
            
        pygame.display.update()
        clock.tick(60)

# ゲームを開始
if __name__ == "__main__":
    loop()