import streamlit as st
import random
import time
import json
import os
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="Church Word Scramble", page_icon="✝️", layout="centered")

WORDS = [
"Pastor","Abasi","Praise","Omega","Christian","Salvation","Prayer","Singing","Offering","Keyboard",
"Redeemed","Abasifreke","Minister","Microphone","Faith","Amplifier","Announcement","Worship","Assistant","Usher",
"Department","Deacon","Pulpit","Chairs","Tithe",
"Bible","Grace","Mercy","Altar","Resurrection",
"Spirit","Gospel","Chapel","Baptism","Trinity",
"Glory","Anointing","Blessing","Temple","Prophet",
"Creation","Cross","Heaven","Miracle","Rapture",
"Testimony","Victory","Wisdom","Zion","Covenant"
]

FILE = "ted_leaderboard.json"
FILE2 = "ted_answers.json"
FILE3 = "ted_feedback.json"
AUDIO_FILE = "oceans.mp3"

@st.cache_resource
def get_audio_bytes():
    if os.path.exists(AUDIO_FILE):
        with open(AUDIO_FILE, "rb") as f:
            return f.read()
    return None

if "theme" not in st.session_state: st.session_state.theme = "dark"
def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

col_t1, col_t2 = st.columns([4,1])
with col_t2:
    st.button("☀️ Light" if st.session_state.theme=="dark" else "🌙 Dark", on_click=toggle_theme)

bg = "#FFFFFF" if st.session_state.theme=="light" else "#0A1931"
box_bg = "#FFF9E6" if st.session_state.theme=="light" else "white"

st.markdown(f"""
<style>
.stApp {{ background: {bg}!important; }}
h1 {{ color: #FFD700!important; text-align:center; font-weight:900; }}
.stTextInput input,.stTextArea textarea {{ background: white!important; color: black!important; border: 2px solid #FFD700!important; border-radius:10px; }}
.stButton button {{ background: linear-gradient(90deg, #FFD700, #FFC300)!important; color: #0A1931!important; font-weight:bold; border-radius:25px; border:none; }}
.instruction-box {{ background: {box_bg}; border:3px solid #FFD700; border-radius:15px; padding:15px; margin:10px 0; }}
.instruction-box p {{ color: #0A1931!important; font-weight:800!important; }}
.footer {{ position: fixed; bottom:0; left:0; width:100%; background:#FFD700; color:#0A1931; text-align:center; padding:8px; font-weight:900; z-index:1000; }}
</style>
""", unsafe_allow_html=True)

def scramble(word):
    l=list(word)
    while True:
        random.shuffle(l)
        s="".join(l)
        if s.lower()!=word.lower(): return s.upper()

def get_remark(s,t):
    if t==0: return ""
    p=s/t*100
    if p==100: return "🏆 PERFECT! You are a Champion!"
    if p>=80: return "🔥 EXCELLENT! Keep it up!"
    if p>=60: return "👏 VERY GOOD! You can do better!"
    if p>=40: return "🙂 GOOD! Aim higher!"
    if p>=20: return "🤔 FAIR! More study needed!"
    return "😢 Poor attempt! Try again!"

def get_rank_display(r):
    if r==1: return "1ST"
    if r==2: return "2ND"
    if r==3: return "3RD"
    suf="TH" if 11<=r%100<=13 else {1:"ST",2:"ND",3:"RD"}.get(r%10,"TH")
    return f"{r}{suf}"

def get_medal(r):
    if r==1: return "🥇"
    if r==2: return "🥈"
    if r==3: return "🥉"
    return f"{r}."

def load_board():
    if os.path.exists(FILE):
        try:
            with open(FILE,"r") as f: return json.load(f)
        except: return []
    return []
def save_board(b):
    with open(FILE,"w") as f: json.dump(b,f,indent=2)
def load_answers():
    if os.path.exists(FILE2):
        try:
            with open(FILE2,"r") as f: return json.load(f)
        except: return []
    return []
def save_answers(a):
    with open(FILE2,"w") as f: json.dump(a,f,indent=2)
def load_feedback():
    if os.path.exists(FILE3):
        try:
            with open(FILE3,"r") as f: return json.load(f)
        except: return []
    return []
def save_feedback(a):
    with open(FILE3,"w") as f: json.dump(a,f,indent=2)

if "started" not in st.session_state: st.session_state.started=False
if "name" not in st.session_state: st.session_state.name=""
if "quiz" not in st.session_state: st.session_state.quiz=[]
if "start_time" not in st.session_state: st.session_state.start_time=0
if "submitted" not in st.session_state: st.session_state.submitted=False
if "star_rating" not in st.session_state: st.session_state.star_rating=0
if "current_q" not in st.session_state: st.session_state.current_q=0
if "hint_used" not in st.session_state: st.session_state.hint_used={}
if "hint_count" not in st.session_state: st.session_state.hint_count=0
if "auto_triggered" not in st.session_state: st.session_state.auto_triggered=False
if "show_grid" not in st.session_state: st.session_state.show_grid=False
if "answers" not in st.session_state: st.session_state.answers={}

with st.expander("🔒 Host Login"):
    pwd=st.text_input("Enter Password",type="password",key="host_pwd")
    if pwd=="TED2026":
        board=load_board()
        feedbacks=load_feedback()
        if feedbacks:
            avg = sum(f['rating'] for f in feedbacks)/len(feedbacks)
            st.write(f"### ⭐ {avg:.1f} / 5.0 from {len(feedbacks)} users")
            st.dataframe(feedbacks, use_container_width=True)
        if board:
            board_sorted=sorted(board,key=lambda x:x.get("Score",0),reverse=True)
            st.write(f"### 🏆 Leaderboard ({len(board_sorted)})")
            st.dataframe(board_sorted,use_container_width=True)
            if st.button("Clear All Data"):
                save_board([]); save_answers([]); save_feedback([]); st.session_state.clear(); st.rerun()
        else: st.info("No one has played yet.")
    elif pwd!="": st.error("❌ Incorrect")

if not st.session_state.started:
    st.title("✝️ CHURCH WORD SCRAMBLE")
    st.markdown("<h3 style='text-align:center; color:#FFD700;'>TED Innovations 2026</h3>", unsafe_allow_html=True)
    feedbacks=load_feedback()
    if feedbacks:
        avg = sum(f['rating'] for f in feedbacks)/len(feedbacks)
        st.markdown(f"""<div style="text-align:center; border:2px solid #FFD700; border-radius:15px; padding:10px; background:{box_bg};">
            <p style="color:#0A1931; font-weight:900; margin:0;">⭐ {avg:.1f} / 5.0 | {len(feedbacks)} Reviews</p></div>""", unsafe_allow_html=True)
    st.divider()
    name_input=st.text_input("Enter FULL name:", placeholder="e.g. Abasifreke Udoh")
    if name_input:
        board=load_board()
        if any(x.get("Name","").lower()==name_input.lower() for x in board):
            st.error("⚠️ This name has already played."); st.stop()
        st.session_state.name=name_input.strip()
    if st.session_state.name:
        st.success(f"Hello **{st.session_state.name}**! Are you ready?")
        st.markdown("""
        <div class='instruction-box'>
        <p style='text-align:center; font-size:22px!important;'>📜 INSTRUCTIONS (READ CAREFULLY)</p>
        <p>🔹 <b>MARKING SCHEME: Each question = 1 POINT. Total = 25 POINTS</b></p>
        <p>🔹 <b>FORMULA: PERCENTAGE = (Your Score / 25) x 100</b></p>
        <p>🔹 <b>Example: If you score 23, it means (23 / 25) x 100 = 92% </b></p>
        <p>🔹 Attempt all 25 questions.</p>
        <p>🔹 Use all the available letters to form the correct word.</p>
        <p>🔹 Confirm all your spellings before submitting to avoid being marked bad.<p>
        <p>🔹 If your answers are auto-submitted, 3 marks will be deducted from your score.<p>
        <p>🔹 The use of hint button will cost you 2 marks for every usage.<p>
        <p>🔹 This game requires logical and critical thinking. </p>
        <p>🔹 The game is based on religious items, activities and beings.</p>
        <p>🔹 To prevent malpractice, each participant's scrambled word is shuffled accordingly.</p>
        <p>🔹 You have 13 minutes only.</p>
        <p>🔹 Highest Score + Fastest Time WINS!</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 START QUIZ", use_container_width=True):
            with st.spinner("🎮 Game Loading... Please wait, getting your questions ready..."):
                get_audio_bytes()
                random.seed(time.time() + datetime.now().microsecond + hash(st.session_state.name) + random.randint(1, 1000000))
                temp = random.sample(WORDS, 25)
                random.shuffle(temp)
                st.session_state.quiz=[(w, scramble(w)) for w in temp]
                random.seed()
                st.session_state.started=True
                st.session_state.play_music=True
                st.session_state.submitted=False
                st.session_state.star_rating=0
                st.session_state.current_q=0
                st.session_state.hint_used={}
                st.session_state.hint_count=0
                st.session_state.auto_triggered=False
                st.session_state.show_grid=False
                st.session_state.answers={}
                time.sleep(0.5)
                st.session_state.start_time=time.time()
            st.success("Ready! Starting game...")
            time.sleep(0.5)
            st.rerun()
    st.stop()

name=st.session_state.name
quiz=st.session_state.quiz

if len(quiz)==0:
    st.error("Quiz error, restarting...")
    st.session_state.started=False
    st.rerun()

if st.session_state.get("submitted", False):
    score = st.session_state.result_score
    raw_score = st.session_state.result_raw_score
    total = st.session_state.result_total
    percent = st.session_state.result_percent
    raw_percent = st.session_state.result_raw_percent
    remark = st.session_state.result_remark
    review = st.session_state.result_review
    new_board_sorted = st.session_state.result_board
    elapsed = st.session_state.result_elapsed
    hint_count = st.session_state.result_hint_count
    auto_triggered = st.session_state.result_auto_triggered

    st.markdown(f"""<div style="text-align:center; padding:25px; background: linear-gradient(135deg, #0A1931, #1a2f5a); border:3px solid #FFD700; border-radius:20px;">
        <h2 style="color:#FFD700!important;">Well-done {name}. You scored {score}!</h2></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class='instruction-box'>
    <p>👤 {name}</p><p>📝 Initial Score: {raw_score}/{total} ({raw_percent}%)</p>
    <p>💡 Hint: {hint_count} x 2 = -{hint_count*2}</p>
    <p>⏰ Auto Penalty: -{3 if auto_triggered else 0}</p>
    <p>✅ Final Score: {score}/{total}</p><p>📊 Final %: {percent}%</p><p>💬 {remark}</p>
    <p>⏱️ Time: {int(elapsed//60)}m {int(elapsed%60)}s</p></div>""", unsafe_allow_html=True)

    share_text = f"✝️ CHURCH WORD SCRAMBLE - TED 2026\nI, {name}, scored {score}/{total} ({percent}%)!\n{remark}\nTime: {int(elapsed//60)}m {int(elapsed%60)}s\nCan you beat me?"
    encoded = urllib.parse.quote(share_text)
    wa_link = f"https://wa.me/?text={encoded}"
    st.link_button("📤 Share My Score to WhatsApp", wa_link, use_container_width=True)

    st.divider()
    st.subheader("⭐ Rate This Game")
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        if st.button("⭐" if st.session_state.star_rating>=1 else "☆", key="s1"): st.session_state.star_rating=1
    with c2:
        if st.button("⭐" if st.session_state.star_rating>=2 else "☆", key="s2"): st.session_state.star_rating=2
    with c3:
        if st.button("⭐" if st.session_state.star_rating>=3 else "☆", key="s3"): st.session_state.star_rating=3
    with c4:
        if st.button("⭐" if st.session_state.star_rating>=4 else "☆", key="s4"): st.session_state.star_rating=4
    with c5:
        if st.button("⭐" if st.session_state.star_rating>=5 else "☆", key="s5"): st.session_state.star_rating=5
    if st.session_state.star_rating>0:
        st.write(f"You selected: {'⭐'*st.session_state.star_rating}")
    fb_text = st.text_area("💬 Feedback:", key="feedback_input")
    if st.button("Submit Rating and Feedback", use_container_width=True):
        if st.session_state.star_rating==0:
            st.warning("Select star first.")
        else:
            fb = load_feedback()
            fb.append({"Name":name,"rating":st.session_state.star_rating,"feedback":fb_text,"date":datetime.now().strftime("%Y-%m-%d %H:%M")})
            save_feedback(fb)
        st.success(f"We have taken note of your feedback, {name}! Thank you.")
    st.divider(); st.subheader("📋 Your Review"); st.dataframe(review,use_container_width=True)
    st.subheader("🏆 Leaderboard"); st.dataframe(new_board_sorted,use_container_width=True)
    if st.button("🔄 Close & Play Again", type="primary", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
    st.stop()

@st.fragment(run_every=1)
def show_timer_and_auto_submit():
    elapsed_inner = time.time() - st.session_state.start_time
    remaining_inner = int(780 - elapsed_inner)
    if remaining_inner < 0: remaining_inner = 0

    if remaining_inner == 0 and not st.session_state.submitted:
        st.session_state.auto_triggered = True
        st.session_state.force_auto = True
        st.rerun()

    pct_width = (remaining_inner/780*100) if remaining_inner>0 else 0
    color = "#22c55e" if pct_width>50 else "#eab308" if pct_width>20 else "#ef4444"
    mins = remaining_inner//60
    secs = remaining_inner%60
    st.markdown(f"""<div style="margin:10px 0;"><div style="height:18px; border-radius:10px; background:#222; width:100%; border:1px solid #FFD700;">
    <div style="height:18px; border-radius:10px; background:{color}; width:{pct_width}%;"></div></div>
    <p style="text-align:center; color:{color}; font-weight:900;">⏳ {mins:02d}:{secs:02d}</p></div>""", unsafe_allow_html=True)

def do_submit(is_auto=False):
    score=0; review=[]
    for i in range(len(quiz)):
        try:
            q_item = quiz[i]
            if isinstance(q_item, (list, tuple)) and len(q_item) >= 1:
                corr = q_item[0]
                scr = q_item[1] if len(q_item) > 1 else ""
            elif isinstance(q_item, dict):
                corr = q_item.get("answer") or q_item.get("word") or ""
                scr = q_item.get("scrambled") or ""
            else:
                corr = str(q_item)
                scr = ""
        except Exception:
            corr = ""
            scr = ""

        ans = st.session_state.answers.get(i, st.session_state.get(f"a_{i}","")).strip()
        if ans.lower()==corr.lower(): score+=1
        review.append({"No":i+1,"Scrambled":scr,"Yours":ans or "-","Correct":corr,"Result":"✅" if ans.lower()==corr.lower() else "❌"})
    total=len(quiz)
    raw_score=score
    raw_percent=round(raw_score/total*100,1) if total>0 else 0
    hint_count = st.session_state.get("hint_count",0)
    final_score = raw_score - (hint_count*2) - (3 if is_auto else 0)
    if final_score<0: final_score=0
    percent=round(final_score/total*100,1) if total>0 else 0
    remark=get_remark(final_score,total)
    elapsed = time.time() - st.session_state.start_time
    new_board=load_board()
    new_board.append({"Name":name,"Score":final_score,"Total":f"{final_score}/{total}","Percent":percent,"Time":f"{int(elapsed//60)}m {int(elapsed%60)}s","Remark":remark,"Hints":hint_count,"Auto":is_auto})
    new_board_sorted=sorted(new_board,key=lambda x:x.get("Score",0),reverse=True)
    for r,p in enumerate(new_board_sorted,start=1):
        p["Rank"]=get_rank_display(r); p["Medal"]=get_medal(r)
    save_board(new_board_sorted)
    new_ans=load_answers()
    new_ans.append({"Name":name,"Score":f"{final_score}/{total}","Raw":f"{raw_score}/{total}","Hints":hint_count,"Auto":is_auto})
    save_answers(new_ans)
    st.session_state.submitted=True
    st.session_state.result_raw_score=raw_score
    st.session_state.result_raw_percent=raw_percent
    st.session_state.result_score=final_score
    st.session_state.result_total=total
    st.session_state.result_percent=percent
    st.session_state.result_remark=remark
    st.session_state.result_review=review
    st.session_state.result_board=new_board_sorted
    st.session_state.result_elapsed=elapsed
    st.session_state.result_hint_count=hint_count
    st.session_state.result_auto_triggered=is_auto
    st.rerun()

if st.session_state.get("force_auto", False):
    st.session_state.force_auto = False
    st.session_state.auto_triggered=True
    do_submit(is_auto=True)
    st.stop()

if st.session_state.get("play_music", False):
    audio_bytes = get_audio_bytes()
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", loop=True)

cur = st.session_state.get("current_q", 0)
try: cur = int(cur)
except: cur = 0
if cur < 0: cur = 0
if cur >= len(quiz): cur = len(quiz)-1
st.session_state.current_q = cur

try:
    q_item = quiz[cur]
    if isinstance(q_item, (list, tuple)) and len(q_item) >= 1:
        correct = q_item[0]
        scrambled = q_item[1] if len(q_item) > 1 else ""
    elif isinstance(q_item, dict):
        correct = q_item.get("answer") or q_item.get("word") or ""
        scrambled = q_item.get("scrambled") or ""
    else:
        correct = str(q_item)
        scrambled = ""
except Exception as e:
    correct = ""
    scrambled = ""
    st.error(f"Question {cur+1} has issue, skipping. {e}")

temp_count = len([v for v in st.session_state.answers.values() if v.strip()!=""])
if st.session_state.get(f"a_{cur}","").strip()!="" and cur not in st.session_state.answers:
    temp_count += 1
if st.session_state.get(f"a_{cur}","").strip()=="" and cur in st.session_state.answers and st.session_state.answers[cur].strip()=="":
    temp_count = max(0, temp_count-1)

st.write(f"📊 {temp_count}/{len(quiz)} answered | 💡 Hints used: {st.session_state.hint_count} | -{st.session_state.hint_count*2} marks")
st.progress(temp_count/len(quiz) if len(quiz)>0 else 0)

show_timer_and_auto_submit()

st.markdown(f"""<div style="background:{box_bg}; border:2px solid #FFD700; border-radius:15px; padding:20px; text-align:center;">
<p style="color:#0A1931; font-weight:900;">QUESTION {cur+1} OF {len(quiz)}</p>
<h1 style="color:#0A1931!important; font-size:42px; letter-spacing:5px;">{scrambled}</h1>
<p style="color:#555; font-size:12px;">Unscramble this word</p></div>""", unsafe_allow_html=True)

if st.session_state.hint_used.get(cur, False):
    st.warning(f"💡 HINT for Q{cur+1}: First = **{correct[0].upper() if correct else '?'}**, Last = **{correct[-1].upper() if correct else '?'}**, Length = **{len(correct)}** letters | -2 marks")
else:
    st.caption("Stuck? Click Hint button below -2 marks")

default_val = st.session_state.answers.get(cur, st.session_state.get(f"a_{cur}", ""))
st.text_input("Answer", value=default_val, key=f"a_{cur}", placeholder="Type your answer and press Next", label_visibility="collapsed")

col1,col2,col3,col4 = st.columns(4)
with col1:
    if st.button("⬅️ Previous", disabled=(cur==0), use_container_width=True):
        v = st.session_state.get(f"a_{cur}","").strip()
        if v: st.session_state.answers[cur]=v
        st.session_state.current_q = max(0, cur-1)
        st.rerun()
with col2:
    if st.button("💡 Hint (-2)", use_container_width=True):
        if not st.session_state.hint_used.get(cur, False):
            st.session_state.hint_used[cur]=True
            st.session_state.hint_count+=1
            st.rerun()
        else:
            st.toast("Hint already used!")
with col3:
    if st.button("Next ➡️", disabled=(cur==len(quiz)-1), use_container_width=True):
        v = st.session_state.get(f"a_{cur}","").strip()
        if v: st.session_state.answers[cur]=v
        elif cur in st.session_state.answers and v=="":
            del st.session_state.answers[cur]
        st.session_state.current_q = min(len(quiz)-1, cur+1)
        st.rerun()
with col4:
    if st.button("📋 Grid", use_container_width=True):
        st.session_state.show_grid = not st.session_state.get("show_grid", False)
        st.rerun()

if st.session_state.get("show_grid", False):
    st.write("---")
    st.write("**Tap to jump - ✅ = answered:**")
    cols = st.columns(5)
    for i in range(len(quiz)):
        c = cols[i % 5]
        is_ans = (i in st.session_state.answers and st.session_state.answers[i].strip()!="") or (i==cur and st.session_state.get(f"a_{i}","").strip()!="")
        label = f"{'✅' if is_ans else '⬜'} {i+1}"
        if c.button(label, key=f"j_{i}", use_container_width=True):
            v = st.session_state.get(f"a_{cur}","").strip()
            if v: st.session_state.answers[cur]=v
            st.session_state.current_q=i
            st.rerun()

st.divider()
if st.button("🚀 SUBMIT MY SCORE", use_container_width=True, type="primary"):
    v = st.session_state.get(f"a_{cur}","").strip()
    if v: st.session_state.answers[cur]=v
    do_submit(is_auto=False)

st.markdown("<div class='footer'>TED INNOVATIONS - BRINGING DREAMS TO REALITY</div>", unsafe_allow_html=True)
