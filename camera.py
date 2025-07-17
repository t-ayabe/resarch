import cv2
import numpy as np
import datetime
import time
import os

# 変換行列を読み込み (camera.pyから追加)
try:
    M = np.load("perspective_matrix.npy")
    print("Transformation matrix loaded successfully.")
except FileNotFoundError:
    print("Error: perspective_matrix.npy not found. Please run calibration_script.py first.")
    exit()

# iVCamがPCのWebカメラとして認識されているインデックスを確認
camera_index = 0

# VideoCaptureオブジェクトを作成
cap = cv2.VideoCapture(camera_index)

# カメラが正しく開かれたか確認
if not cap.isOpened():
    print("エラー: カメラを開けませんでした。camera_index を確認してください。")
    exit()

now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_directory = r"C:\Users\tayav\Documents\resarch\output_videos"
os.makedirs(output_directory, exist_ok=True)
output_file = os.path.join(output_directory, f"fish_{now}.mp4")

# 映像のフレームサイズとFPSを取得
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"フレームサイズ: {frame_width}x{frame_height}, FPS: {fps}")

# 映像を保存するためのVideoWriterオブジェクトを作成
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

print("録画を開始しました。'q' キーを押すと終了します。")

while(cap.isOpened()):
    # フレームを読み込み
    ret, frame = cap.read()
    
    if ret:
        # camera.pyから追加: 映像の中心点を取得し、座標変換を適用
        center_x = frame_width // 2
        center_y = frame_height // 2
        
        # 取得した座標を変換
        src_point = np.float32([[center_x, center_y]]).reshape(-1, 1, 2)
        dst_point = cv2.perspectiveTransform(src_point, M)
        
        # 変換後の座標を取得
        transformed_x = int(dst_point[0][0][0])
        transformed_y = int(dst_point[0][0][1])

        # 変換された座標をコンソールに出力 (camera.pyから追加)
        print(f"Transformed point: ({transformed_x}, {transformed_y})")

        # 映像をファイルに書き込む
        out.write(frame)
        
        # リアルタイムで映像を表示（任意）
        cv2.imshow('iVCam Live', frame)
        
        # 'q' キーが押されたらループを抜ける
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# すべての処理が完了したら、オブジェクトを解放
cap.release()
out.release()
cv2.destroyAllWindows()

print("録画が終了しました。'output.mp4' ファイルが保存されました。")