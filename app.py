import streamlit as st
import pandas as pd

# 1. LOAD THE DATA (Updated for Parquet)
try:
    # Reading the compressed parquet file
    df = pd.read_parquet('voter_grades_app.parquet')
    counts_df = pd.read_csv('voter_counts_summary.csv')
except FileNotFoundError:
    st.error("Data files not found. Please ensure 'voter_grades_app.parquet' is in your GitHub folder.")
    st.stop()

st.set_page_config(page_title="Conformalytics | Are You A Supervoter?", page_icon="🛡️")

# --- FUNCTIONS ---

def show_grades(v):
    st.divider()
    
    # "nan" suffix fix
    suffix = str(v['NSUFFIX']) if pd.notnull(v['NSUFFIX']) and str(v['NSUFFIX']).lower() != 'nan' else ""
    full_name = f"{v['FNAME']} {v['LNAME']} {suffix}".strip()
    
    st.subheader(f"Scorecard for {full_name}")
    
    # Dichotomous Badge: New Voter
    if v['Is_New_Voter'] == 'Yes':
        st.info("👋 **Welcome!** You are a New Voter in the District (registered within the last 2 years).")
    
    # Habit Badge
    st.write(f"**Voting Habit:** {v['Early_Habit']}")

    # Grade Metrics
    g1, g2, g3 = st.columns(3)
    g1.metric("General Elections", v['General_Grade'])
    g2.metric("Primary Elections", v['Primary_Grade'])
    g3.metric("Special Elections", v['Special_Grade'])
    
    st.caption(f"**Methodology:** Grades are eligibility-adjusted based on Ward {v['WRD_STR']} and your District registration year ({int(v['RegYear'])}).")

    # Civic Call to Action
    st.info(f"""
    **Your Vote, Your Voice**
    
    While every campaign defines a 'supervoter' differently, what is most important is that you continue to exercise your right to vote! 
    
    If you were disappointed with your grade, **make a plan to vote** in the next election. In the District, voting is accessible and convenient:
    * 📬 **By Mail:** Every registered voter is mailed a ballot.
    * 🏛️ **Early In-Person:** Vote at *any* early voting center city-wide.
    * 🗳️ **Election Day:** Vote at *any* voting precinct in the District.
    """)

def show_legal():
    with st.expander("Methodology, Privacy & Legal Disclaimer"):
        st.markdown("""
        **New Voter Definition:** Voters registered for less than 2 years as of March 21, 2026, are identified as 'New Voters.' Their participation grades may show 'N/A' if no eligible elections have occurred since their registration date.
        
        **Privacy:** No search data is stored... [Rest of your disclaimer]
        """)

# --- UI ---
# st.image("dc_superman_crest.png", width=120) 
st.title("🛡️ Super Voter Identifier")
st.markdown("### Are You A Supervoter?")

# --- SEARCH ---
with st.container():
    c1, c2 = st.columns(2)
    lname = c1.text_input("Last Name").upper().strip()
    snum = c2.text_input("Street Number").strip()

if lname and snum:
    results = df[(df['LNAME'] == lname) & (df['StreetNum'].astype(str) == snum)]
    
    if results.empty:
        st.error("No records found at this address. Please check your spelling and street number. If that still does not work, check your voter registration status with DCBOE!")
    elif len(results) > 1:
        st.info("Multiple voters found at this address. Please select your specific record:")
        results = results.copy()
        results['Label'] = results['FNAME'] + " (Reg: " + results['RegYear'].astype(str) + ")"
        choice = st.selectbox("Select your record:", results['Label'])
        voter = results[results['Label'] == choice].iloc[0]
        show_grades(voter)
    else:
        voter = results.iloc[0]
        show_grades(voter)

st.write("\n")
show_legal()
