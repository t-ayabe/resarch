import cv2
import numpy as np

# グローバル変数
pts1 = []
click_count = 0

def click_event(event, x, y, flags, param):
    """
    マウスのクリックイベントを処理するコールバック関数
    """
    global pts1, click_count

    if event == cv2.EVENT_LBUTTONDOWN:
        if click_count < 4:
            # クリックした点をリストに追加
            pts1.append([x, y])
            click_count += 1
            print(f"Clicked point {click_count}: ({x}, {y})")

            # 画面に点を描画
            cv2.circle(img_copy, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Camera Feed - Click 4 Points", img_copy)

# カメラのキャプチャ
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# 最初のフレームを読み込み、コピーを作成
ret, img = cap.read()
if not ret:
    print("Error: Could not read frame from camera.")
    cap.release()
    exit()
img_copy = img.copy()

# ウィンドウを作成し、マウスイベントコールバックを設定
cv2.imshow("Camera Feed - Click 4 Points", img_copy)
cv2.setMouseCallback("Camera Feed - Click 4 Points", click_event)

print("Please click on the 4 corners of the monitor in the camera view.")
print("Press 'q' to quit.")

# ... (既存のコード) ...
# ユーザーが4つの点を選択するまで待機
while click_count < 4:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    
# 変換行列を計算
if len(pts1) == 4:
    # 変換先の座標を定義（Pygameの画面サイズに合わせる）
    # 左上、右上、右下、左下の順で指定
    SCREEN_WIDTH = 1920  # main.pyのSCREEN_WIDTHに合わせてください
    SCREEN_HEIGHT = 1080 # main.pyのSCREEN_HEIGHTに合わせてください
    pts2 = np.float32([[0, 0], [SCREEN_WIDTH, 0], [SCREEN_WIDTH, SCREEN_HEIGHT], [0, SCREEN_HEIGHT]])

    pts1 = np.float32(pts1)
    
    # 透視投影変換行列を計算
    M = cv2.getPerspectiveTransform(pts1, pts2)
    print("Transformation matrix (M):")
    print(M)
    
    # 変換行列をファイルに保存
    np.save("perspective_matrix.npy", M)
    print("Transformation matrix saved to perspective_matrix.npy")

# リソースを解放
cv2.destroyAllWindows()
cap.release()