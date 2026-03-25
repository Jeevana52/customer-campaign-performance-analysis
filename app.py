import os
import json
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "bank.csv")

def load_data():
    df = pd.read_csv(DATA_PATH, sep=";")
    df.columns = [c.strip().lower().replace('"', '').replace("'", "") for c in df.columns]
    # Clean string values
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip().str.replace('"', '').str.replace("'", "")
    return df

@app.route("/")
def index():
    df = load_data()

    total = len(df)
    yes_col = "y" if "y" in df.columns else df.columns[-1]
    yes_count = int((df[yes_col].str.lower() == "yes").sum())
    no_count = total - yes_count
    rate = round((yes_count / total) * 100, 1)

    # Profession / job breakdown
    job_col = "job" if "job" in df.columns else None
    prof_data = {}
    if job_col:
        grp = df.groupby(job_col)[yes_col].apply(lambda x: (x.str.lower() == "yes").sum())
        total_grp = df[job_col].value_counts()
        prof_data = {
            "labels": list(grp.index),
            "yes_counts": [int(v) for v in grp.values],
            "totals": [int(total_grp.get(k, 0)) for k in grp.index],
            "rates": [round(int(grp[k]) / int(total_grp.get(k, 1)) * 100, 1) for k in grp.index]
        }

    # Contact type breakdown
    contact_col = "contact" if "contact" in df.columns else None
    contact_data = {}
    if contact_col:
        c_grp = df.groupby(contact_col)[yes_col].apply(lambda x: (x.str.lower() == "yes").sum())
        c_total = df[contact_col].value_counts()
        contact_data = {
            "labels": list(c_grp.index),
            "rates": [round(int(c_grp[k]) / int(c_total.get(k, 1)) * 100, 1) for k in c_grp.index]
        }

    # Month trend
    month_col = "month" if "month" in df.columns else None
    month_order = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
    month_data = {}
    if month_col:
        m_grp = df.groupby(month_col)[yes_col].apply(lambda x: (x.str.lower() == "yes").sum())
        m_total = df[month_col].value_counts()
        sorted_months = [m for m in month_order if m in m_grp.index]
        month_data = {
            "labels": sorted_months,
            "rates": [round(int(m_grp.get(m, 0)) / int(m_total.get(m, 1)) * 100, 1) for m in sorted_months]
        }

    # Age distribution
    age_col = "age" if "age" in df.columns else None
    age_data = {}
    if age_col:
        bins = [18, 25, 35, 45, 55, 65, 100]
        labels = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        df["age_group"] = pd.cut(df[age_col], bins=bins, labels=labels, right=False)
        age_grp = df.groupby("age_group", observed=True)[yes_col].apply(lambda x: (x.str.lower() == "yes").sum())
        age_total = df["age_group"].value_counts()
        age_data = {
            "labels": labels,
            "rates": [round(int(age_grp.get(l, 0)) / int(age_total.get(l, 1)) * 100, 1) for l in labels]
        }

    return render_template(
        "index.html",
        total=f"{total:,}",
        yes_count=f"{yes_count:,}",
        no_count=f"{no_count:,}",
        rate=rate,
        prof_data=json.dumps(prof_data),
        contact_data=json.dumps(contact_data),
        month_data=json.dumps(month_data),
        age_data=json.dumps(age_data),
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
