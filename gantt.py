import plotly.express as px
import pandas as pd

# Sample data
df = pd.DataFrame([
    dict(Task="Task A", Start='2025-05-22 09:00:00', Finish='2025-05-22 11:30:00'),
    dict(Task="Task B", Start='2025-05-22 10:00:00', Finish='2025-05-22 14:00:00'),
    dict(Task="Task C", Start='2025-05-22 13:00:00', Finish='2025-05-22 15:30:00'),
    dict(Task="Task D", Start='2025-05-23 09:00:00', Finish='2025-05-23 11:00:00'),
    dict(Task="Task E", Start='2025-05-23 11:30:00', Finish='2025-05-23 13:00:00'),
    dict(Task="Task F", Start='2025-05-23 13:30:00', Finish='2025-05-23 16:00:00'),
    dict(Task="Task G", Start='2025-05-24 09:00:00', Finish='2025-05-24 12:00:00'),
    dict(Task="Task H", Start='2025-05-24 12:30:00', Finish='2025-05-24 15:00:00'),
    dict(Task="Task I", Start='2025-05-24 15:30:00', Finish='2025-05-24 18:00:00')
])

# Convert to datetime
df['Start'] = pd.to_datetime(df['Start'])
df['Finish'] = pd.to_datetime(df['Finish'])

# Optional: color palette
custom_colors = [
    "#A6C8FF", "#B5EAD7", "#FFDAC1", "#FF9AA2",
    "#CBAACB", "#E2F0CB", "#F1F0C0", "#D6E2E9", "#FFB7B2"
]

# Create timeline
fig = px.timeline(
    df,
    x_start="Start",
    x_end="Finish",
    y="Task",
    color="Task",
    color_discrete_sequence=custom_colors,
    title="📅 Gantt Chart with Horizontal Scrolling"
)

# Configure Y-axis
fig.update_yaxes(categoryorder="total ascending")

# Define visible range (e.g., show only 2 days at once)
visible_start = df['Start'].min()
visible_end = visible_start + pd.Timedelta(days=2)

# Layout and scrollbar
fig.update_layout(
    xaxis=dict(
        range=[visible_start, visible_end],
        tickformat="%H:%M\n%b %d",
        rangeslider=dict(visible=True),  # Show horizontal scroll
        showgrid=True,
        gridcolor='lightgrey'
    ),
    yaxis=dict(showgrid=False),
    font=dict(family="Segoe UI", size=14),
    plot_bgcolor="white",
    margin=dict(l=120, r=40, t=80, b=40)
)

fig.show()