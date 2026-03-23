import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Customer Campaign Analytics",
    layout="wide"
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
df = pd.read_csv("data/bank.csv", sep=";")
df.columns = df.columns.str.lower()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Dashboard Controls")

job_filter = st.sidebar.multiselect(
    "Select Profession",
    options=df["job"].unique(),
    default=["management", "technician", "student"]
)

df = df[df["job"].isin(job_filter)]

# ---------------- KPI METRICS ----------------
total_customers = len(df)
total_yes = (df["y"] == "yes").sum()
total_no = (df["y"] == "no").sum()
response_rate = round((total_yes / total_customers) * 100, 2)

# ---------------- TITLE ----------------
st.title("📈 Customer Campaign Performance Dashboard")

# ---------------- KPI CARDS ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", f"{total_customers:,}")
col2.metric("Positive Responses", f"{total_yes:,}")
col3.metric("Negative Responses", f"{total_no:,}")
col4.metric("Response Rate", f"{response_rate}%")

st.divider()

# ---------------- RESPONSE BY JOB ----------------
job_summary = df.groupby("job")["y"].value_counts().unstack().fillna(0)
job_summary["response_rate"] = job_summary["yes"] / (job_summary["yes"] + job_summary["no"])
job_summary = job_summary.sort_values("response_rate", ascending=False)

# ---------------- CHART ROW ----------------
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        job_summary.head(10),
        x=job_summary.head(10).index,
        y="response_rate",
        title="Top Response Segments",
        color="response_rate",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    pie = px.pie(
        names=["Yes", "No"],
        values=[total_yes, total_no],
        title="Campaign Outcome Distribution",
        hole=0.55
    )
    st.plotly_chart(pie, use_container_width=True)

st.divider()

# ---------------- TREND ANALYSIS ----------------
col3, col4 = st.columns(2)

with col3:
    fig_line = px.line(
        job_summary.head(10),
        y="response_rate",
        title="Segment Response Trend",
        markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col4:
    fig_stack = go.Figure()

    fig_stack.add_bar(
        x=job_summary.head(10).index,
        y=job_summary.head(10)["yes"],
        name="Yes"
    )

    fig_stack.add_bar(
        x=job_summary.head(10).index,
        y=job_summary.head(10)["no"],
        name="No"
    )

    fig_stack.update_layout(
        barmode="stack",
        title="Response Comparison"
    )

    st.plotly_chart(fig_stack, use_container_width=True)

st.divider()

# ---------------- INSIGHTS ----------------
best_job = job_summary.index[0]
best_rate = round(job_summary.iloc[0]["response_rate"] * 100, 2)

st.subheader("📌 Key Insights")

st.success(f"Highest engagement came from **{best_job}** customers.")
st.info(f"Response rate for this segment is **{best_rate}%**.")
st.warning("Segments with low engagement may require targeted messaging or personalized marketing strategies.")

# ---------------- DOWNLOAD BUTTON ----------------
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Filtered Report",
    csv,
    "campaign_report.csv",
    "text/csv"
)