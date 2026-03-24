from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly
import json

app = Flask(__name__)

@app.route("/")
def dashboard():
    df = pd.read_csv("data/bank.csv", sep=";")
    df.columns = df.columns.str.lower()

    summary = df.groupby("job")["y"].value_counts().unstack().fillna(0)

    if "yes" not in summary.columns:
        summary["yes"] = 0
    if "no" not in summary.columns:
        summary["no"] = 0

    summary["response_rate"] = summary["yes"] / (summary["yes"] + summary["no"])
    summary = summary.sort_values("response_rate", ascending=False)

    total_customers = len(df)
    total_yes = (df["y"] == "yes").sum()
    total_no = (df["y"] == "no").sum()
    response_rate = round((total_yes / total_customers) * 100, 2)

    fig = px.bar(
        summary.head(10),
        x=summary.head(10).index,
        y="response_rate",
        title="Top Customer Response Segments"
    )

    graphJSON = json.loads(plotly.io.to_json(fig))

    return render_template(
        "index.html",
        total_customers=total_customers,
        total_yes=total_yes,
        total_no=total_no,
        response_rate=response_rate,
        graphJSON=graphJSON
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
