import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Fitness Tracker", layout="wide", page_icon="🏋️")
st.title("🏋️ Fitness Tracker Dashboard")
st.caption("50 users · July 1–20 2024 · Filtered view updates all charts and insights")

SLEEP_COLOURS = {
    "Poor": "#e74c3c",
    "Fair": "#f39c12",
    "Good": "#3498db",
    "Excellent": "#2ecc71",
}

WORKOUT_TYPES = ["Cycling", "Yoga", "Running", "Weightlifting", "Rest", "HIIT"]
SLEEP_LEVELS = ["Poor", "Fair", "Good", "Excellent"]


@st.cache_data
def load_data():
    df = pd.read_excel("data/fitness_tracker.xlsx", parse_dates=["Date"])
    df["Net Calories"] = df["Calories Consumed"] - df["Calories Burned"]
    return df


df_all = load_data()

# ── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Filters")
    st.caption("Select 'All' or pick specific values")

    workout_sel = st.multiselect(
        "Workout Type",
        options=["All"] + WORKOUT_TYPES,
        default=["All"],
    )
    sleep_sel = st.multiselect(
        "Sleep Quality",
        options=["All"] + SLEEP_LEVELS,
        default=["All"],
    )

# "All" selected or nothing selected → use all values
wf = WORKOUT_TYPES if (not workout_sel or "All" in workout_sel) else workout_sel
sf = SLEEP_LEVELS if (not sleep_sel or "All" in sleep_sel) else sleep_sel

df = df_all[df_all["Workout Type"].isin(wf) & df_all["Sleep Quality"].isin(sf)]

# ── BAN cards ────────────────────────────────────────────────────────────────
st.subheader("Fitness Overview")

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

total_steps = int(df["Steps Count"].sum())
avg_daily_steps = int(df.groupby("Date")["Steps Count"].mean().mean())
cal_burned = int(df["Calories Burned"].sum())
cal_consumed = int(df["Calories Consumed"].sum())
net_cal = cal_consumed - cal_burned
avg_sleep = round(df["Sleep Duration (Hours)"].mean(), 1)
num_users = df["User ID"].nunique()

def fmt(n):
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

c1.metric("Users", num_users)
c2.metric("Total Steps", fmt(total_steps))
c3.metric("Avg Daily Steps", fmt(avg_daily_steps))
c4.metric("Calories Burned", fmt(cal_burned))
c5.metric("Cal. Consumed", fmt(cal_consumed))
c6.metric("Net Calories", fmt(net_cal), delta="surplus" if net_cal > 0 else "deficit", delta_color="inverse")
c7.metric("Avg Sleep", f"{avg_sleep} hrs")

st.divider()

# ── Row 2: Steps over time (full width) ─────────────────────────────────────
daily_steps = df.groupby("Date")["Steps Count"].mean().reset_index()

fig_steps = go.Figure()
fig_steps.add_trace(go.Scatter(
    x=daily_steps["Date"], y=daily_steps["Steps Count"],
    mode="lines+markers", name="Avg Steps",
    line=dict(color="#3498db", width=2),
    fill="tozeroy", fillcolor="rgba(52,152,219,0.15)",
    hovertemplate="%{x|%b %d}<br>Avg Steps: %{y:,.0f}<extra></extra>",
))
fig_steps.update_layout(
    title="Daily Steps Trend", xaxis_title=None, yaxis_title="Avg Steps",
    margin=dict(t=40, b=20), height=280, plot_bgcolor="white",
    xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
)
st.plotly_chart(fig_steps, use_container_width=True)

# ── Row 3: Calories (60%) + Workout breakdown (40%) ─────────────────────────
col_cal, col_workout = st.columns([3, 2])

with col_cal:
    daily_cal = df.groupby("Date")[["Calories Burned", "Calories Consumed"]].mean().reset_index()
    fig_cal = go.Figure()
    fig_cal.add_trace(go.Scatter(
        x=daily_cal["Date"], y=daily_cal["Calories Burned"],
        mode="lines+markers", name="Burned",
        line=dict(color="#e74c3c", width=2),
        hovertemplate="%{x|%b %d}<br>Burned: %{y:,.0f} kcal<extra></extra>",
    ))
    fig_cal.add_trace(go.Scatter(
        x=daily_cal["Date"], y=daily_cal["Calories Consumed"],
        mode="lines+markers", name="Consumed",
        line=dict(color="#2ecc71", width=2),
        hovertemplate="%{x|%b %d}<br>Consumed: %{y:,.0f} kcal<extra></extra>",
    ))
    fig_cal.update_layout(
        title="Calories Burned vs Consumed", xaxis_title=None, yaxis_title="Avg kcal",
        margin=dict(t=40, b=20), height=300, plot_bgcolor="white",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_cal, use_container_width=True)

with col_workout:
    workout_dur = (
        df[df["Workout Type"] != "Rest"]
        .groupby("Workout Type")["Workout Duration (Minutes)"]
        .sum()
        .sort_values()
        .reset_index()
    )
    fig_workout = go.Figure(go.Bar(
        x=workout_dur["Workout Duration (Minutes)"],
        y=workout_dur["Workout Type"],
        orientation="h",
        marker_color="#9b59b6",
        hovertemplate="%{y}: %{x:,} mins<extra></extra>",
    ))
    fig_workout.update_layout(
        title="Total Workout Duration by Type", xaxis_title="Total Minutes", yaxis_title=None,
        margin=dict(t=40, b=20), height=300, plot_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_workout, use_container_width=True)

# ── Row 4: Sleep trend (40%) + Sleep quality donut (25%) + Weight (35%) ─────
col_sleep, col_pie, col_weight = st.columns([4, 2.5, 3.5])

with col_sleep:
    daily_sleep = df.groupby("Date").agg(
        avg_sleep=("Sleep Duration (Hours)", "mean"),
        top_quality=("Sleep Quality", lambda x: x.mode()[0]),
    ).reset_index()

    fig_sleep = go.Figure()
    fig_sleep.add_trace(go.Scatter(
        x=daily_sleep["Date"], y=daily_sleep["avg_sleep"],
        mode="lines", line=dict(color="#bdc3c7", width=1.5),
        showlegend=False, hoverinfo="skip",
    ))
    for quality, colour in SLEEP_COLOURS.items():
        mask = daily_sleep["top_quality"] == quality
        subset = daily_sleep[mask]
        if subset.empty:
            continue
        fig_sleep.add_trace(go.Scatter(
            x=subset["Date"], y=subset["avg_sleep"],
            mode="markers", name=quality,
            marker=dict(color=colour, size=11, line=dict(width=1, color="white")),
            hovertemplate="%{x|%b %d}<br>%{y:.1f} hrs · " + quality + "<extra></extra>",
        ))
    fig_sleep.update_layout(
        title="Sleep Duration & Quality", xaxis_title=None, yaxis_title="Avg Hours",
        margin=dict(t=40, b=20), height=300, plot_bgcolor="white",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_sleep, use_container_width=True)

with col_pie:
    sleep_counts = df["Sleep Quality"].value_counts().reindex(SLEEP_LEVELS).dropna()
    fig_pie = go.Figure(go.Pie(
        labels=sleep_counts.index,
        values=sleep_counts.values,
        hole=0.52,
        marker=dict(colors=[SLEEP_COLOURS[q] for q in sleep_counts.index]),
        textinfo="percent",
        textposition="inside",
        insidetextorientation="horizontal",
        hovertemplate="%{label}: %{value} nights (%{percent})<extra></extra>",
    ))
    fig_pie.update_layout(
        title="Sleep Quality Mix",
        margin=dict(t=40, l=10, r=10, b=60), height=320,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5),
        annotations=[dict(text=f"<b>{len(df)}</b><br>days", x=0.5, y=0.5, font_size=13, showarrow=False)],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_weight:
    daily_weight = df.groupby("Date")["Weight (kg)"].mean().reset_index()
    fig_weight = go.Figure()
    fig_weight.add_trace(go.Scatter(
        x=daily_weight["Date"], y=daily_weight["Weight (kg)"],
        mode="lines+markers", name="Avg Weight",
        line=dict(color="#e67e22", width=2),
        marker=dict(size=6),
        hovertemplate="%{x|%b %d}<br>Avg Weight: %{y:.1f} kg<extra></extra>",
    ))
    fig_weight.update_layout(
        title="Average Weight Trend", xaxis_title=None, yaxis_title="kg",
        margin=dict(t=40, b=20), height=300, plot_bgcolor="white",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_weight, use_container_width=True)

# ── Summary Insights ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Summary Insights")

active_df = df[df["Workout Type"] != "Rest"]

step_goal_pct = (df["Steps Count"] >= 10_000).mean() * 100
good_sleep_pct = df["Sleep Quality"].isin(["Good", "Excellent"]).mean() * 100
surplus_pct = (df["Net Calories"] > 0).mean() * 100

best_workout = (
    active_df.groupby("Workout Type")["Calories Burned"].mean().idxmax()
    if not active_df.empty else "N/A"
)
best_workout_cal = (
    int(active_df.groupby("Workout Type")["Calories Burned"].mean().max())
    if not active_df.empty else 0
)

long_sleep_good = (
    df[df["Workout Duration (Minutes)"] >= 45]["Sleep Quality"]
    .isin(["Good", "Excellent"]).mean() * 100
    if (df["Workout Duration (Minutes)"] >= 45).any() else 0
)
short_sleep_good = (
    df[df["Workout Duration (Minutes)"] < 45]["Sleep Quality"]
    .isin(["Good", "Excellent"]).mean() * 100
    if (df["Workout Duration (Minutes)"] < 45).any() else 0
)

worst_workout = (
    active_df.groupby("Workout Type")["Calories Burned"].mean().idxmin()
    if not active_df.empty else "N/A"
)

rest_poor = (
    df[df["Workout Type"] == "Rest"]["Sleep Quality"]
    .isin(["Poor", "Fair"]).mean() * 100
    if "Rest" in df["Workout Type"].values else 0
)

i1, i2, i3 = st.columns(3)
sleep_lift = long_sleep_good - short_sleep_good

with i1:
    st.info(f"""
**Takeaway**

- **{step_goal_pct:.0f}%** of days hit the 10,000-step target
- **{good_sleep_pct:.0f}%** of nights rated Good or Excellent sleep
- **{surplus_pct:.0f}%** of days in caloric surplus (consumed > burned)
- Avg net calories: **{int(df['Net Calories'].mean()):,} kcal/day** {"surplus" if df['Net Calories'].mean() > 0 else "deficit"}
""")

with i2:
    st.success(f"""
**Keep Doing ✅**

- **{best_workout}** delivers the highest avg calorie burn at **{best_workout_cal:,} kcal/session** — keep it in rotation
- Workouts **≥45 min** → **{long_sleep_good:.0f}%** Good/Excellent sleep vs **{short_sleep_good:.0f}%** for shorter sessions ({sleep_lift:+.0f}pp)
- Step counts stay consistent across all 20 days — good movement habit
""")

with i3:
    st.warning(f"""
**Stop / Watch Out ⚠️**

- **{worst_workout}** has the lowest avg calorie burn — swap for higher-intensity sessions
- **Rest days** → **{rest_poor:.0f}%** Poor/Fair sleep — add light movement on rest days
- Caloric surplus **{surplus_pct:.0f}%** of days — review portion sizes on low-activity days
""")
