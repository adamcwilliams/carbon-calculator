import streamlit as st
import pandas as pd

# Load emission factors from CSV
@st.cache_data
def load_emission_factors(filepath):
    df = pd.read_csv(filepath)
    return df.set_index('activity')

# Calculate emissions
def calculate_emissions(user_df, factors_df):
    results = []
    total_emissions = 0.0

    for _, row in user_df.iterrows():
        activity = row['activity']
        amount = row['amount']

        if activity not in factors_df.index:
            results.append({
                'activity': activity,
                'amount': amount,
                'emissions': 'N/A',
                'scope': 'Unknown'
            })
            continue

        factor = factors_df.loc[activity, 'factor']
        scope = factors_df.loc[activity, 'scope']
        emissions = amount * factor
        total_emissions += emissions

        results.append({
            'activity': activity,
            'amount': amount,
            'emissions': emissions,
            'scope': scope
        })

    results_df = pd.DataFrame(results)
    return results_df, total_emissions

# UI
st.title("Carbon Emissions Calculator (Beta)")
st.write("Upload your activity data CSV (columns: `activity`, `amount`).")

# Load emission factors once
factors_df = load_emission_factors("emission_factors.csv")

uploaded_file = st.file_uploader("Upload activity data CSV", type="csv")

if uploaded_file:
    user_df = pd.read_csv(uploaded_file)

    if {'activity', 'amount'}.issubset(user_df.columns):
        results_df, total = calculate_emissions(user_df, factors_df)

        st.subheader("Emissions Breakdown")
        st.dataframe(results_df)

        st.markdown(f"### 🌍 Total Emissions: **{total:.2f} kg CO₂e**")

        # Optional: download result
        csv = results_df.to_csv(index=False)
        st.download_button("Download results as CSV", csv, "emissions_report.csv", "text/csv")
    else:
        st.error("CSV must include 'activity' and 'amount' columns.")
else:
    st.info("Awaiting CSV upload...")
