import streamlit as st
import pandas as pd

# Load the data
df = pd.read_csv('voter_grades_app.csv')

st.set_page_config(page_title="Conformalytics | Super Voter", page_icon="🛡️")

# --- DEFINE FUNCTIONS FIRST ---
def show_grades(v):
    st.divider()
    
    # Clean up the suffix display so it doesn't show "nan"
    # We check if it's a string and not "nan"
    suffix = str(v['NSUFFIX']) if pd.notnull(v['NSUFFIX']) and str(v['NSUFFIX']).lower() != 'nan' else ""
    full_name = f"{v['FNAME']} {v['LNAME']} {suffix}".strip()
    
    st.subheader(f"Scorecard for {full_name}")
    
    g1, g2, g3 = st.columns(3)
    g1.metric("General", v['General_Grade'])
    g2.metric("Primary", v['Primary_Grade'])
    g3.metric("Specials", v['Special_Grade'])
    st.caption("*Grades are eligibility-adjusted based on your District registration date.*")

# --- UI AND SEARCH LOGIC ---
st.title("🛡️ Super Voter Identifier")
# Update: Changed to your requested headline
st.markdown("### Are You A Supervoter?")

with st.container():
    c1, c2 = st.columns(2)
    lname = c1.text_input("Last Name").upper().strip()
    snum = c2.text_input("Street Number").strip()

if lname and snum:
    results = df[(df['LNAME'] == lname) & (df['StreetNum'].astype(str) == snum)]
    
    if results.empty:
        st.error("No records found. Please check your spelling and address.")
    elif len(results) > 1:
        st.info("Multiple voters found at this address.")
        
        # Clean up labels for the selection dropdown as well
        results = results.copy() # Avoid warning
        results['Suffix_Clean'] = results['NSUFFIX'].apply(lambda x: str(x) if pd.notnull(x) and str(x).lower() != 'nan' else "")
        results['Selection_Label'] = results['FNAME'] + " " + results['Suffix_Clean'] + " (Reg: " + results['RegYear'].astype(str) + ")"
        
        choice = st.selectbox("Select your record:", results['Selection_Label'])
        voter = results[results['Selection_Label'] == choice].iloc[0]
        show_grades(voter)
    else:
        voter = results.iloc[0]
        show_grades(voter)
