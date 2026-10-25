
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Expense Tracker")
st.write("Record your expenses and understand your spending habits.")

# ----------------------------
# Data storage
# ----------------------------
DATA_FILE = Path(__file__).parent / "expenses.csv"

COLUMNS = [
    "Date",
    "Amount",
    "Category",
    "Payment Method",
    "Description"
]

if not DATA_FILE.exists():
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)


def load_expenses():
    df = pd.read_csv(DATA_FILE)

    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    df = df.dropna(subset=["Date", "Amount"])
    return df


# ----------------------------
# Add a new expense
# ----------------------------
st.header("➕ Add a New Expense")

with st.form("expense_form", clear_on_submit=True):
    expense_date = st.date_input("Expense date", value=date.today())

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.01,
        value=100.0,
        step=10.0
    )

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Education",
            "Shopping",
            "Entertainment",
            "Bills",
            "Health",
            "Other"
        ]
    )

    payment_method = st.selectbox(
        "Payment method",
        ["Cash", "UPI", "Debit Card", "Credit Card", "Other"]
    )

    description = st.text_input(
        "Description",
        placeholder="Example: Lunch, bus ticket, notebook"
    )

    submitted = st.form_submit_button("Save Expense")

    if submitted:
        new_expense = pd.DataFrame([{
            "Date": expense_date.isoformat(),
            "Amount": amount,
            "Category": category,
            "Payment Method": payment_method,
            "Description": description.strip()
        }])

        new_expense.to_csv(
            DATA_FILE,
            mode="a",
            header=False,
            index=False
        )

        st.success("Expense saved successfully!")
        st.rerun()


# ----------------------------
# Load and display expenses
# ----------------------------
df = load_expenses()

st.divider()
st.header("📊 Expense Dashboard")

if df.empty:
    st.info("No expenses recorded yet. Add your first expense above.")
else:
    # Filters
    st.subheader("Filter Expenses")

    col1, col2 = st.columns(2)

    with col1:
        months = sorted(
            df["Date"].dt.strftime("%Y-%m").unique(),
            reverse=True
        )

        selected_month = st.selectbox(
            "Select month",
            ["All months"] + months
        )

    with col2:
        categories = sorted(df["Category"].dropna().unique())

        selected_category = st.selectbox(
            "Select category",
            ["All categories"] + categories
        )

    filtered = df.copy()

    if selected_month != "All months":
        filtered = filtered[
            filtered["Date"].dt.strftime("%Y-%m") == selected_month
        ]

    if selected_category != "All categories":
        filtered = filtered[
            filtered["Category"] == selected_category
        ]

    # Summary metrics
    total = filtered["Amount"].sum()
    count = len(filtered)
    average = total / count if count else 0

    m1, m2, m3 = st.columns(3)

    m1.metric("Total Expenses", f"₹{total:,.2f}")
    m2.metric("Number of Transactions", count)
    m3.metric("Average Expense", f"₹{average:,.2f}")

    # Charts
    st.subheader("Spending by Category")

    if not filtered.empty:
        category_totals = (
            filtered.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_totals)

        st.subheader("Monthly Spending Trend")

        monthly_totals = (
            filtered.assign(
                Month=filtered["Date"].dt.to_period("M").astype(str)
            )
            .groupby("Month")["Amount"]
            .sum()
            .sort_index()
        )

        st.line_chart(monthly_totals)

    else:
        st.info("No expenses match the selected filters.")

    # Transaction table
    st.subheader("🧾 Expense History")

    display_df = filtered.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        display_df.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    # Download filtered expenses
    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Expenses (CSV)",
        data=csv_data,
        file_name="my_expenses.csv",
        mime="text/csv"
    )

st.caption("Your expenses are stored locally in expenses.csv.")
