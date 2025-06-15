import streamlit as st
import pandas as pd

@st.cache_data
def load_emission_factors(filepath):
    df = pd.read_csv(filepath)
    return df.set_index('activity')

def calculate_emissions(user_df, factors_df):
    results = []
    total_emissions = 0.0
    scope_totals = {"1": 0.0, "2": 0.0, "3": 0.0, "Unknown": 0.0}

    for _, row in user_df.iterrows():
        activity = row['activity'].strip()
        amount = row['amount']

        if activity not in factors_df.index:
            results.append({
                'activity': activity,
                'amount': amount,
                'emissions': 'N/A',
                'scope': 'Unknown'
            })
            scope_totals["Unknown"] += 0
            continue

        factor = factors_df.loc[activity, 'factor']
        scope = str(factors_df.loc[activity, 'scope'])
        emissions = amount * factor
        scope_totals[scope] += emissions
        total_emissions += emissions

        results.append({
            'activity': activity,
            'amount': amount,
            'emissions': emissions,
            'scope': scope
        })

    results_df = pd.DataFrame(results)
    return results_df, total_emissions, scope_totals

# Streamlit UI
st.title("Carbon Emissions Calculator (Expanded)")
st.write("Upload a CSV file with two columns: `activity`, `amount` (e.g. kWh, miles, GBP).")
st.write("Need help? Here's a list of accepted activity names:")

with st.expander("📋 Accepted Activity Names"):
    st.code(", ".join([
        "electricity_uk_grid", "natural_gas", "biomass", "heating_oil",
        "diesel", "petrol", "car_business_miles", "van_diesel_miles",
        "van_petrol_miles", "short_haul_flight", "long_haul_flight", "rail",
        "bus", "taxi", "waste_landfill", "waste_recycling", "waste_composting",
        "paper", "it_equipment", "construction_materials"
    ]))

factors_df = load_emission_factors("emission_factors.csv")

uploaded_file = st.file_uploader("📤 Upload your activity data CSV", type="csv")

if uploaded_file:
    try:
        user_df = pd.read_csv(uploaded_file)

        if {'activity', 'amount'}.issubset(user_df.columns):
            results_df, total, scope_totals = calculate_emissions(user_df, factors_df)

            st.subheader("🧾 Emissions Breakdown")
            st.dataframe(results_df)

            st.markdown(f"### 🌍 Total Emissions: **{total:.2f} kg CO₂e**")

            st.markdown("### 🔎 By Scope:")
            for scope, val in scope_totals.items():
                st.markdown(f"- Scope {scope}: **{val:.2f} kg CO₂e**")

            # Download
            csv = results_df.to_csv(index=False)
            st.download_button("⬇️ Download results as CSV", csv, "emissions_report.csv", "text/csv")
        else:
            st.error("CSV must include columns: 'activity' and 'amount'")
    except Exception as e:
        st.error(f"Something went wrong: {e}")
else:
    st.info("Awaiting your activity CSV upload...")
