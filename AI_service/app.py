from flask import Flask, request, jsonify
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np

# Khởi tạo Flask app
app = Flask(__name__)

# Tải mô hình RNN đã lưu
model_rnn = tf.keras.models.load_model(
    'model_rnn.h5',
    compile=False  # Don't load the optimizer configuration
)

# Recompile the model with a compatible optimizer
model_rnn.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Tải tokenizer đã huấn luyện
# Replace the tokenizer loading code with this
try:
    with open('tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
except ModuleNotFoundError:
    # Recreate tokenizer if loading fails
    print("Recreating tokenizer from data...")

    data = pd.read_csv('v3_sentences_pseudo_with_ids.csv')
    # Thêm cột user_id và clothes_id với giá trị ngẫu nhiên từ 1 đến 100
    data['user_id'] = np.random.randint(1, 101, size=len(data))
    data['clothes_id'] = np.random.randint(1, 101, size=len(data))
    import re


    # Chuẩn hóa văn bản
    def normalize_text(text):
        text = re.sub(r'\W+', ' ', text)
        text = text.lower()
        return text


    data['text_normalized'] = data['txt'].apply(normalize_text)
    texts = data['text_normalized'].values
    labels = data['lbl'].values
    tokenizer = Tokenizer(num_words=10000)
    tokenizer.fit_on_texts(texts)

    # Save the new tokenizer
    with open('tokenizer_new.pkl', 'wb') as f:
        pickle.dump(tokenizer, f)
    print("New tokenizer saved as tokenizer_new.pkl")

# Định nghĩa các tham số cho bộ mã hóa đầu vào (Input encoding)
MAX_LEN = 100  # Chiều dài tối đa của chuỗi

# Đọc dữ liệu từ file CSV chứa các đánh giá
data = pd.read_csv('v3_sentences_pseudo_with_ids.csv')

# Hàm dự đoán bình luận
def predict_comment(comment):
    # Tiền xử lý bình luận
    comment_seq = tokenizer.texts_to_sequences([comment])
    comment_padded = pad_sequences(comment_seq, maxlen=MAX_LEN, padding='pre')
    
    # Dự đoán với mô hình RNN
    prediction = model_rnn.predict(comment_padded)
    
    # Chuyển đổi dự đoán thành nhị phân (0 hoặc 1)
    if prediction[0] > 0.5:
        return [1]  # Tích cực
    else:
        return [0]  # Tiêu cực

# Định nghĩa route Flask để dự đoán bình luận
@app.route('/predict', methods=['POST'])
def predict():
    # Lấy dữ liệu bình luận từ request
    data = request.get_json()
    comment = data.get('comment', '')

    if not comment:
        return jsonify({'error': 'Không có bình luận được gửi'}), 400

    # Dự đoán kết quả cho bình luận
    result = predict_comment(comment)

    # Trả kết quả về cho người dùng dưới dạng JSON
    return jsonify({'prediction': result})

# Định nghĩa route Flask để gợi ý sản phẩm
@app.route('/recomment', methods=['POST'])
def recomment():
    try:
        # Lấy dữ liệu từ request
        request_data = request.get_json()
        user_id = request_data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Đọc dữ liệu từ CSV
        data = pd.read_csv('v3_sentences_pseudo_with_ids.csv')

        # Đảm bảo user_id tồn tại trong dataset
        if user_id not in data['user_id'].unique():
            return jsonify({'error': f'No data found for user_id {user_id}'}), 404

        # Lọc ra những sản phẩm mà user đã đánh giá tiêu cực (lbl = 0)
        user_negative_reviews = data[(data['user_id'] == user_id) & (data['lbl'] == 0)]
        negative_clothes_ids = user_negative_reviews['clothes_id'].tolist()

        # Loại bỏ những sản phẩm bị đánh giá tiêu cực bởi user_id
        filtered_data = data[~data['clothes_id'].isin(negative_clothes_ids)]

        # Tính tỷ lệ đánh giá tích cực của từng sản phẩm
        positive_rate = (
            filtered_data.groupby('clothes_id')['lbl']
            .mean()  # Tính trung bình của lbl = 1 (số lượt đánh giá tích cực / tổng số đánh giá)
            .reset_index()
        )

        # Lấy 10 sản phẩm có tỷ lệ đánh giá tích cực cao nhất
        top_products = positive_rate.nlargest(10, 'lbl')

        # Trả về danh sách sản phẩm có tỉ lệ đánh giá tích cực cao nhất
        recommendations = top_products.rename(columns={'lbl': 'positive_rate'}).to_dict(orient='records')

        return jsonify({'recommendations': recommendations})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Chạy Flask app
if __name__ == '__main__':
    app.run(debug=True)
