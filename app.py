import streamlit as st
import pandas as pd

# 1. LOAD THE DATA
# Using Parquet for the large voter file and CSV for the summary
try:
    df = pd.read_parquet('voter_grades_app.parquet')
    counts_df = pd.read_csv('voter_counts_summary.csv')
except FileNotFoundError:
    st.error("Data files not found. Please ensure 'voter_grades_app.parquet' and 'voter_counts_summary.csv' are in your GitHub folder.")
    st.stop()

st.set_page_config(page_title="Conformalytics | Are You A Supervoter?", page_icon="🛡️", layout="wide")

# --- STEP 1: DEFINE DISPLAY FUNCTIONS ---

def show_grades(v):
    st.divider()
    
    # Handle "nan" suffix and clean name display
    suffix = str(v['NSUFFIX']) if pd.notnull(v['NSUFFIX']) and str(v['NSUFFIX']).lower() != 'nan' else ""
    full_name = f"{v['FNAME']} {v['LNAME']} {suffix}".strip()
    
    st.subheader(f"Scorecard for {full_name}")
    
    # New Voter & Habit Badges
    col_a, col_b = st.columns(2)
    with col_a:
        if v['Is_New_Voter'] == 'Yes':
            st.info("👋 **Welcome!** You are a New Voter in the District (registered within the last 2 years).")
        else:
            st.write(f"**Registration Year:** {int(v['RegYear'])}")
    
    with col_b:
        habit = v['Early_Habit']
        if "Frequently" in habit:
            st.success(f"🏅 {habit}")
        elif "Sometimes" in habit:
            st.info(f"📊 {habit}")
        else:
            st.warning(f"🗳️ {habit}")

    # Participation Metrics
    st.write("### Your Participation Grades")
    g1, g2, g3 = st.columns(3)
    g1.metric("General Elections", v['General_Grade'])
    g2.metric("Primary Elections", v['Primary_Grade'])
    g3.metric("Special Elections", v['Special_Grade'])
    
    st.caption(f"**Methodology:** Grades are eligibility-adjusted based on Ward {v['WRD_STR']} and your District registration year.")

    # Civic Call to Action
    st.info(f"""
    **Your Vote, Your Voice**
    
    While every campaign defines a 'supervoter' differently, what is most important is that you continue to exercise your right to vote! 
    
    If you were disappointed with your grade, **make a plan to vote** in the next election. In the District, voting is accessible and convenient:
    * 📬 **By Mail:** Every registered voter is mailed a ballot.
    * 🏛️ **Early In-Person:** Vote at *any* early voting center city-wide.
    * 🗳️ **Election Day:** Vote at *any* voting precinct in the District.
    """)

def show_disclaimers():
    with st.expander("Methodology, Privacy & Legal Disclaimer"):
        st.markdown("""
        ### **Methodology**
        Grades are calculated using an **Eligibility-Adjusted Participation Model**. Unlike standard voter scores that penalize residents for missing elections they were not eligible for, our system normalizes participation based on:
        * **Registration Date:** We only count elections that occurred *after* you registered in the District.
        * **Ward-Specific Eligibility:** For Special Elections, you are only graded on contests where your specific Ward was eligible to participate.
        * **New Voter Definition:** Voters registered for less than 2 years as of March 21, 2026, are identified as 'New Voters.' Their participation grades may show 'N/A' if no eligible elections have occurred since their registration date.
        * **The Scale:** Participation percentages are converted to a standard A–F academic scale.

        ### **Privacy & Data Security**
        At Conformalytics, we prioritize data integrity and user privacy:
        * **No Data Retention:** We do not store, track, or save the names or addresses entered into this tool. Your search is processed in real-time and cleared immediately upon closing the session.
        * **Public Records:** This tool utilizes the public voter file provided by the District of Columbia Board of Elections (DCBOE). We do not display sensitive Personally Identifiable Information (PII) such as birth dates or social security numbers.
        * **Encryption:** This application is served over an encrypted (SSL) connection to ensure your search remains secure.

        ### **Legal Disclaimer**
        This tool is provided for **informational and educational purposes only**. While Conformalytics strives for accuracy, the data is derived from third-party public records which may contain clerical errors or update lags. 
        
        This tool does not constitute an official government record or an official statement of your voting status. To verify your official registration or voting history, please visit the [DC Board of Elections website](https://dcboe.org). Conformalytics is an independent consultancy and is not affiliated with, or endorsed by, any government agency.
        """)

# --- STEP 2: APP TABS ---

tab1, tab2 = st.tabs(["🔍 Supervoter Lookup", "📊 Win Number Calculator"])

# --- TAB 1: SUPERVOTER LOOKUP ---
with tab1:
    # Optional: st.image("dc_superman_crest.png", width=120) 
    st.title("🛡️ Super Voter Identifier")
    st.markdown("## Are You A Supervoter?")

    with st.container():
        c1, c2 = st.columns(2)
        lname_input = c1.text_input("Last Name", key="lookup_lname").upper().strip()
        snum_input = c2.text_input("Street Number", key="lookup_snum").strip()

    if lname_input and snum_input:
        results = df[(df['LNAME'] == lname_input) & (df['StreetNum'].astype(str) == snum_input)]
        
        if results.empty:
            st.error("No records found at this address. Please check your spelling and street number. If that still does not work, check your voter registration status with DCBOE!")
        
        elif len(results) > 1:
            st.info("Multiple voters were found at this address. Please select your specific record:")
            results = results.copy()
            results['Suffix_Clean'] = results['NSUFFIX'].apply(lambda x: str(x) if pd.notnull(x) and str(x).lower() != 'nan' else "")
            results['Label'] = results['FNAME'] + " " + results['Suffix_Clean'] + " (Reg: " + results['RegYear'].astype(str) + ")"
            
            choice = st.selectbox("Who are you looking for?", results['Label'])
            voter = results[results['Label'] == choice].iloc[0]
            show_grades(voter)
        
        else:
            voter = results.iloc[0]
            show_grades(voter)

# --- TAB 2: WIN NUMBER CALCULATOR ---
with tab2:
    st.title("🗳️ Strategic Win Number Calculator")
    st.markdown("### Step 1: Select Your District")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Get clean list of Wards
        ward_list = sorted(counts_df['WRD_STR'].unique(), key=lambda x: int(x))
        selected_wrd = st
