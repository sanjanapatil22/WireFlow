# ⚙️ Wire Production Scheduler & Gantt Chart Visualizer

This Flask-based web application streamlines the wire manufacturing process by allowing users to input wire order details and generate machine start times. It visualizes the timeline using an interactive Gantt chart and calculates machine-wise durations, raw materials, and dependencies.

## 📌 Features

- 📥 Input wire order: company name, subwires (n), dimension (m), and length
- 📆 Specify manufacturing date and start times for machines
- ⚙️ Auto-generate machine timings based on manufacturing date
- 🔄 Sync start times with the previous order to avoid overlap
- 📊 Interactive Gantt chart showing machine usage across companies
- ✅ Exportable chart with zoom, pan, and download options

## 🛠️ Tech Stack

- **Backend**: Python + Flask
- **Frontend**: HTML + Tailwind CSS + JavaScript
- **Visualization**: Plotly Express
- **Data Storage**: CSV file ( `used as per project constraints to simulate external data integration without a database.`)


### 🎥 Demo Video

[▶️ Click to download or view the video](https://github.com/sanjanapatil22/WireFLow/images/Wire.mov)
