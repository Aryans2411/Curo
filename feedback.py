import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db import SessionLocal, User, ChatFeedback, PrescriptionFeedback, init_db
from sqlalchemy import func
from datetime import datetime, timedelta

st.set_page_config("Feedback Analytics", layout="wide", page_icon="📊")
init_db()

# Define pastel color scheme
PASTEL_COLORS = {
    "positive": "#A1DE93",  # Pastel green
    "negative": "#FF9AA2",  # Pastel pink
    "chat": "#B5EAD7",      # Pastel mint
    "prescription": "#FFB7B2",  # Pastel peach
    "background": "#F5F5F5",
    "text": "#333333",
    "header": "#6C63FF"     # Pastel purple
}

def fetch_feedback():
    db = SessionLocal()
    chat = db.query(ChatFeedback).all()
    presc = db.query(PrescriptionFeedback).all()
    users = db.query(User).all()
    db.close()
    return chat, presc, users

def make_df(feedback, kind="chat"):
    rows = []
    for f in feedback:
        user = f.user_id
        feedback_val = f.feedback
        timestamp = getattr(f, "timestamp", None)
        if not timestamp:
            timestamp = datetime.now()
        rows.append({
            "user_id": user,
            "feedback": feedback_val,
            "timestamp": timestamp,
            "type": kind
        })
    return pd.DataFrame(rows)

def user_map(users):
    return {u.id: u.username for u in users}

# --- Data load ---
chat, presc, users = fetch_feedback()
if not chat and not presc:
    st.warning("No feedback data found yet.")
    st.stop()

user_lookup = user_map(users)

chat_df = make_df(chat, "chat")
presc_df = make_df(presc, "prescription")

chat_df["username"] = chat_df["user_id"].map(user_lookup)
presc_df["username"] = presc_df["user_id"].map(user_lookup)

df = pd.concat([chat_df, presc_df], ignore_index=True)
df["date"] = pd.to_datetime(df["timestamp"]).dt.date
df["week"] = df["timestamp"].apply(lambda x: x - timedelta(days=x.weekday()))
df["feedback_type"] = df["feedback"].apply(lambda x: "positive" if x else "negative")

st.title("📊 Chatbot & Prescription Feedback Dashboard")
st.markdown("**Track user feedback and model performance metrics**")

# --- Summary Cards ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Feedbacks", len(df), help="All feedback entries collected")
with col2:
    st.metric("👍 Positive Rate", f"{100*df['feedback'].mean():.1f}%", 
             help="Percentage of positive feedback")
with col3:
    st.metric("💬 Chat Feedbacks", len(chat_df), 
             delta=f"{len(chat_df)/len(df)*100:.1f}% of total" if len(df) > 0 else "0%")
with col4:
    st.metric("💊 Prescription Feedbacks", len(presc_df), 
             delta=f"{len(presc_df)/len(df)*100:.1f}% of total" if len(df) > 0 else "0%")

st.markdown("---")

# --- Main Columns ---
main_col1, main_col2 = st.columns([1, 1])

with main_col1:
    # Feedback Distribution by Type
    st.subheader("Feedback Distribution by Type")
    type_fig = px.pie(
        df, 
        names='type',
        color='type',
        color_discrete_map={'chat': PASTEL_COLORS['chat'], 
                          'prescription': PASTEL_COLORS['prescription']},
        hole=0.4
    )
    type_fig.update_traces(textposition='inside', textinfo='percent+label')
    type_fig.update_layout(showlegend=False)
    st.plotly_chart(type_fig, use_container_width=True)
    
    # Weekly Feedback Trend
    st.subheader("Weekly Feedback Trend")
    weekly = df.groupby(['week', 'feedback_type', 'type']).size().reset_index(name='count')
    if not weekly.empty:
        trend_fig = px.bar(
            weekly,
            x='week',
            y='count',
            color='type',
            barmode='group',
            color_discrete_map={
                'chat': PASTEL_COLORS['chat'],
                'prescription': PASTEL_COLORS['prescription']
            },
            labels={'count': 'Feedback Count', 'week': 'Week'}
        )
        trend_fig.update_xaxes(tickformat="%b %d")
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info("No data available for weekly trends")

with main_col2:
    # Feedback Sentiment Analysis
    st.subheader("Feedback Sentiment")
    sentiment_fig = px.sunburst(
        df,
        path=['type', 'feedback_type'],
        color='feedback_type',
        color_discrete_map={
            'positive': PASTEL_COLORS['positive'],
            'negative': PASTEL_COLORS['negative']
        },
        hover_data=['type']
    )
    sentiment_fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(sentiment_fig, use_container_width=True)
    
    # Feedback by User
    st.subheader("Feedback by User")
    user_feedback = df.groupby(['username', 'feedback_type']).size().unstack(fill_value=0)
    user_feedback['total'] = user_feedback.sum(axis=1)
    user_feedback = user_feedback.sort_values('total', ascending=False).head(10)
    
    if not user_feedback.empty:
        user_fig = go.Figure()
        user_fig.add_trace(go.Bar(
            x=user_feedback.index,
            y=user_feedback.get('positive', 0),
            name='Positive',
            marker_color=PASTEL_COLORS['positive']
        ))
        user_fig.add_trace(go.Bar(
            x=user_feedback.index,
            y=user_feedback.get('negative', 0),
            name='Negative',
            marker_color=PASTEL_COLORS['negative']
        ))
        user_fig.update_layout(barmode='stack', xaxis_title="User", yaxis_title="Feedback Count")
        st.plotly_chart(user_fig, use_container_width=True)
    else:
        st.info("No user feedback data available")

st.markdown("---")
st.header("Detailed Feedback Analysis")

# --- Tabs for Detailed View ---
tab1, tab2 = st.tabs(["💬 Chat Feedback", "💊 Prescription Feedback"])

with tab1:
    if not chat_df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Sentiment Distribution")
            chat_sentiment = chat_df['feedback'].value_counts()
            fig = px.pie(
                values=chat_sentiment.values,
                names=chat_sentiment.index.map({1: 'Positive', 0: 'Negative'}),
                color_discrete_sequence=[PASTEL_COLORS['positive'], PASTEL_COLORS['negative']]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("Top Users")
            top_users = chat_df['username'].value_counts().head(5)
            fig = px.bar(
                top_users, 
                orientation='v',
                labels={'index': 'User', 'value': 'Feedback Count'},
                color_discrete_sequence=[PASTEL_COLORS['chat']]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recent Chat Feedback")
        st.dataframe(
            chat_df[['timestamp', 'username', 'feedback']]
            .sort_values('timestamp', ascending=False)
            .head(10)
            .assign(feedback=lambda x: x['feedback'].map({1: '👍', 0: '👎'}))
            .rename(columns={
                'timestamp': 'Timestamp',
                'username': 'User',
                'feedback': 'Feedback'
            }),
            hide_index=True
        )
    else:
        st.info("No chat feedback available")

with tab2:
    if not presc_df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Sentiment Distribution")
            presc_sentiment = presc_df['feedback'].value_counts()
            fig = px.pie(
                values=presc_sentiment.values,
                names=presc_sentiment.index.map({1: 'Positive', 0: 'Negative'}),
                color_discrete_sequence=[PASTEL_COLORS['positive'], PASTEL_COLORS['negative']]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("Top Users")
            top_users = presc_df['username'].value_counts().head(5)
            fig = px.bar(
                top_users, 
                orientation='v',
                labels={'index': 'User', 'value': 'Feedback Count'},
                color_discrete_sequence=[PASTEL_COLORS['prescription']]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recent Prescription Feedback")
        st.dataframe(
            presc_df[['timestamp', 'username', 'feedback']]
            .sort_values('timestamp', ascending=False)
            .head(10)
            .assign(feedback=lambda x: x['feedback'].map({1: '👍', 0: '👎'}))
            .rename(columns={
                'timestamp': 'Timestamp',
                'username': 'User',
                'feedback': 'Feedback'
            }),
            hide_index=True
        )
    else:
        st.info("No prescription feedback available")

# Apply custom styling
st.markdown(f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {PASTEL_COLORS['background']};
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {PASTEL_COLORS['header']} !important;
    }}
    
    /* Metric cards */
    [data-testid="stMetric"] {{
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    
    /* Tabs */
    [data-baseweb="tab"] {{
        background-color: white !important;
        border-radius: 8px !important;
        margin: 5px !important;
        padding: 10px 15px !important;
    }}
    
    [data-baseweb="tab"][aria-selected="true"] {{
        background-color: {PASTEL_COLORS['chat']} !important;
        color: {PASTEL_COLORS['text']} !important;
        font-weight: bold;
    }}
    
    /* Dataframes */
    .dataframe {{
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    
    /* Dividers */
    hr {{
        margin: 2rem 0;
        border-top: 2px solid {PASTEL_COLORS['prescription']};
    }}
</style>
""", unsafe_allow_html=True)