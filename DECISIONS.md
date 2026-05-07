# Fitness Dashboard — Decisions & Ideas

## Context
Hackathon session: "Agentic BI Workflows in Power BI" — Mac users can't run Power BI Desktop, so this is a Python-native equivalent using Streamlit + Plotly.

## Dataset
- Source: trumpexcel.com Fitness Tracker sample dataset
- 1000 rows: 50 users × 20 days (July 1–20 2024)
- No nulls; all columns numeric or categorical; daily grain

---

## Decisions

### D1 — Streamlit over Dash/Panel
Streamlit is the fastest path to a demo-quality dashboard. Dash requires more boilerplate for callbacks; Panel is heavier. For a hackathon context, Streamlit's top-down execution model fits the Z-layout idea naturally.

### D2 — Plotly for all charts
Plotly gives interactive hover tooltips out of the box without extra config. Alternatives (Altair, Matplotlib, Bokeh) require more setup to reach the same interactivity level. All charts use `plotly.graph_objects` for fine-grained control rather than `plotly.express`, which can be limiting for dual-axis or custom colour maps.

### D3 — Filters: Workout Type + Sleep Quality only
Deliberately omitted User ID as a filter. The dataset becomes more interesting as a cross-sectional view: "what do fitness metrics look like on days with Excellent sleep quality, across all users?" That's a more meaningful analytical question than per-user drill-down with only 20 data points per user. A user filter can be added later if needed.

### D4 — Aggregation strategy: daily mean across users
All "over time" charts aggregate by date (mean across all matching users). This avoids clutter from 50 overlapping lines while still showing the trend shape. Sum would overweight busy days with more active users; mean is more interpretable.

### D5 — Z-pattern layout
Intentional reading flow:
1. BAN row (left→right): quick headline numbers
2. Steps trend (full width): primary activity metric
3. Calories (60%) + Workout breakdown (40%): related metrics, two complementary views
4. Sleep (50%) + Weight (50%): recovery and outcome metrics

This mirrors Power BI's recommended dashboard layout for executive-style reports.

### D6 — "Show all" default for filters
Empty multi-select = show all data (not no data). This is the Power BI default and the more intuitive behaviour for someone landing on the dashboard cold.

### D7 — Net Calories = Consumed − Burned
Positive = caloric surplus (more eaten than burned). A positive delta on the BAN card is displayed as a warning colour since surplus typically signals weight gain risk. This is the standard nutrition framing.

---

## Ideas for future iterations

### Analytics
- **Correlation heatmap**: steps vs sleep duration, calories burned vs workout duration — reveals which metrics move together
- **Sleep quality predictor**: logistic regression on same-day metrics to predict poor vs good sleep
- **Workout effectiveness score**: calories burned per minute, ranked by workout type
- **Rest day impact**: compare next-day step count after Rest vs active day

### UX / Features
- **User filter (optional)**: toggle between "all users" aggregate and single-user deep-dive
- **Date range slider**: even though data is only 20 days, a slider would make the pattern more explorable
- **Benchmark lines**: add average reference line on all charts (dashed horizontal)
- **Dark mode**: Streamlit supports `theme = dark` in config.toml — matches Power BI dark canvas aesthetic
- **Export button**: `st.download_button` to export filtered data as CSV

### Technical
- **Live data via Google Sheets**: replace static Excel with a Google Sheets connector — makes the demo feel live
- **MCP server hook**: if running locally with Claude Code, wire the MCP server to generate new Plotly charts from natural language ("show me a scatter of steps vs sleep")
- **Automated data refresh**: GitHub Actions cron job to pull new data and push to a hosted Streamlit app (Streamlit Community Cloud)
