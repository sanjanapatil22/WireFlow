from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the Excel file once at startup
df = pd.read_excel("2005 FLEX  REV-g.xls", sheet_name=0)

# Clean column headers
df.columns = df.columns.map(lambda x: x if not str(x).startswith("Unnamed") else "")

# Replace NaNs with 0
df.fillna(0, inplace=True)

# Define machine column names (from col X to AH)
machine_columns = [
    "RBD", "MD", "FD", "AN", "B50/80", "BU10",
    "12B", "INS (EXT)", "ASSLY(B1000)", "ASSLY(12B)", "SHEATH (EXT)"
]

# Mapping n values to row ranges
n_ranges = {
    2: (4, 14),   # Excel rows 6–15 -> Python rows 5–14
    3: (15, 25),
    4: (26, 36),
    5: (37, 47)
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        try:
            n = int(request.form["n"])
            m = float(request.form["m"])
            length = float(request.form["length"])

            print(f"\n>>> Input received - n: {n}, m: {m}, length: {length}")

            if n not in n_ranges:
                return "Error: Invalid value for n", 400

            start, end = n_ranges[n]
            print(f"Fetching rows from index {start} to {end - 1} for n = {n}")
            filtered_df = df.iloc[start:end]

            # Debug print: Check selected range
            print("Filtered DataFrame preview:")
            print(filtered_df.head())

            # Ensure m column (E) is treated as float
            filtered_df = filtered_df.copy()
            filtered_df.iloc[:, 4] = pd.to_numeric(filtered_df.iloc[:, 4], errors='coerce')
            print("Column E (m values) after conversion:")
            print(filtered_df.iloc[:, 4])

            # Match m in column E (index 4)
            matched_row = filtered_df[filtered_df.iloc[:, 4] == m]
            if matched_row.empty:
                print(f"No match found for m = {m} in column E.")
                return "Error: No matching wire found for the selected combination.", 400

            row_index = matched_row.index[0]
            print(f"Matching row found at index: {row_index}")
            print("Matched row preview:")
            print(df.iloc[row_index])

            # Extract raw materials from columns Q to U (index 17 to 21)
            raw_materials = df.iloc[row_index, 17:22].fillna(0)
            print("Raw materials (per meter):")
            print(raw_materials)

            raw_materials_dict = {
                "Conductor": round(raw_materials.iloc[0] * length, 4),
                "Insulation": round(raw_materials.iloc[1] * length, 4),
                "Dumy": round(raw_materials.iloc[2] * length, 4),
                "Sheath": round(raw_materials.iloc[3] * length, 4),
                "Total": round(raw_materials.iloc[4] * length, 4),
            }
            print("Calculated raw materials:")
            print(raw_materials_dict)

            # Machine times from columns X to AH (index 23 to 33)
            machine_times_raw = df.iloc[row_index, 23:34].fillna(0)
            print("Machine times (per meter):")
            print(machine_times_raw)

            machine_times = {
                machine_columns[i]: round(val * length, 3)
                for i, val in enumerate(machine_times_raw.values.flatten())
            }
            print("Calculated machine times:")
            print(machine_times)

            
            matched_cols = df.iloc[row_index, 2:16].tolist()
            print(matched_cols)
            result = {
                "length": length,
                "n": n,
                "m": m,
                "raw_materials": raw_materials_dict,
                "machine_times": machine_times,
                "matched_cols": matched_cols  # <-- Add this
            }



        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return f"Error: {str(e)}", 500

    return render_template("index.html", result=result)

@app.route("/confirm", methods=["POST"])
def confirm():
    try:
        n = int(request.form["n"])
        m = float(request.form["m"])
        length = float(request.form["length"])

        # Extract raw materials and machine times from form
        raw_materials = {
            key.split("raw_")[1]: float(val)
            for key, val in request.form.items() if key.startswith("raw_")
        }
        machine_times = {
            key.split("machine_")[1]: float(val)
            for key, val in request.form.items() if key.startswith("machine_")
        }

        # Prepare hidden fields for final POST
        hidden_fields = {
            key: val for key, val in request.form.items()
        }

        data = {
            "n": n,
            "m": m,
            "length": length,
            "raw_materials": raw_materials,
            "machine_times": machine_times,
            "hidden_fields": hidden_fields
        }

        return render_template("confirm.html", data=data)

    except Exception as e:
        return f"Error in confirm route: {str(e)}", 500


@app.route("/finalize", methods=["POST"])
def finalize():
    try:
        import os
        output_path = "output.csv"

        # Get form data
        company_name = request.form["company_name"]
        order_date = request.form["order_date"]

        # Validate numeric inputs
        try:
            length = float(request.form["length"])
            n = int(request.form["n"])
            m = float(request.form["m"])
        except ValueError:
            return "❌ Invalid number input for length, n, or m.", 400

        # Raw materials (keys: raw_CU, raw_AL, ...)
        raw_materials = {
            key.split("raw_")[1]: float(val)
            for key, val in request.form.items() if key.startswith("raw_")
        }

        # Machine times (keys: machine_Bunching, machine_Coning, ...)
        machine_times = {
            key.split("machine_")[1]: float(val)
            for key, val in request.form.items() if key.startswith("machine_")
        }

        # Matched data from C to P (13 values: index 2 to 14)
        matched_data = [
            request.form.get(f"matched_col_{i}", "") for i in range(2, 15 + 1)
        ]
        print("Matched Data:", matched_data)

        # If output file doesn't exist, create 5 blank rows and 35 columns
        if not os.path.exists(output_path):
            pd.DataFrame([[""] * 35 for _ in range(5)]).to_csv(output_path, index=False, header=False)

        # Load and ensure structure
        out_df = pd.read_csv(output_path, header=None)

        # Ensure exactly 35 columns in DataFrame
        required_cols = 48  # adjust based on actual max index you're using
        if out_df.shape[1] < required_cols:
            for _ in range(required_cols - out_df.shape[1]):
                out_df[out_df.shape[1]] = ""


        # Create new row
        new_row = [""] * 48
        new_row[0] = company_name  # A
        new_row[1] = order_date    # B
        new_row[2] = length        # C
        new_row[3:3+len(matched_data)] = matched_data  # D to Q

        # Raw materials to S–W (index 18–22)
        for idx, val in enumerate(raw_materials.values()):
            new_row[18 + idx] = round(val, 2)

        # Machine times to Y–AI (index 24–34)
        for idx, val in enumerate(machine_times.values()):
            new_row[24 + idx] = round(val, 2)

        # Append new row
        out_df.loc[len(out_df)] = new_row
        out_df.to_csv(output_path, index=False, header=False)

        return render_template("finalize.html", company_name=company_name, order_date=order_date)

    except Exception as e:
        return f"❌ Error in finalize route: {str(e)}", 500

@app.route("/gantt", methods=["GET", "POST"])
def gantt():
    import pandas as pd
    import os

    csv_path = "output.csv"
    
    # Load the CSV
    df = pd.read_csv(csv_path, header=None)

    # Ensure we have enough columns
    if df.shape[1] < 47:  # Up to AL = col 37, AV = col 47
        for _ in range(47 - df.shape[1]):
            df[df.shape[1]] = ""

    # Get company entries from row 5 (index 4) onward
    company_data = df.iloc[4:].copy()

    # Sort by priority in column AK (index 36)
    company_data[36] = pd.to_numeric(company_data[36], errors="coerce").fillna(float("inf"))
    company_data = company_data.sort_values(by=36)

    # List of machine names for columns Y to AI (24–34)
    machine_names = [
        "RBD", "MD", "FD", "AN", "B50/80", "BU10",
        "12B", "INS (EXT)", "ASSLY(B1000)", "ASSLY(12B)", "SHEATH (EXT)"
    ]

    gantt_rows = []
    for _, row in company_data.iterrows():
        company_name = row[0]
        order_date = row[1]
        length = row[2]
        n = row[3]
        m = row[5]

        val = row[36]
        if pd.isnull(val) or val == float("inf"):
            priority = "?"
        else:
            priority = int(val)

        durations = row[24:35].tolist()
        starts = row[37:48].tolist()

        gantt_rows.append({
            "company": company_name,
            "order_date": order_date,
            "priority": priority,
            "durations": durations,
            "start_times": starts,
            "machine_names": machine_names,
            "length": length,
            "n": n,
            "m": m
        })

    return render_template("gantt_input.html", gantt_rows=gantt_rows)

@app.route("/save_start_times", methods=["POST", "GET"])
def save_start_times():
    import pandas as pd
    csv_path = "output.csv"
    df = pd.read_csv(csv_path, header=None)

    company_name = request.form.get("company_name") or request.args.get("company_name")
    print(f"Received start times for: {company_name}")

    # Ensure DataFrame has at least 48 columns (index 0 to 47 = AL)
    required_columns = 37 + 11  # 37 is AL, 11 machines
    if df.shape[1] < required_columns:
        for _ in range(required_columns - df.shape[1]):
            df[df.shape[1]] = ""

    # Find matching row and update
    for idx in range(4, len(df)):
        if df.iloc[idx, 0] == company_name:
            for i in range(11):
                value = request.form.get(f"start_{i}", "")
                df.iloc[idx, 37 + i] = value  # Start times go from AL (index 37)
            print(f"✅ Updated row: {idx}")
            break
    else:
        print("❌ Company name not found!")

    df.to_csv(csv_path, index=False, header=False)
    return f"✅ Start times updated for <strong>{company_name}</strong>! <a href='/gantt'>Go Back</a>"



@app.route("/gantt_chart")
def view_gantt():
    import pandas as pd
    import plotly.express as px
    import plotly

    # Read and process CSV
    df = pd.read_csv("output.csv", header=None)
    df = df.iloc[4:].reset_index(drop=True)

    machine_names = [
        "RD", "MD", "FD", "AN", "B50/80", "BU10", "12B",
        "INS EXT", "ASSLY B1000", "ASSLY 12B", "SHEATH EXT"
    ]
    machine_start_cols = list(range(37, 48))
    machine_duration_cols = list(range(24, 35))

    gantt_data = []
    for idx, row in df.iterrows():
        company = row[0]
        for i in range(11):
            start_time_str = row[machine_start_cols[i]]
            duration_val = row[machine_duration_cols[i]]

            if pd.isna(start_time_str) or pd.isna(duration_val):
                continue

            try:
                start = pd.to_datetime(start_time_str, dayfirst=True, errors='raise')
                if isinstance(duration_val, str):
                    duration_val = float(duration_val.strip())
                finish = start + pd.to_timedelta(duration_val, unit='h')
                gantt_data.append({
                    "Task": machine_names[i],
                    "Start": start,
                    "Finish": finish,
                    "Company": company
                })
            except Exception as e:
                print(f"Skipping row {idx}, machine {i} due to error: {e}")

    gantt_df = pd.DataFrame(gantt_data)

    if gantt_df.empty:
        return "⚠️ No valid Gantt data found."

    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Company",
        title="📊 Machine Usage Timeline (Gantt Chart)",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        xaxis=dict(
            tickformat="%d-%m\n%H:%M",
            rangeslider=dict(visible=True),
            showgrid=True,
            gridcolor="lightgrey"
        ),
        yaxis=dict(showgrid=False),
        font=dict(family="Segoe UI", size=14),
        plot_bgcolor="white",
        margin=dict(l=140, r=40, t=80, b=40)
    )

    gantt_html = plotly.io.to_html(fig, full_html=False)

    return render_template("gantt_chart.html", gantt_html=gantt_html)

if __name__ == "__main__":
    app.run(debug=True)

    
