# pages/csv_analytics.py
#
# Tab 2: Waste Analytics Dashboard
#
# What this page does:
#   1. Lets the user upload a campus waste CSV (or loads the bundled sample)
#   2. Validates that the CSV has the expected columns
#   3. Provides simple sidebar filters (date range, location, waste type)
#   4. Shows 4 KPI metrics at the top
#   5. Displays 4 Plotly charts:
#       - Waste by category (bar chart)
#       - Waste trend over time (line chart)
#       - Waste by location (horizontal bar)
#       - Correct vs incorrect disposal (pie chart)
#   6. Optionally asks the AI assistant to summarise the key insights

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from utils.watsonx_client import generate_text, is_text_ai_available
from utils.waste_categories import ASSISTANT_SYSTEM_PROMPT

# Columns the app expects in the CSV.
# The validation step below gives a clear error if any are missing.
REQUIRED_COLUMNS = {"date", "location", "waste_type", "weight_kg", "disposed_correctly"}

# Path to the bundled sample dataset
SAMPLE_CSV_PATH = Path(__file__).parent.parent / "data" / "sample_campus_waste.csv"


def _load_and_validate(file) -> tuple[pd.DataFrame | None, str | None]:
    """
    Load a CSV file into a Pandas DataFrame and validate its structure.
    Returns (dataframe, None) on success or (None, error_message) on failure.
    """
    try:
        df = pd.read_csv(file)
    except Exception as exc:
        return None, f"Could not read the CSV file: {exc}"

    missing = REQUIRED_COLUMNS - set(df.columns.str.lower().tolist())
    if missing:
        return None, (
            f"The CSV is missing these required columns: **{', '.join(sorted(missing))}**  \n"
            f"Required columns: `date`, `location`, `waste_type`, `weight_kg`, "
            f"`disposed_correctly`"
        )

    # Normalise column names to lowercase
    df.columns = df.columns.str.lower()

    # Parse date column; rows with invalid dates are dropped with a warning.
    # format="mixed" tells Pandas to try each value individually without
    # raising a UserWarning, while errors="coerce" turns bad values into NaT.
    df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
    n_invalid = df["date"].isna().sum()
    df = df.dropna(subset=["date"])

    # Normalise waste_type to lowercase for consistent filtering
    df["waste_type"] = df["waste_type"].str.lower().str.strip()
    df["location"]   = df["location"].str.strip()

    # Convert disposed_correctly to boolean
    df["disposed_correctly"] = df["disposed_correctly"].apply(
        lambda v: str(v).strip().lower() in ("true", "1", "yes")
    )

    return df, (
        f"⚠️ {n_invalid} row(s) had invalid dates and were skipped."
        if n_invalid > 0
        else None
    )


def _build_summary_prompt(df: pd.DataFrame) -> str:
    """
    Build a short text summary of the data to send to the AI for insight generation.
    We never send raw CSV rows – only aggregated statistics.
    """
    total_kg      = df["weight_kg"].sum()
    top_type      = df.groupby("waste_type")["weight_kg"].sum().idxmax()
    top_location  = df.groupby("location")["weight_kg"].sum().idxmax()
    correct_pct   = df["disposed_correctly"].mean() * 100
    n_days        = df["date"].nunique()

    return (
        f"Campus waste data summary ({n_days} days of records):\n"
        f"- Total waste recorded: {total_kg:.1f} kg\n"
        f"- Largest waste category by weight: {top_type}\n"
        f"- Location producing the most waste: {top_location}\n"
        f"- Percentage disposed correctly: {correct_pct:.1f}%\n\n"
        "In 3–5 concise bullet points, what are the key sustainability insights "
        "from this data and what practical actions should the campus take?"
    )


def render() -> None:
    """Main render function called by app.py."""

    st.subheader("📊 Waste Analytics Dashboard")
    st.markdown(
        "Upload your campus waste CSV to visualise patterns and identify "
        "opportunities to improve waste management."
    )

    # -----------------------------------------------------------------------
    # FILE UPLOAD / SAMPLE DATA
    # -----------------------------------------------------------------------

    col_upload, col_sample = st.columns([2, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload campus waste CSV",
            type=["csv"],
            help=(
                "The CSV must have columns: date, location, waste_type, "
                "weight_kg, disposed_correctly"
            ),
        )

    with col_sample:
        st.markdown(" ")   # vertical spacing
        use_sample = st.button(
            "📂 Load sample data",
            help="Loads the bundled 100-row demo dataset so you can explore the dashboard.",
        )

    # Decide which file to load
    source_file = None
    source_label = ""

    if uploaded_file is not None:
        source_file  = uploaded_file
        source_label = f"Uploaded file: `{uploaded_file.name}`"
    elif use_sample or st.session_state.get("analytics_using_sample"):
        source_file  = SAMPLE_CSV_PATH
        source_label = "📂 Using bundled sample dataset (`data/sample_campus_waste.csv`)"
        st.session_state["analytics_using_sample"] = True

    if source_file is None:
        st.markdown("👆 Upload a CSV or click **Load sample data** to begin.")
        st.markdown(
            "**Expected CSV format:**\n"
            "```\ndate,location,waste_type,weight_kg,disposed_correctly\n"
            "2024-01-08,Cafeteria,food,4.2,True\n```"
        )
        return

    # -----------------------------------------------------------------------
    # LOAD AND VALIDATE
    # -----------------------------------------------------------------------

    df, warning = _load_and_validate(source_file)

    if df is None:
        # warning contains the error message when df is None
        st.error(warning)
        return

    if warning:
        st.warning(warning)

    st.caption(source_label)
    st.caption(f"Loaded {len(df):,} records from {df['date'].min().date()} to {df['date'].max().date()}")

    # -----------------------------------------------------------------------
    # FILTERS  (sidebar section)
    # -----------------------------------------------------------------------

    with st.expander("🔍 Filters", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            min_date = df["date"].min().date()
            max_date = df["date"].max().date()
            date_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )

        with col_f2:
            all_locations = sorted(df["location"].unique())
            selected_locations = st.multiselect(
                "Location",
                options=all_locations,
                default=all_locations,
            )

        with col_f3:
            all_types = sorted(df["waste_type"].unique())
            selected_types = st.multiselect(
                "Waste type",
                options=all_types,
                default=all_types,
            )

    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[
            (df["date"].dt.date >= start_date) &
            (df["date"].dt.date <= end_date)
        ]

    if selected_locations:
        df = df[df["location"].isin(selected_locations)]

    if selected_types:
        df = df[df["waste_type"].isin(selected_types)]

    if df.empty:
        st.warning("No data matches the selected filters. Try broadening your selection.")
        return

    # -----------------------------------------------------------------------
    # KPI METRICS
    # -----------------------------------------------------------------------

    st.markdown("### Key Metrics")
    k1, k2, k3, k4 = st.columns(4)

    total_kg      = df["weight_kg"].sum()
    correct_pct   = df["disposed_correctly"].mean() * 100
    n_records     = len(df)
    top_type      = df.groupby("waste_type")["weight_kg"].sum().idxmax()

    k1.metric("Total Waste Recorded", f"{total_kg:.1f} kg")
    k2.metric("Correctly Disposed",   f"{correct_pct:.1f}%")
    k3.metric("Total Records",        f"{n_records:,}")
    k4.metric("Top Waste Category",   top_type.capitalize())

    st.divider()

    # -----------------------------------------------------------------------
    # CHARTS
    # -----------------------------------------------------------------------

    st.markdown("### Charts")

    chart_col1, chart_col2 = st.columns(2)

    # Chart 1 – Waste by category (bar)
    with chart_col1:
        by_type = (
            df.groupby("waste_type")["weight_kg"]
            .sum()
            .reset_index()
            .rename(columns={"waste_type": "Waste Type", "weight_kg": "Total (kg)"})
            .sort_values("Total (kg)", ascending=False)
        )
        fig1 = px.bar(
            by_type,
            x="Waste Type",
            y="Total (kg)",
            title="Total Waste by Category",
            color="Waste Type",
            text_auto=".1f",
        )
        fig1.update_layout(showlegend=False, xaxis_title="", yaxis_title="kg")
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2 – Correct vs incorrect disposal (pie)
    with chart_col2:
        disposal_counts = (
            df["disposed_correctly"]
            .map({True: "Correctly Disposed", False: "Incorrectly Disposed"})
            .value_counts()
            .reset_index()
        )
        disposal_counts.columns = ["Disposal", "Count"]
        fig2 = px.pie(
            disposal_counts,
            names="Disposal",
            values="Count",
            title="Disposal Behaviour",
            color="Disposal",
            color_discrete_map={
                "Correctly Disposed":   "#16A34A",
                "Incorrectly Disposed": "#DC2626",
            },
        )
        st.plotly_chart(fig2, use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)

    # Chart 3 – Weekly trend over time (line)
    with chart_col3:
        df_trend = df.copy()
        df_trend["week"] = df_trend["date"].dt.to_period("W").apply(lambda r: r.start_time)
        weekly = (
            df_trend.groupby(["week", "waste_type"])["weight_kg"]
            .sum()
            .reset_index()
            .rename(columns={"week": "Week", "waste_type": "Waste Type", "weight_kg": "kg"})
        )
        fig3 = px.line(
            weekly,
            x="Week",
            y="kg",
            color="Waste Type",
            title="Waste Trend by Week",
            markers=True,
        )
        fig3.update_layout(xaxis_title="", yaxis_title="kg per week")
        st.plotly_chart(fig3, use_container_width=True)

    # Chart 4 – Waste by location (horizontal bar)
    with chart_col4:
        by_location = (
            df.groupby("location")["weight_kg"]
            .sum()
            .reset_index()
            .rename(columns={"location": "Location", "weight_kg": "Total (kg)"})
            .sort_values("Total (kg)")
        )
        fig4 = px.bar(
            by_location,
            x="Total (kg)",
            y="Location",
            orientation="h",
            title="Total Waste by Location",
            text_auto=".1f",
        )
        fig4.update_layout(yaxis_title="", xaxis_title="kg")
        st.plotly_chart(fig4, use_container_width=True)

    # -----------------------------------------------------------------------
    # AI INSIGHT SUMMARY (optional, shown only if text AI is available)
    # -----------------------------------------------------------------------

    st.divider()
    st.markdown("### 🤖 AI Insight Summary")

    if not is_text_ai_available():
        st.info(
            "Configure `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` in your `.env` file "
            "to enable AI-generated insights for this data."
        )
        return

    if st.button("Generate AI insights from this data"):
        with st.spinner("Asking IBM Granite to summarise the data patterns..."):
            summary_prompt = _build_summary_prompt(df)
            response, error = generate_text(
                prompt=summary_prompt,
                system_prompt=ASSISTANT_SYSTEM_PROMPT,
                max_new_tokens=400,
            )

        if error:
            st.error(f"Could not generate insights: {error}")
        else:
            st.markdown(response)
            st.caption(
                "🤖 Generated by IBM Granite (ibm/granite-3-3-8b-instruct) via watsonx.ai. "
                "Review before acting on these suggestions."
            )
