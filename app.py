import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(layout="wide")
st.title("🩸 Blood Sample Compliance Dashboard")

# -----------------------------------
# File Path
# -----------------------------------
file1 = r"Final_Blood_ReportB.xlsx"

# -----------------------------------
# Read Excel
# -----------------------------------
df = pd.read_excel(file1)

# -----------------------------------
# Sidebar Filters
# -----------------------------------
st.sidebar.header("Filters")

locations = st.sidebar.multiselect(
    "Select Location(s)",
    options=sorted(df["loc_nurse_unit"].unique()),
    default=sorted(df["loc_nurse_unit"].unique())
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    options=sorted(df["month"].unique())
)

# -----------------------------------
# Apply Filters
# -----------------------------------
filtered_df = df[
    (df["loc_nurse_unit"].isin(locations)) &
    (df["month"] == selected_month)
]

# -----------------------------------
# KPI Calculations
# -----------------------------------
total_samples = len(filtered_df)

compliant_samples = len(
    filtered_df[filtered_df["volume_ml"] >= 5]
)

compliance_rate = (
    (compliant_samples / total_samples) * 100
    if total_samples > 0 else 0
)

# -----------------------------------
# KPI Display
# -----------------------------------
st.subheader("📌 Monthly Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Bottles", total_samples)
col2.metric("Bottles ≥ 5 mL", compliant_samples)
col3.metric("Compliance Rate (%)", f"{compliance_rate:.2f}%")

# -----------------------------------
# Location-wise Performance
# -----------------------------------
st.subheader("📊 Location-wise Performance")

location_summary = (
    filtered_df
    .groupby("loc_nurse_unit")
    .agg(
        Total=("volume_ml", "count"),
        Compliant=("volume_ml", lambda x: (x >= 5).sum())
    )
    .reset_index()
)

if not location_summary.empty:

    location_summary["Compliance %"] = (
        location_summary["Compliant"] /
        location_summary["Total"]
    ) * 100

    # Copy for charts
    location_chart = location_summary.copy()

    # Format for table (2 decimals)
    location_summary["Compliance %"] = location_summary["Compliance %"].map(lambda x: f"{x:.2f}")

    st.dataframe(location_summary)

    # -----------------------------------
    # Color coding
    # -----------------------------------
    colors = [
        "green" if val >= 90 else "red"
        for val in location_chart["Compliance %"]
    ]

    # -----------------------------------
    # Bar Chart
    # -----------------------------------
    fig1, ax1 = plt.subplots(figsize=(10,6))

    ax1.bar(
        location_chart["loc_nurse_unit"],
        location_chart["Compliance %"],
        color=colors
    )

    # Target line at 90%
    ax1.axhline(
        y=90,
        color="blue",
        linestyle="--",
        linewidth=2,
        label="Target 90%"
    )

    ax1.set_ylabel("Compliance %")
    ax1.set_title("Compliance Rate per Location")

    plt.xticks(rotation=45, ha="right")
    plt.subplots_adjust(bottom=0.30)

    ax1.legend()

    st.pyplot(fig1)

else:
    st.warning("No data available for selected filters.")

# -----------------------------------
# Location-wise Bottles > 10 mL
# -----------------------------------
st.subheader("🧪 Locations with Bottles > 10 mL")

above_10_summary = (
    filtered_df
    .groupby("loc_nurse_unit")
    .agg(
        Total=("volume_ml", "count"),
        Above_10ml=("volume_ml", lambda x: (x > 10).sum())
    )
    .reset_index()
)

above_10_summary = above_10_summary[above_10_summary["Above_10ml"] > 0]

if not above_10_summary.empty:

    above_10_summary["> 10 mL %"] = (
        above_10_summary["Above_10ml"] /
        above_10_summary["Total"]
    ) * 100

    st.dataframe(
        above_10_summary.assign(
            **{"> 10 mL %": above_10_summary["> 10 mL %"].map(lambda x: f"{x:.2f}")}
        )
    )

    fig3, ax3 = plt.subplots(figsize=(10,6))

    ax3.bar(
        above_10_summary["loc_nurse_unit"],
        above_10_summary["> 10 mL %"]
    )

    ax3.set_ylabel("Percentage of Bottles > 10 mL")
    ax3.set_xlabel("Location")
    ax3.set_title("Percentage of Bottles Greater Than 10 mL by Location")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    st.pyplot(fig3)

else:
    st.info("No locations found with bottles greater than 10 mL for the selected filters.")

# -----------------------------------
# Monthly Compliance Trend by Location
# -----------------------------------
st.subheader("📈 Monthly Compliance Trend by Location")

trend_df = df[df["loc_nurse_unit"].isin(locations)]

monthly_location_summary = (
    trend_df
    .groupby(["month", "loc_nurse_unit"])
    .agg(
        Total=("volume_ml", "count"),
        Compliant=("volume_ml", lambda x: (x >= 5).sum())
    )
    .reset_index()
)

monthly_location_summary["Compliance %"] = (
    monthly_location_summary["Compliant"] /
    monthly_location_summary["Total"]
) * 100

monthly_location_summary = monthly_location_summary.sort_values("month")

# -----------------------------------
# Trend Chart
# -----------------------------------
fig2, ax2 = plt.subplots(figsize=(10,6))

for location in monthly_location_summary["loc_nurse_unit"].unique():

    location_data = monthly_location_summary[
        monthly_location_summary["loc_nurse_unit"] == location
    ]

    ax2.plot(
        location_data["month"],
        location_data["Compliance %"],
        marker="o",
        linewidth=2,
        label=location
    )

# Target line for compliance
ax2.axhline(
    y=90,
    color="blue",
    linestyle="--",
    linewidth=2,
    label="Target 90%"
)

ax2.set_ylabel("Compliance %")
ax2.set_xlabel("Month")
ax2.set_title("Monthly Compliance Trend by Location")

plt.xticks(rotation=45)

# Move legend outside
ax2.legend(
    title="Location",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.tight_layout()

st.pyplot(fig2)
