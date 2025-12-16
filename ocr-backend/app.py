from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
)
  # ✅ REQUIRED for Web (CORS)

@app.route("/ocr-url", methods=["POST", "OPTIONS"])

def ocr():
    if request.method == "OPTIONS":
     return "", 200
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