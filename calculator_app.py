import streamlit as st
import pandas as pd

# 1. LOAD DATA
try:
    # Ensure this file was created by your data engine
    df = pd.read_csv('voter_counts_smd.csv')
except FileNotFoundError:
    st.error("Data file 'voter_counts_smd.csv' not found. Please upload it to GitHub.")
    st.stop()

st.set_page_config(page_title="Conformalytics | Win Number", page_icon="📊", layout="wide")

# --- UI HEADER ---
st.title("🗳️ DC Win Number Calculator")
st.markdown("#### Strategic Targets for Plurality and Ranked-Choice Voting (RCV)")
st.divider()

# --- STEP 1: HIERARCHICAL SELECTION ---
st.header("Step 1: Select Your Race")
c1, c2 = st.columns(2)

with c1:
    # Ward Options: 1-8 + "All"
    ward_list = sorted(df['WRD_STR'].unique().astype(str), key=lambda x: int(x))
    ward_options = ["All"] + ward_list
    sel_ward = st.selectbox("Select Ward", ward_options)

with c2:
    # SMD Options: Dynamic based on Ward selection
    if sel_ward == "All":
        sel_smd = "None"
        st.write("**City-Wide Race:** SMD selection is disabled.")
        # Calculate for all of DC
        reg_voters = df['Voter_Count'].sum()
    else:
        smd_list = sorted(df[df['WRD_STR'].astype(str) == sel_ward]['SMD_STR'].unique())
        smd_options = ["None"] + smd_list
        sel_smd = st.selectbox("Select SMD (Optional)", smd_options)
        
        # Determine voter count based on SMD selection
        if sel_smd == "None":
            # Total for the selected Ward
            reg_voters = df[df['WRD_STR'].astype(str) == sel_ward]['Voter_Count'].sum()
        else:
            # Total for the specific SMD
            reg_voters = df[df['SMD_STR'] == sel_smd]['Voter_Count'].sum()

# --- STEP 2: STRATEGY & MATH ---
st.header("Step 2: Strategy & Turnout")
col_l, col_r = st.columns([2, 1])

with col_l:
    st.write(f"**Target District:** Ward {sel_ward} | SMD {sel_smd}")
    st.write(f"**Total Registered Voters:** {reg_voters:,}")
    
    turnout_pct = st.slider("Expected Turnout (%)", 5, 100, 35, 
                           help="Typical ANC races range from 25-45%. General elections can exceed 70%.")
    
    exhaustion_pct = st.slider("Projected Ballot Exhaustion (%)", 0, 20, 5, 
                              help="Under DC Law 25-295, these are ballots that become inactive if all ranked candidates are eliminated.")

# --- RCV CALCULATIONS ---
# 1. Total Ballots Cast
total_ballots = reg_voters * (turnout_pct / 100)
# 2. Active Ballots (Remaining in final round after exhaustion)
active_ballots = total_ballots * (1 - (exhaustion_pct / 100))
# 3. RCV Win Threshold (50% + 1 of Active Ballots)
win_number = int(active_ballots / 2) + 1
# 4. First Choice Goal (51% of Total Ballots to win in Round 1)
round_one_goal = int(total_ballots * 0.51)

with col_r:
    st.metric("Total Ballots Expected", f"{int(total_ballots):,}")
    st.metric("RCV Win Number", f"{win_number:,}")
    st.caption("Threshold for victory in the final round of counting.")

# --- STRATEGIC NUDGE ---
st.divider()
st.subheader("🛡️ Conformalytics Strategic Nudge")

st.info(f"""
**The Path to Victory:**
* **To Win in Round 1:** Aim for **{round_one_goal:,}** first-choice votes. This avoids the Instant Runoff entirely.
* **To Win via Coalition:** If the race goes to multiple rounds, you must secure enough #2 and #3 rankings to reach **{win_number:,}** active votes.
* **Field Target:** We recommend identifying **{int(win_number * 1.2):,}** strong supporters on your walk list to account for Election Day attrition.
""")

# --- METHODOLOGY ---
with st.expander("Methodology & DC Law 25-295"):
    st.latex(r"Win\ Number = \left\lfloor \frac{\text{Total Ballots} \times (1 - \text{Exhaustion Rate})}{2} \right\rfloor + 1")
    st.markdown("""
    This calculator reflects the **Ranked-Choice Voting** rules established by DC Initiative 83. 
    * **Plurality vs. RCV:** In a plurality race, you only need one more vote than the second-place finisher. In RCV, you must reach a majority of the active ballots.
    * **Exhaustion:** This occurs when a voter does not rank enough candidates to last until the final round of counting.
    """)