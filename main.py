from flask import Flask, render_template, request
from core.analyzer import analyze_text

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    score = None
    description = None
    input_text = ""
    if request.method == "POST":
        input_text = request.form.get("text", "")
        if input_text:
            try:
                result = analyze_text(input_text)
                score = round(result["score"] * 100, 1)
                description = result["text"]
            except Exception as e:
                score = f"Error: {str(e)}"
    return render_template("index.html", score=score, description=description, text=input_text)


if __name__ == "__main__":
    app.run(debug=True)
