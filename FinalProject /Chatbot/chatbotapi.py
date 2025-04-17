from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)

# Load the model and define global variables
X_train = np.array([
    # Flu examples - fever, cough, fatigue
    [1, 1, 0, 1, 0, 0],
    [1, 1, 1, 1, 0, 0],
    [1, 0, 0, 1, 0, 0],
    # Cold examples - cough, sneezing
    [0, 1, 1, 0, 0, 0],
    [0, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 0, 0],
    # COVID-19 examples - fever, cough, loss of taste
    [1, 1, 0, 0, 1, 0],
    [1, 1, 0, 1, 1, 0],
    [1, 0, 0, 1, 1, 0],
    # Allergy examples - sneezing, itchy eyes
    [0, 0, 1, 0, 0, 1],
    [0, 1, 1, 0, 0, 1],
    [0, 0, 1, 1, 0, 1]
], dtype=np.float32)

y_train = tf.keras.utils.to_categorical([0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3], num_classes=4)
diseases = ["Flu", "Cold", "COVID-19", "Allergy"]
symptom_names = ["Fever", "Cough", "Sneezing", "Fatigue", "Loss of Taste", "Itchy Eyes"]


# Model definition and training functions
def build_model():
    inputs = tf.keras.Input(shape=(6,))
    x = tf.keras.layers.Dense(16, activation='relu')(inputs)
    x = tf.keras.layers.Dropout(0.5)(x)
    x = tf.keras.layers.Dense(16, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    outputs = tf.keras.layers.Dense(4, activation='softmax')(x)
    return tf.keras.Model(inputs, outputs)


def predict_with_uncertainty(model, x, n_iter=100):
    preds = []
    for _ in range(n_iter):
        # Apply Monte Carlo Dropout during inference for uncertainty estimation
        pred = model(x, training=True).numpy()
        preds.append(pred)
    preds = np.array(preds)
    mean = preds.mean(axis=0)
    std = preds.std(axis=0)
    return mean, std


def generate_plot(mean_probs, std_probs):
    plt.figure(figsize=(10, 6))
    plt.bar(diseases, mean_probs[0], yerr=std_probs[0], capsize=5, color='skyblue')
    plt.ylabel("Probability")
    plt.title("Diagnosis Confidence")

    # Save plot to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return plot_data


# Initialize the model
model = build_model()
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=100, verbose=0)


# API endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint to check if the service is running"""
    return jsonify({"status": "healthy"}), 200


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Main endpoint for diagnosing based on symptoms"""
    # Get symptoms from request
    try:
        data = request.get_json()
        if not data or 'symptoms' not in data:
            return jsonify({"error": "No symptoms provided"}), 400
        # Validate and extract symptoms
        symptoms = data['symptoms']
        # Check if symptoms format is correct
        if isinstance(symptoms, dict):
            # Convert symptoms dict to array in correct order
            input_symptoms = []
            for name in symptom_names:
                input_symptoms.append(1 if symptoms.get(name.lower(), False) else 0)
        elif isinstance(symptoms, list) and len(symptoms) == 6:
            input_symptoms = symptoms
        else:
            return jsonify({"error": "Invalid symptoms format"}), 400

        # Make prediction
        input_array = np.array([input_symptoms], dtype=np.float32)
        mean_probs, std_probs = predict_with_uncertainty(model, input_array)
        most_likely = np.argmax(mean_probs)
        diagnosis = diseases[most_likely]

        # Create confidence score
        confidence = float(mean_probs[0][most_likely])
        uncertainty = float(std_probs[0][most_likely])

        # Determine confidence level
        confidence_level = "high" if confidence > 0.7 and uncertainty < 0.1 else \
            "medium" if confidence > 0.5 and uncertainty < 0.2 else "low"

        # Get recommendations
        test_map = {
            "Flu": "Influenza A/B test",
            "Cold": "Nasal swab",
            "COVID-19": "PCR test",
            "Allergy": "Allergy skin test"
        }
        medicine_map = {
            "Flu": "Oseltamivir (Tamiflu)",
            "Cold": "Rest, fluids, antihistamines",
            "COVID-19": "Isolation + Paracetamol",
            "Allergy": "Loratadine or Cetirizine"
        }

        # Generate plot
        plot_data = generate_plot(mean_probs, std_probs)

        # Format detailed probabilities
        probabilities = {}
        for i, dis in enumerate(diseases):
            probabilities[dis] = {
                "probability": float(mean_probs[0][i]),
                "uncertainty": float(std_probs[0][i])
            }

        result = {
            "diagnosis": diagnosis,
            "confidence_level": confidence_level,
            "confidence_score": confidence,
            "uncertainty": uncertainty,
            "recommendation": {
                "test": test_map[diagnosis],
                "treatment": medicine_map[diagnosis]
            },
            "detailed_probabilities": probabilities,
            "plot": plot_data
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Return the list of symptoms the model can analyze"""
    return jsonify({"symptoms": symptom_names}), 200

from flask import render_template

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)