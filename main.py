import streamlit as st
import sqlite3
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="LinkedOut", page_icon="📉", layout="centered")

# --- DATABASE FUNCTIONS ---
def init_db():
    conn = sqlite3.connect('linkedout_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  content TEXT, 
                  timestamp TEXT,
                  hugs INTEGER)''')
    conn.commit()
    conn.close()

def add_post(username, content):
    conn = sqlite3.connect('linkedout_v2.db')
    c = conn.cursor()
    time_now = datetime.now().strftime("%I:%M %p · %b %d")
    c.execute("INSERT INTO posts (username, content, timestamp, hugs) VALUES (?, ?, ?, 0)", 
              (username, content, time_now))
    conn.commit()
    conn.close()

def get_posts():
    conn = sqlite3.connect('linkedout_v2.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

def add_hug(post_id):
    conn = sqlite3.connect('linkedout_v2.db')
    c = conn.cursor()
    c.execute("UPDATE posts SET hugs = hugs + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def contains_buzzwords(text):
    banned_words = [
        "synergy", "leverage", "roi", "humbled to announce", 
        "thrilled to announce", "excited to share", "circle back", 
        "thought leader", "game changer", "optimize"
    ]
    for word in banned_words:
        if word.lower() in text.lower():
            return True, word
    return False, ""

# --- APP UI ---

init_db()

st.title("📉 LinkedOut")
st.caption("No hustle. No flex. Just vibes.")

st.divider()

# --- STEP 1: WHO ARE YOU? (Top of Page) ---
st.subheader("1. Who are you today?")

# We use columns to make it look like a form row
col1, col2 = st.columns(2)

with col1:
    username = st.text_input("Display Name", value="Anonymous Burnout")

with col2:
    status_option = st.selectbox("Current Status", [
        "🟢 Touching Grass",
        "🔴 Pretending to Work",
        "🟡 Rotting in Bed",
        "🔵 Crying in the Bathroom",
        "⚪ Actually Working (Ew)",
        "✏️ Create Custom Status..."
    ])

# Custom status logic
if status_option == "✏️ Create Custom Status...":
    custom_status_text = st.text_input("Type your custom vibe:", placeholder="e.g. Eating Amala", max_chars=25)
    if custom_status_text:
        status = f"🟣 {custom_status_text}"
    else:
        status = "🟣 Mystery Vibe"
else:
    status = status_option

# Show the user what they look like
st.info(f"Posting as: **{username}** [{status}]")

st.divider()

# --- STEP 2: POST INPUT ---
st.subheader("2. Vent to the Void")

with st.form("new_post_form", clear_on_submit=True):
    new_post = st.text_area("What's wrong?", height=100, placeholder="I spilled coffee on my resume...")
    
    submitted = st.form_submit_button("Post Update", use_container_width=True)
    
    if submitted:
        if not new_post:
            st.warning("You can't post nothing. That's lazy.")
        else:
            is_toxic, word = contains_buzzwords(new_post)
            
            if is_toxic:
                st.error(f"🚫 BLOCKED: Toxic word detected: '{word}'. Be real.")
            else:
                full_username = f"{username} [{status}]"
                add_post(full_username, new_post)
                st.success("Posted.")
                st.rerun()

st.divider()

# --- STEP 3: THE FEED ---
st.subheader("The Feed")

posts = get_posts()

if not posts:
    st.info("No posts yet. Be the first failure.")

for post in posts:
    post_id = post[0]
    user = post[1]
    content = post[2]
    timestamp = post[3]
    hugs = post[4]

    with st.container(border=True):
        # Post Header
        st.markdown(f"**{user}**")
        st.caption(f"{timestamp}")
        
        # Post Body
        st.markdown(content)
        
        # Action Buttons (Full width hug button)
        if st.button(f"🫂 Send Hug ({hugs})", key=f"hug_{post_id}", use_container_width=True):
            add_hug(post_id)
            st.rerun()
