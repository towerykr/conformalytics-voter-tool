import streamlit as st
import pandas as pd

# Load the data generated in Part 1
df = pd.read_csv('voter_grades_app.csv')

st.set_page_config(page_title="Conformalytics | Super Voter", page_icon="🛡️")

# Use your new logo colors (Green on Dark)
st.title("🛡️ Super Voter Identifier")
st.markdown("### Precision Data for the District")

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
        # Collision handling: distinguish by First Name and Registration Year
        choice = st.selectbox("Select your record:", results['FNAME'] + " (Registered " + results['RegYear'].astype(str) + ")")
        selected_fname = choice.split(" ")[0]
        voter = results[results['FNAME'] == selected_fname].iloc[0]
        show_grades(voter)
    else:
        voter = results.iloc[0]
        show_grades(voter)

def show_grades(v):
    st.divider()
    st.subheader(f"Scorecard for {v['FNAME']} {v['LNAME']}")
    g1, g2, g3 = st.columns(3)
    g1.metric("General", v['General_Grade'])
    g2.metric("Primary", v['Primary_Grade'])
    g3.metric("Specials", v['Special_Grade'])
    st.caption("*Grades are eligibility-adjusted based on your District registration date.*")