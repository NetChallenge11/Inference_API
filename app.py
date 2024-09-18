## 온전한 Alexnet 모델 추론 API
## 전체 추론 시간 과 전체 처리 시간
## 총 2가지 측정

from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import time

app = Flask(__name__)

# H5 파일로부터 모델 로드
MODEL_PATH = 'model/head-alexnet-split-layer-1.h5'
model = tf.keras.models.load_model(MODEL_PATH)

# 이미지 전처리 함수 (모델에 맞는 크기로 변환 및 Alpha 채널 제거)
def preprocess_image(image):
    # 이미지가 RGBA 또는 다른 형식이면 RGB로 변환
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # 이미지를 250x250 크기로 리사이즈
    image = image.resize((250, 250))
    
    # 이미지 데이터를 numpy 배열로 변환
    image = np.array(image) / 255.0  # 0-255 값 -> 0-1로 정규화
    
    # 모델 입력에 맞게 차원 추가 (배치 차원)
    image = np.expand_dims(image, axis=0)  # (1, 250, 250, 3) 형태로 변환
    return image

# 예측 API 엔드포인트
@app.route('/predict', methods=['POST'])
def predict():
    # 시간 측정 시작 (전체 처리 시간)
    start_time_total = time.time()

    # POST 요청에서 이미지를 가져옴
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    # 이미지 파일 로드
    file = request.files['file']

    try:
        # 시간 측정 시작 (모델 추론 시간)
        start_time_inference = time.time()

        # 이미지를 열고 전처리
        image = Image.open(io.BytesIO(file.read()))
        processed_image = preprocess_image(image)

        # 모델 예측 수행
        prediction = model.predict(processed_image)

        # 모델 추론 시간 측정 종료 및 경과 시간 계산
        end_time_inference = time.time()
        elapsed_time_inference = end_time_inference - start_time_inference

        # 전체 처리 시간 측정 종료 및 경과 시간 계산
        end_time_total = time.time()
        elapsed_time_total = end_time_total - start_time_total

        # 로그 출력 (선택 사항)
        app.logger.debug(f"Inference time: {elapsed_time_inference} seconds")
        app.logger.debug(f"Total processing time (including response preparation): {elapsed_time_total} seconds")

        # 예측 결과 반환
        return jsonify({'prediction': prediction.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
