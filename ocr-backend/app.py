from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ✅ REQUIRED for Web (CORS)

@app.route("/ocr-url", methods=["POST"])
def ocr():
    data = request.json
    file_url = data.get("file_url")
    doc_type = data.get("doc_type")

    # --- your OCR logic here ---
    return jsonify({
        "success": True,
        "expiry_date": "Not detected",
        "extracted_text": "sample text"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)  # ✅ VERY IMPORTANT