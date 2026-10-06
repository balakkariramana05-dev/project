import streamlit as st
import pandas as pd
import plotly.express as px
import ollama
import os

# -------------------------------------------------
# PAGE SETTINGS
# -------------------------------------------------

st.set_page_config(
    page_title="Subscription Detective",
    page_icon="💰",
    layout="wide"
)

# -------------------------------------------------
# FILE SETTINGS
# -------------------------------------------------

DATA_FILE = "subscriptions.csv"

# -------------------------------------------------
# LOAD SAVED DATA
# -------------------------------------------------

if "subscriptions" not in st.session_state:

    if os.path.exists(DATA_FILE):

        try:

            saved_df = pd.read_csv(DATA_FILE)

            st.session_state.subscriptions = (
                saved_df.to_dict("records")
            )

        except Exception:

            st.session_state.subscriptions = []

    else:

        st.session_state.subscriptions = []

# -------------------------------------------------
# SAVE DATA FUNCTION
# -------------------------------------------------

def save_data():

    df = pd.DataFrame(
        st.session_state.subscriptions
    )

    df.to_csv(
        DATA_FILE,
        index=False
    )

# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title("💰 Subscription Detective")

st.write(
    "AI-powered personal finance analyzer"
)

st.caption(
    "💾 Your subscription data is automatically saved."
)

# -------------------------------------------------
# CSV UPLOAD
# -------------------------------------------------

st.header("📁 Import Subscription Data")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    try:

        uploaded_df = pd.read_csv(
            uploaded_file
        )

        required_columns = [
            "Subscription",
            "Category",
            "Monthly Cost",
            "Usage"
        ]

        if all(
            column in uploaded_df.columns
            for column in required_columns
        ):

            st.session_state.subscriptions = (
                uploaded_df[
                    required_columns
                ].to_dict("records")
            )

            save_data()

            st.success(
                "CSV data uploaded and saved successfully!"
            )

        else:

            st.error(
                "CSV must contain these columns: "
                "Subscription, Category, Monthly Cost, Usage"
            )

    except Exception:

        st.error(
            "Could not read the CSV file."
        )

# -------------------------------------------------
# ADD SUBSCRIPTION
# -------------------------------------------------

st.header("➕ Add a Subscription")

col1, col2 = st.columns(2)

with col1:

    name = st.text_input(
        "Subscription Name"
    )

    category = st.selectbox(
        "Category",
        [
            "Entertainment",
            "Education",
            "Fitness",
            "Shopping",
            "Cloud Storage",
            "Other"
        ]
    )

with col2:

    cost = st.number_input(
        "Monthly Cost (₹)",
        min_value=0.0,
        step=10.0
    )

    usage = st.selectbox(
        "How often do you use it?",
        [
            "High",
            "Medium",
            "Low"
        ]
    )

if st.button("➕ Add Subscription"):

    if name and cost > 0:

        subscription = {
            "Subscription": name,
            "Category": category,
            "Monthly Cost": cost,
            "Usage": usage
        }

        st.session_state.subscriptions.append(
            subscription
        )

        save_data()

        st.success(
            f"{name} added successfully!"
        )

    else:

        st.error(
            "Please enter subscription name and cost."
        )

# -------------------------------------------------
# MAIN APPLICATION
# -------------------------------------------------

if st.session_state.subscriptions:

    df = pd.DataFrame(
        st.session_state.subscriptions
    )

    # -------------------------------------------------
    # SUBSCRIPTIONS
    # -------------------------------------------------

    st.header("📋 Your Subscriptions")

    st.dataframe(
        df,
        use_container_width=True
    )

    # -------------------------------------------------
    # DOWNLOAD CSV
    # -------------------------------------------------

    csv_data = df.to_csv(
        index=False
    )

    st.download_button(
        label="📥 Download Subscription Data",
        data=csv_data,
        file_name="subscription_data.csv",
        mime="text/csv"
    )

    # -------------------------------------------------
    # DELETE SUBSCRIPTIONS
    # -------------------------------------------------

    st.header("🗑️ Manage Subscriptions")

    delete_subscriptions = st.multiselect(
        "Select subscriptions to delete:",
        df["Subscription"].tolist()
    )

    if st.button("🗑️ Delete Selected"):

        if delete_subscriptions:

            st.session_state.subscriptions = [
                item
                for item in st.session_state.subscriptions
                if item["Subscription"]
                not in delete_subscriptions
            ]

            save_data()

            st.success(
                "Selected subscriptions deleted successfully!"
            )

            st.rerun()

        else:

            st.warning(
                "Please select at least one subscription."
            )

    if st.button(
        "🧹 Clear All Subscriptions"
    ):

        st.session_state.subscriptions = []

        if os.path.exists(DATA_FILE):

            os.remove(DATA_FILE)

        st.success(
            "All subscriptions have been cleared."
        )

        st.rerun()

    # -------------------------------------------------
    # SPENDING SUMMARY
    # -------------------------------------------------

    monthly_total = df[
        "Monthly Cost"
    ].sum()

    yearly_total = (
        monthly_total * 12
    )

    st.header("💰 Spending Summary")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Subscriptions",
            len(df)
        )

    with col2:

        st.metric(
            "Monthly Spending",
            f"₹{monthly_total:,.2f}"
        )

    with col3:

        st.metric(
            "Yearly Spending",
            f"₹{yearly_total:,.2f}"
        )

    # -------------------------------------------------
    # SPENDING ANALYSIS
    # -------------------------------------------------

    st.header("📊 Spending Analysis")

    category_spending = (
        df.groupby("Category")[
            "Monthly Cost"
        ]
        .sum()
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_bar = px.bar(
            category_spending,
            x="Category",
            y="Monthly Cost",
            title="Monthly Spending by Category"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    with col2:

        fig_pie = px.pie(
            category_spending,
            names="Category",
            values="Monthly Cost",
            title="Spending Distribution"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

    # -------------------------------------------------
    # MOST EXPENSIVE
    # -------------------------------------------------

    st.header(
        "🏆 Most Expensive Subscription"
    )

    expensive = df.loc[
        df["Monthly Cost"].idxmax()
    ]

    st.info(
        f"**{expensive['Subscription']}** "
        f"is your most expensive subscription "
        f"at **₹{expensive['Monthly Cost']:,.2f}/month**."
    )

    # -------------------------------------------------
    # LOW USAGE DETECTION
    # -------------------------------------------------

    st.header(
        "🔎 Subscription Detective"
    )

    low_usage = df[
        df["Usage"] == "Low"
    ]

    if len(low_usage) > 0:

        st.warning(
            "These subscriptions have low usage "
            "and may be unnecessary:"
        )

        st.dataframe(
            low_usage,
            use_container_width=True
        )

        possible_monthly_savings = (
            low_usage["Monthly Cost"].sum()
        )

        possible_yearly_savings = (
            possible_monthly_savings * 12
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Possible Monthly Savings",
                f"₹{possible_monthly_savings:,.2f}"
            )

        with col2:

            st.metric(
                "Possible Yearly Savings",
                f"₹{possible_yearly_savings:,.2f}"
            )

    else:

        st.success(
            "🎉 No low-usage subscriptions detected!"
        )

    # -------------------------------------------------
    # SAVINGS SIMULATOR
    # -------------------------------------------------

    st.header(
        "💰 Savings Simulator"
    )

    st.write(
        "Select the subscriptions you are "
        "considering cancelling."
    )

    selected_subscriptions = st.multiselect(
        "Choose subscriptions:",
        df["Subscription"].tolist()
    )

    if selected_subscriptions:

        selected_df = df[
            df["Subscription"].isin(
                selected_subscriptions
            )
        ]

        monthly_savings = (
            selected_df["Monthly Cost"].sum()
        )

        yearly_savings = (
            monthly_savings * 12
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "💰 Monthly Savings",
                f"₹{monthly_savings:,.2f}"
            )

        with col2:

            st.metric(
                "💰 Yearly Savings",
                f"₹{yearly_savings:,.2f}"
            )

        st.success(
            f"You could save "
            f"₹{yearly_savings:,.2f} per year "
            f"by cancelling the selected subscriptions."
        )

    else:

        st.info(
            "Select one or more subscriptions "
            "to calculate your savings."
        )

    # -------------------------------------------------
    # AI ANALYSIS
    # -------------------------------------------------

    st.header(
        "🤖 AI Subscription Detective"
    )

    st.write(
        "Let Ollama analyze your subscriptions "
        "and give you personalized suggestions."
    )

    if st.button(
        "🔍 Analyze My Spending with AI"
    ):

        subscription_data = df.to_string(
            index=False
        )

        prompt = f"""
You are an intelligent personal finance assistant.

Analyze the following subscription data:

{subscription_data}

Total monthly spending: ₹{monthly_total:.2f}
Total yearly spending: ₹{yearly_total:.2f}

Give a simple financial analysis.

Identify:

1. Unnecessary or low-value subscriptions.
2. Expensive subscriptions.
3. Spending patterns.
4. Subscriptions the user should consider reviewing.
5. Ways to save money.
6. Estimated possible monthly and yearly savings.

Use simple language.

Do not make assumptions that are not supported by the data.

Format your response with clear headings and bullet points.
"""

        try:

            with st.spinner(
                "🤖 AI is analyzing your subscriptions..."
            ):

                response = ollama.chat(
                    model="llama3.2",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

            answer = response[
                "message"
            ]["content"]

            st.subheader(
                "🕵️ AI Detective Report"
            )

            st.markdown(answer)

        except Exception:

            st.error(
                "Could not connect to Ollama. "
                "Please make sure Ollama is running "
                "and llama3.2 is installed."
            )

else:

    st.info(
        "👆 Add your first subscription above "
        "to start analyzing your spending."
    )