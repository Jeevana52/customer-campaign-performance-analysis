import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/bank.csv", sep=';')

# Clean column names
df.columns = df.columns.str.lower()

# Group by job and campaign response
summary = df.groupby("job")["y"].value_counts().unstack().fillna(0)

# Calculate response rate
summary["response_rate"] = summary["yes"] / (summary["yes"] + summary["no"])

# Sort highest response
summary = summary.sort_values("response_rate", ascending=False)

# Save excel report
summary.to_excel("reports/summary.xlsx")

# Plot chart
summary["response_rate"].plot(kind="bar")

plt.title("Campaign Response Rate by Job")
plt.tight_layout()
plt.savefig("reports/response_chart.png")

print(summary)