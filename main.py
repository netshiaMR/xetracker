import pandas as pd
import streamlit as st

# Define Absa color pattern
absa_colors = {
    "primary": "#BF0029",  # Absa primary red
    "secondary": "#EBE5E6",  # Light neutral color for background
    "text": "#262224",  # Dark text color
    "accent": "#FEB5B8",  # Light red accent
}

# Streamlit App Title and Icon
st.set_page_config(page_title="Credit Card Calculator", page_icon="🏦")

# Title Section
st.title("🏦 Credit Card Payment Calculator")
st.markdown(
    f"<h3 style='color:{absa_colors['primary']};'>Credit Card Repayment Schedule</h3>",
    unsafe_allow_html=True,
)

# Streamlit App Inputs
st.sidebar.header("Calculator Settings")
start_balance = st.sidebar.number_input("Starting Balance", value=198000, step=1000)
monthly_interest_rate = st.sidebar.number_input("Monthly Interest Rate (%)", value=2.08)
admin_fee = st.sidebar.number_input("Admin Fee", value=1200)
repayment = st.sidebar.number_input("Monthly Repayment Amount", value=7500, step=100)

# Month selection for start
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
start_month_name = st.sidebar.selectbox("Start Month", months)
start_month = months.index(start_month_name) + 1

# Number of months for the repayment plan
num_months = st.sidebar.slider("Repayment Duration (Months)", min_value=1, max_value=36, value=18)

# Extra Contributions Section
st.sidebar.subheader("Extra Contributions")
num_contributions = st.sidebar.number_input("Number of Extra Contributions", min_value=0, max_value=12, value=3, step=1)

extra_contributions = {}
for i in range(num_contributions):
    col1, col2 = st.sidebar.columns(2)
    with col1:
        contrib_month = st.selectbox(f"Month for Contribution {i+1}", months, key=f"month_{i}")
        contrib_year = st.number_input(f"Year for Contribution {i+1}", min_value=2024, max_value=2030, value=2024, step=1, key=f"year_{i}")
    with col2:
        amount = st.number_input(f"Amount for Contribution {i+1}", min_value=0, value=5000, step=500, key=f"amount_{i}")

    # Format the month and year to match the DataFrame output
    month_year = pd.Timestamp(year=contrib_year, month=months.index(contrib_month)+1, day=1).strftime('%B %Y')
    extra_contributions[month_year] = amount

# Credit Card Calculator Class
class CreditCardCalculator:
    def __init__(self, start_balance, monthly_interest_rate, admin_fee):
        self.start_balance = start_balance
        self.monthly_interest_rate = monthly_interest_rate / 100
        self.admin_fee = admin_fee
        self.schedule = []

    def calculate_schedule(self, months, start_month, repayment, extra_contributions=None):
        balance = self.start_balance
        extra_contributions = extra_contributions or {}

        for i in range(months):
            # Determine current month and year
            month_index = (start_month - 1 + i) % 12 + 1
            year = 2024 + (start_month - 1 + i) // 12
            month_name = pd.Timestamp(year=year, month=month_index, day=1).strftime('%B %Y')

            # Get the extra contribution for the current month, if available
            contribution = extra_contributions.get(month_name, 0)

            # Calculate interest and ending balance
            interest = round(balance * self.monthly_interest_rate, 2)
            payment = repayment
            ending_balance = balance + interest + self.admin_fee - payment - contribution
            available_credit = self.start_balance - ending_balance

            # Append monthly data
            self.schedule.append({
                "Month": month_name,
                "Beginning Balance": round(balance, 2),
                "Interest": interest,
                "Admin Fees": self.admin_fee,
                "Payment": payment,
                "Extra Contribution": contribution,
                "Account Balance": round(ending_balance, 2),
                "Available Credit": round(available_credit, 2)
            })

            # Update balance for next month
            balance = ending_balance

    def get_schedule(self):
        return pd.DataFrame(self.schedule)

# Initialize the calculator and calculate schedule
calculator = CreditCardCalculator(start_balance, monthly_interest_rate, admin_fee)
calculator.calculate_schedule(num_months, start_month, repayment, extra_contributions)

# Retrieve the schedule
schedule_df = calculator.get_schedule()

# Display the schedule in a styled table
st.markdown(
    f"<h4 style='color:{absa_colors['primary']};'>Repayment Schedule</h4>",
    unsafe_allow_html=True,
)
st.dataframe(schedule_df)

# Download option
csv = schedule_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Repayment Schedule as CSV",
    data=csv,
    file_name="credit_card_repayment_schedule.csv",
    mime="text/csv",
)

# Custom CSS Styling
st.markdown(
    f"""
    <style>
        body {{
            background-color: {absa_colors['secondary']};
            color: {absa_colors['text']};
        }}
        .stButton > button {{
            background-color: {absa_colors['primary']};
            color: white;
            border-radius: 8px;
        }}
        .stDataFrame {{
            border: 2px solid {absa_colors['primary']};
        }}
    </style>
    """,
    unsafe_allow_html=True
)
