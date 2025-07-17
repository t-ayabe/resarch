import pygame
import random
import math
import colors
import colorsys
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
START_MENU_COLOR_PICKER = 1
START_MENU_MOVEMENT_PICKER = 2 # New sub-state for movement selection

current_game_state = GAME_STATE_START_MENU
current_start_menu_sub_state = START_MENU_MAIN

# --- HSL関連の関数---
def hsl_to_rgb(h, s, l):
    """
    HSL (H:0-360, S:0-100, L:0-100) を RGB (0-255, 0-255, 0-255) に変換
    """
    # HSL値を0-1の範囲に正規化 (colorsysが0-1を期待するため)
    h_norm = h / 360.0
    s_norm = s / 100.0
    l_norm = l / 100.0

    # colorsys.hls_to_rgb を使用
    r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm) # 注意: colorsysは (H, L, S) の順序

    # RGB値を0-255の範囲に変換
    return (int(r * 255), int(g * 255), int(b * 255))

def rgb_to_hsl(r, g, b):
    """
    RGB (0-255) を HSL (H:0-360, S:0-100, L:0-100) に変換
    """
    # RGB値を0-1の範囲に正規化
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    # colorsys.rgb_to_hls を使用
    h_norm, l_norm, s_norm = colorsys.rgb_to_hls(r_norm, g_norm, b_norm) # 注意: colorsysは (H, L, S) の順序

    # HSL値を指定の範囲に変換
    h = h_norm * 360.0
    s = s_norm * 100.0
    l = l_norm * 100.0
    return (h, s, l)

# --- スタートメニュー関連の変数---
# プリセットカラー選択用
selected_preset_color_index = 0

# HSLスライダー用
h_value = 0    # Hue: 0-360
s_value = 100 # Saturation: 0-100
l_value = 50  # Lightness: 0-100 (純色の場合、Lightnessは通常50%が適切)
current_selected_rgb_color = hsl_to_rgb(h_value, s_value, l_value) # 選択中のRGB色

# 速度入力用
selected_speed_str = "3"
speed_input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 150, 150, 40)
active_input = False

# Movement pattern selection
movement_patterns = {
    "ランダム": "random",
    "上から下": "up_to_down",
    "下から上": "down_to_up",
    "右から左": "right_to_left",
    "左から右": "left_to_right"
}
selected_movement_pattern_key = "ランダム" # Default to random
selected_movement_pattern_value = movement_patterns[selected_movement_pattern_key]


# ボタンRects
start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 250, 200, 60)
hsl_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 140, 40)
movement_button_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 80, 140, 40) # New button for movement
back_to_main_menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 250, 200, 60)

# スタートメニューの色プレビューボックスのRect
MAIN_MENU_COLOR_PREVIEW_RECT = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 20, 100, 50)

# スライダーのRect (変数名を修正)
slider_width = 300
slider_height = 20
h_slider_rect = pygame.Rect(SCREEN_WIDTH // 2 - slider_width // 2, SCREEN_HEIGHT // 2 - 80, slider_width, slider_height)
s_slider_rect = pygame.Rect(SCREEN_WIDTH // 2 - slider_width // 2, SCREEN_HEIGHT // 2 - 20, slider_width, slider_height)
l_slider_rect = pygame.Rect(SCREEN_WIDTH // 2 - slider_width // 2, SCREEN_HEIGHT // 2 + 40, slider_width, slider_height)

# --- 映像用の変数 ---
# point_x, point_y, point_speed, point_color, d_ang, move_duration_frames, current_frame_count
# These will now be managed by the MovingPoint object
moving_point = None

# スタート画面の描画関数
def draw_start_menu():
    dis.fill(colors.LIGHT_GRAY)

    if current_start_menu_sub_state == START_MENU_MAIN:
        title_text = font_title.render("Random Movement Game", True, colors.BLACK)
        dis.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4 - 50))

        # 現在選択されている色を表示
        pygame.draw.rect(dis, current_selected_rgb_color, MAIN_MENU_COLOR_PREVIEW_RECT)
        pygame.draw.rect(dis, colors.BLACK, MAIN_MENU_COLOR_PREVIEW_RECT, 3)
        color_preview_text = font_message.render("Selected Color", True, colors.BLACK)
        dis.blit(color_preview_text, (SCREEN_WIDTH // 2 - color_preview_text.get_width() // 2, SCREEN_HEIGHT // 2 - 70))

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

        # HSLカラーピッカーボタン
        pygame.draw.rect(dis, colors.GRAY, hsl_button_rect) # hsl_button_rectを使用
        hsl_button_text = font_input.render("HSL Picker", True, colors.BLACK)
        dis.blit(hsl_button_text, (hsl_button_rect.x + (hsl_button_rect.width - hsl_button_text.get_width()) // 2,
                                    hsl_button_rect.y + (hsl_button_rect.height - hsl_button_text.get_height()) // 2))

        # Movement Picker Button
        pygame.draw.rect(dis, colors.GRAY, movement_button_rect)
        movement_button_text = font_input.render("Movement", True, colors.BLACK)
        dis.blit(movement_button_text, (movement_button_rect.x + (movement_button_rect.width - movement_button_text.get_width()) // 2,
                                          movement_button_rect.y + (movement_button_rect.height - movement_button_text.get_height()) // 2))


    elif current_start_menu_sub_state == START_MENU_COLOR_PICKER:
        title_text = font_title.render("Color Picker (HSL)", True, colors.BLACK) # タイトルを変更
        dis.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4 - 50))

        # HSLスライダーの描画
        # H (色相)
        pygame.draw.rect(dis, colors.BLACK, h_slider_rect, 2)
        for i in range(h_slider_rect.width):
            h_preview = (i / h_slider_rect.width) * 360
            # SとLの値を反映させたグラデーションを表示
            preview_color = hsl_to_rgb(h_preview, s_value, l_value)
            pygame.draw.rect(dis, preview_color, (h_slider_rect.x + i, h_slider_rect.y, 1, h_slider_rect.height))
        h_handle_x = h_slider_rect.x + int((h_value / 360) * h_slider_rect.width)
        pygame.draw.circle(dis, colors.WHITE, (h_handle_x, h_slider_rect.centery), 12)
        pygame.draw.circle(dis, colors.BLACK, (h_handle_x, h_slider_rect.centery), 12, 2)
        h_label = font_input.render(f"Hue: {int(h_value)}", True, colors.BLACK)
        dis.blit(h_label, (h_slider_rect.x - h_label.get_width() - 10, h_slider_rect.centery - h_label.get_height() // 2))

        # S (彩度)
        pygame.draw.rect(dis, colors.BLACK, s_slider_rect, 2)
        for i in range(s_slider_rect.width):
            s_preview = (i / s_slider_rect.width) * 100
            # HとLの値を反映させたグラデーションを表示
            preview_color = hsl_to_rgb(h_value, s_preview, l_value)
            pygame.draw.rect(dis, preview_color, (s_slider_rect.x + i, s_slider_rect.y, 1, s_slider_rect.height))
        s_handle_x = s_slider_rect.x + int((s_value / 100) * s_slider_rect.width)
        pygame.draw.circle(dis, colors.WHITE, (s_handle_x, s_slider_rect.centery), 12)
        pygame.draw.circle(dis, colors.BLACK, (s_handle_x, s_slider_rect.centery), 12, 2)
        s_label = font_input.render(f"Saturation: {int(s_value)}", True, colors.BLACK)
        dis.blit(s_label, (s_slider_rect.x - s_label.get_width() - 10, s_slider_rect.centery - s_label.get_height() // 2))

        # L (明度)
        pygame.draw.rect(dis, colors.BLACK, l_slider_rect, 2)
        for i in range(l_slider_rect.width):
            l_preview = (i / l_slider_rect.width) * 100
            # HとSの値を反映させたグラデーションを表示
            preview_color = hsl_to_rgb(h_value, s_value, l_preview)
            pygame.draw.rect(dis, preview_color, (l_slider_rect.x + i, l_slider_rect.y, 1, l_slider_rect.height))
        l_handle_x = l_slider_rect.x + int((l_value / 100) * l_slider_rect.width)
        pygame.draw.circle(dis, colors.WHITE, (l_handle_x, l_slider_rect.centery), 12)
        pygame.draw.circle(dis, colors.BLACK, (l_handle_x, l_slider_rect.centery), 12, 2)
        l_label = font_input.render(f"Lightness: {int(l_value)}", True, colors.BLACK)
        dis.blit(l_label, (l_slider_rect.x - l_label.get_width() - 10, l_slider_rect.centery - l_label.get_height() // 2))

        # 現在の選択色を表示
        selected_color_preview_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 120, 100, 50)
        pygame.draw.rect(dis, current_selected_rgb_color, selected_color_preview_rect)
        pygame.draw.rect(dis, colors.BLACK, selected_color_preview_rect, 3)

        # メインメニューに戻るボタン
        pygame.draw.rect(dis, colors.GRAY, back_to_main_menu_button_rect)
        back_text = font_message.render("Back to Main Menu", True, colors.BLACK)
        dis.blit(back_text, (back_to_main_menu_button_rect.x + (back_to_main_menu_button_rect.width - back_text.get_width()) // 2,
                                    back_to_main_menu_button_rect.y + (back_to_main_menu_button_rect.height - back_text.get_height()) // 2))

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
    global selected_preset_color_index, selected_speed_str, active_input
    global h_value, s_value, l_value, current_selected_rgb_color
    global selected_movement_pattern_key, selected_movement_pattern_value
    global moving_point

    clock = pygame.time.Clock()
    
    # スライダーのドラッグ状態
    dragging_h = False
    dragging_s = False
    dragging_l = False
    
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
                        if current_start_menu_sub_state == START_MENU_COLOR_PICKER or \
                           current_start_menu_sub_state == START_MENU_MOVEMENT_PICKER:
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
                        # 色プレビューボックスのクリックでプリセットを切り替え
                        if MAIN_MENU_COLOR_PREVIEW_RECT.collidepoint(event.pos):
                            selected_preset_color_index = (selected_preset_color_index + 1) % len(colors.PRESET_COLORS_RGB)
                            current_selected_rgb_color = colors.PRESET_COLORS_RGB[selected_preset_color_index]
                            h_value, s_value, l_value = rgb_to_hsl(*current_selected_rgb_color)

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
                                    point_speed = 3
                                    selected_speed_str = "3"
                            except ValueError:
                                point_speed = 3
                                selected_speed_str = "3"
                            
                            # Initialize MovingPoint object
                            moving_point = MovingPoint(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                                                       current_selected_rgb_color, point_speed, 
                                                       SCREEN_WIDTH, SCREEN_HEIGHT)
                            
                            current_game_state = GAME_STATE_PLAYING
                            pygame.mouse.set_visible(False)
                        
                        # HSLカラーピッカーボタン (hsl_button_rectを使用)
                        if hsl_button_rect.collidepoint(event.pos):
                            current_start_menu_sub_state = START_MENU_COLOR_PICKER
                            
                        # Movement Picker Button
                        if movement_button_rect.collidepoint(event.pos):
                            current_start_menu_sub_state = START_MENU_MOVEMENT_PICKER

                    elif current_start_menu_sub_state == START_MENU_COLOR_PICKER:
                        # スライダーのドラッグ開始
                        if h_slider_rect.collidepoint(event.pos):
                            dragging_h = True
                        elif s_slider_rect.collidepoint(event.pos):
                            dragging_s = True
                        elif l_slider_rect.collidepoint(event.pos):
                            dragging_l = True
                        
                        # メインメニューに戻るボタン
                        if back_to_main_menu_button_rect.collidepoint(event.pos):
                            current_start_menu_sub_state = START_MENU_MAIN

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

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_h = False
                dragging_s = False
                dragging_l = False
                
            elif event.type == pygame.MOUSEMOTION:
                if current_start_menu_sub_state == START_MENU_COLOR_PICKER:
                    if dragging_h:
                        new_h_x = event.pos[0] - h_slider_rect.x
                        h_value = max(0, min(360, (new_h_x / h_slider_rect.width) * 360))
                        current_selected_rgb_color = hsl_to_rgb(h_value, s_value, l_value) # hsl_to_rgbを使用
                    elif dragging_s:
                        new_s_x = event.pos[0] - s_slider_rect.x
                        s_value = max(0, min(100, (new_s_x / s_slider_rect.width) * 100))
                        current_selected_rgb_color = hsl_to_rgb(h_value, s_value, l_value) # hsl_to_rgbを使用
                    elif dragging_l:
                        new_l_x = event.pos[0] - l_slider_rect.x
                        l_value = max(0, min(100, (new_l_x / l_slider_rect.width) * 100))
                        current_selected_rgb_color = hsl_to_rgb(h_value, s_value, l_value) # hsl_to_rgbを使用

        # 描画処理
        if current_game_state == GAME_STATE_START_MENU:
            draw_start_menu()
            pygame.mouse.set_visible(True)

        elif current_game_state == GAME_STATE_PLAYING:
            dis.fill(colors.WHITE) # ゲームプレイ中の背景色

            # Update the moving point based on the selected pattern
            if selected_movement_pattern_value == "random":
                moving_point.update_random()
            elif selected_movement_pattern_value == "up_to_down":
                moving_point.update_up_to_down()
            elif selected_movement_pattern_value == "down_to_up":
                moving_point.update_down_to_up()
            elif selected_movement_pattern_value == "right_to_left":
                moving_point.update_right_to_left()
            elif selected_movement_pattern_value == "left_to_right":
                moving_point.update_left_to_right()

            moving_point.draw(dis)
            
        pygame.display.update()
        clock.tick(60)

# ゲームを開始
if __name__ == "__main__":
    loop()