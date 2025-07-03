import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db import SessionLocal, User, ChatFeedback, PrescriptionFeedback, init_db
from sqlalchemy import func
from datetime import datetime, timedelta

st.set_page_config("Feedback Analytics", layout="wide", page_icon="📊")
init_db()

COLORS = {
    "positive": "#4CAF50",
    "negative": "#F44336",
    "chat": "#2196F3",
    "prescription": "#FF9800",
    "background": "var(--background-color)",
    "text": "var(--text-color)",
    "header": "#9C27B0",
    "card": "var(--card-background-color)"
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

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Feedbacks", len(df))
with col2:
    st.metric("👍 Positive Rate", f"{100*df['feedback'].mean():.1f}%")
with col3:
    st.metric("💬 Chat Feedbacks", len(chat_df), 
             delta=f"{len(chat_df)/len(df)*100:.1f}% of total" if len(df) > 0 else "0%")
with col4:
    st.metric("💊 Prescription Feedbacks", len(presc_df), 
             delta=f"{len(presc_df)/len(df)*100:.1f}% of total" if len(df) > 0 else "0%")

st.markdown("---")

main_col1, main_col2 = st.columns([1, 1])

with main_col1:
    st.subheader("Feedback Distribution by Type")
    type_fig = px.pie(
        df, 
        names='type',
        color='type',
        color_discrete_map={'chat': COLORS['chat'], 
                          'prescription': COLORS['prescription']},
        hole=0.4
    )
    type_fig.update_traces(textposition='inside', textinfo='percent+label')
    type_fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'])
    )
    st.plotly_chart(type_fig, use_container_width=True)
    
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
                'chat': COLORS['chat'],
                'prescription': COLORS['prescription']
            },
            labels={'count': 'Feedback Count', 'week': 'Week'}
        )
        trend_fig.update_xaxes(tickformat="%b %d")
        trend_fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text']),
            xaxis=dict(color=COLORS['text']),
            yaxis=dict(color=COLORS['text'])
        )
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info("No data available for weekly trends")

with main_col2:
    st.subheader("Feedback Sentiment")
    sentiment_fig = px.sunburst(
        df,
        path=['type', 'feedback_type'],
        color='feedback_type',
        color_discrete_map={
            'positive': COLORS['positive'],
            'negative': COLORS['negative']
        },
        hover_data=['type']
    )
    sentiment_fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'])
    )
    st.plotly_chart(sentiment_fig, use_container_width=True)
    
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
            marker_color=COLORS['positive']
        ))
        user_fig.add_trace(go.Bar(
            x=user_feedback.index,
            y=user_feedback.get('negative', 0),
            name='Negative',
            marker_color=COLORS['negative']
        ))
        user_fig.update_layout(
            barmode='stack', 
            xaxis_title="User", 
            yaxis_title="Feedback Count",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text']),
            xaxis=dict(color=COLORS['text']),
            yaxis=dict(color=COLORS['text']),
            legend=dict(font=dict(color=COLORS['text']))
        )
        st.plotly_chart(user_fig, use_container_width=True)
    else:
        st.info("No user feedback data available")

st.markdown("---")
st.header("Detailed Feedback Analysis")

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
                color_discrete_sequence=[COLORS['positive'], COLORS['negative']]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text'])
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("Top Users")
            top_users = chat_df['username'].value_counts().head(5)
            fig = px.bar(
                top_users, 
                orientation='v',
                labels={'index': 'User', 'value': 'Feedback Count'},
                color_discrete_sequence=[COLORS['chat']]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text']),
                xaxis=dict(color=COLORS['text']),
                yaxis=dict(color=COLORS['text'])
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
            hide_index=True,
            use_container_width=True
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
                color_discrete_sequence=[COLORS['positive'], COLORS['negative']]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text'])
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("Top Users")
            top_users = presc_df['username'].value_counts().head(5)
            fig = px.bar(
                top_users, 
                orientation='v',
                labels={'index': 'User', 'value': 'Feedback Count'},
                color_discrete_sequence=[COLORS['prescription']]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text']),
                xaxis=dict(color=COLORS['text']),
                yaxis=dict(color=COLORS['text'])
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
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No prescription feedback available")

st.markdown(f"""
<style>
    :root {{
        --background-color: var(--background-color);
        --text-color: var(--text-color);
        --card-background-color: var(--secondary-background-color);
    }}
    
    [data-testid="stMetric"] {{
        background-color: var(--card-background-color);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid var(--border-color);
    }}
    
    [data-testid="stMetricValue"] {{
        color: var(--text-color) !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: var(--text-color) !important;
    }}
    
    [data-baseweb="tab"] {{
        background-color: var(--card-background-color) !important;
        border-radius: 8px !important;
        margin: 5px !important;
        padding: 10px 15px !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    [data-baseweb="tab"][aria-selected="true"] {{
        background-color: {COLORS['chat']} !important;
        color: white !important;
        font-weight: bold;
    }}
    
    .dataframe {{
        background-color: var(--card-background-color) !important;
        color: var(--text-color) !important;
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }}
    
    .dataframe th, .dataframe td {{
        color: var(--text-color) !important;
    }}
    
    hr {{
        margin: 2rem 0;
        border-top: 2px solid {COLORS['prescription']};
    }}
    
    .js-plotly-plot .plotly {{
        background: transparent !important;
    }}
</style>
""", unsafe_allow_html=True)