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

# --- MANUAL MODERATION ---
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
st.subheader("The Anti-Professional Network")
st.markdown("No hustle. No flex. Just vibes.")

# --- SIDEBAR: USER PROFILE ---
with st.sidebar:
    st.header("Who are you today?")
    username = st.text_input("Display Name", value="Anonymous Burnout")
    
    # Status Selection with Custom Option
    status_option = st.selectbox("Current Status", [
        "🟢 Touching Grass",
        "🔴 Pretending to Work",
        "🟡 Rotting in Bed",
        "🔵 Crying in the Bathroom",
        "⚪ Actually Working (Ew)",
        "✏️ Create Custom Status..."
    ])
    
    # Logic: If they choose 'Custom', show a text box
    if status_option == "✏️ Create Custom Status...":
        custom_status_text = st.text_input("Type your vibe:", placeholder="e.g. Eating Amala", max_chars=25)
        # If they leave it blank, give them a default
        if custom_status_text:
            status = f"🟣 {custom_status_text}"
        else:
            status = "🟣 Mystery Vibe"
    else:
        status = status_option
        
    st.divider()
    st.caption("This works like a forum. Anyone who accesses this app sees the same feed.")

# --- POST INPUT ---
with st.form("new_post_form", clear_on_submit=True):
    st.write("Create a Post:")
    new_post = st.text_area("Vent here...", height=100, placeholder="I spilled coffee on my resume...")
    
    submitted = st.form_submit_button("Post Update")
    
    if submitted:
        if not new_post:
            st.warning("You can't post nothing. That's lazy.")
        else:
            is_toxic, word = contains_buzzwords(new_post)
            
            if is_toxic:
                st.error(f"🚫 BLOCKED: We detected toxic corporate slang: '{word}'. Get that LinkedIn energy out of here.")
            else:
                full_username = f"{username} [{status}]"
                add_post(full_username, new_post)
                st.success("Posted to the void.")
                st.rerun()

st.divider()

# --- THE FEED ---
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
        col1, col2 = st.columns([0.85, 0.15])
        
        with col1:
            st.markdown(f"**@{user}**")
            st.caption(f"{timestamp}")
            st.info(content)
            
        with col2:
            st.write("")
            if st.button(f"🫂 {hugs}", key=f"hug_{post_id}"):
                add_hug(post_id)
                st.rerun()