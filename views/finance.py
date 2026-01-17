import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from modules import database as db

CATEGORIES = [
    "Income: Dad",
    "Income: Other",
    "Expense: Girlfriend",
    "Expense: Food",
    "Expense: Travel",
    "Expense: Other",
    "Invest: Nifty 50",
    "Invest: Gold",
]


def render():
    st.header(" Finance — The 10% Rule")
    
    records = db.get_finance(limit=500)
    
    # Motivational stats at top
    if records:
        df = pd.DataFrame(records, columns=["id", "date", "category", "amount", "note"])
        
        total_income = df[df["category"].str.startswith("Income")]["amount"].sum()
        total_expenses = df[df["category"].str.startswith("Expense")]["amount"].sum()
        total_invested = df[df["category"].str.startswith("Invest")]["amount"].sum()
        
        investment_rate = (total_invested / total_income * 100) if total_income > 0 else 0
        
        st.write("")  # spacing
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(" Total Income", f"{total_income:.2f}", delta="Keep earning!")
        
        with col2:
            st.metric(" Total Expenses", f"{total_expenses:.2f}", delta=f"{(total_expenses/total_income*100):.1f}%" if total_income > 0 else "0%")
        
        with col3:
            if investment_rate >= 10:
                st.metric(" Investment Rate", f"{investment_rate:.1f}%", delta="Goal Met! ")
            elif investment_rate >= 5:
                st.metric(" Investment Rate", f"{investment_rate:.1f}%", delta="Almost there!")
            else:
                st.metric(" Investment Rate", f"{investment_rate:.1f}%", delta="Need 10%!")
        
        st.write("")
        st.write("")
        st.divider()
    
    st.subheader(" Add Transaction")
    st.write("")

    # Toggle between income and expense
    tab1, tab2, tab3 = st.tabs(["➕ Income", "➖ Expense", "📈 Investment"])
    
    with tab1:
        st.write("**Add Income**")
        with st.form("income_form"):
            income_category = st.selectbox("Income Source", 
                ["Dad", "Freelance", "Bonus", "Gift", "Other"], 
                key="income_category")
            amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", key="income_amount")
            note = st.text_input("Note (optional)", key="income_note")
            st.write("")
            submitted = st.form_submit_button("✅ Add Income", use_container_width=True)
            if submitted and amount > 0:
                db.add_finance_entry(date.today().isoformat(), f"Income: {income_category}", float(amount), note)
                st.success("💰 Income added!")
                st.rerun()
    
    with tab2:
        st.write("**Add Expense**")
        with st.form("expense_form"):
            expense_category = st.selectbox("Expense Type", 
                ["Girlfriend", "Food", "Travel", "Entertainment", "Shopping", "Bills", "Other"],
                key="expense_category")
            amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", key="expense_amount")
            note = st.text_input("Note (optional)", key="expense_note")
            st.write("")
            submitted = st.form_submit_button("❌ Add Expense", use_container_width=True)
            if submitted and amount > 0:
                db.add_finance_entry(date.today().isoformat(), f"Expense: {expense_category}", float(amount), note)
                st.success("✅ Expense recorded!")
                st.rerun()
    
    with tab3:
        st.write("**Add Investment**")
        with st.form("investment_form"):
            investment_category = st.selectbox("Investment Type",
                ["Nifty 50", "Gold", "Stocks", "Crypto", "Savings", "Other"],
                key="investment_category")
            amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", key="investment_amount")
            note = st.text_input("Note (optional)", key="investment_note")
            st.write("")
            submitted = st.form_submit_button("📊 Add Investment", use_container_width=True)
            if submitted and amount > 0:
                db.add_finance_entry(date.today().isoformat(), f"Invest: {investment_category}", float(amount), note)
                st.success("📈 Investment added!")
                st.rerun()

    if not records:
        st.write("")
        st.info(" Add your first transaction to start tracking your finances!")
        return

    df = pd.DataFrame(records, columns=["id", "date", "category", "amount", "note"])

    # Donut: expenses only
    st.write("")
    st.write("")
    st.divider()
    st.subheader(" Expense Breakdown")
    st.write("")
    exp_df = df[df["category"].str.startswith("Expense")]
    if not exp_df.empty:
        fig_exp = px.pie(exp_df, names="category", values="amount", hole=0.5, 
                         title="Where Your Money Goes",
                         color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_exp, width='stretch')
        
        st.write("")
        # Top expense
        top_expense = exp_df.groupby("category")["amount"].sum().idxmax()
        top_amount = exp_df.groupby("category")["amount"].sum().max()
        st.info(f" Biggest expense: **{top_expense}** ({top_amount:.2f})")
    else:
        st.info("Add expense entries to see the breakdown.")

    # Line: investments trend
    st.write("")
    st.write("")
    st.divider()
    st.subheader(" Investment Growth")
    st.write("")
    inv_df = df[df["category"].str.startswith("Invest")].copy()
    if not inv_df.empty:
        inv_df["date_only"] = pd.to_datetime(inv_df["date"]).dt.date
        trend = inv_df.groupby("date_only")["amount"].sum().cumsum().reset_index()
        fig_inv = px.line(trend, x="date_only", y="amount", markers=True, 
                          title="Your Wealth Journey",
                          labels={"amount": "Total Invested", "date_only": "Date"})
        fig_inv.update_traces(line_color='#007aff', line_width=3)
        st.plotly_chart(fig_inv, width='stretch')
        
        st.write("")
        current_total = trend["amount"].iloc[-1]
        st.success(f" Total Invested: {current_total:.2f}")
    else:
        st.info("Add investment entries to see the trend.")

    st.write("")
    st.write("")
    st.divider()
    st.subheader(" Recent Transactions")
    st.write("")
    recent = db.get_recent_finance(limit=5)
    recent_df = pd.DataFrame(recent, columns=["id", "date", "category", "amount", "note"])
    st.dataframe(recent_df[["date", "category", "amount", "note"]], use_container_width=True, hide_index=True)
