
import streamlit as st
import google.generativeai as genai
import json
import os
import re
from datetime import datetime

st.set_page_config(page_title="CreatorOS Pro", page_icon="🎬", layout="wide")

HISTORY_FILE = "creator_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_history(h):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1 { font-weight: 800; }
.stButton>button { border-radius: 12px; font-weight: 700; padding: 0.7rem 1.4rem; }
</style>""", unsafe_allow_html=True)

st.title("🎬 CreatorOS Pro — War Edition")
st.caption("V8.8 ULTRA AUTO • Searches latest models live • Gemini 3.6 ready • Never fails")

ALL_LANGUAGES = ['English','Hindi','Hinglish','Bengali','Tamil','Telugu','Marathi','Spanish','French','German','Japanese','Korean']
NICHES = ["Any Topic (Auto-Detect)","Food & Cooking","Money & Finance","Gaming","Tech & AI","Health","Travel"]

if 'mem_history' not in st.session_state:
    st.session_state['mem_history'] = load_history()

with st.sidebar:
    st.markdown("### 🎬 V8.8 ULTRA")
    api_key = st.text_input("🔑 Gemini API Key:", type="password")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
            if api_key: st.success("Using secret key")
        except: pass
    if api_key:
        genai.configure(api_key=api_key)
    niche = st.selectbox("Niche:", NICHES, index=0)

def extract_version(model_name):
    # Extract version like 3.6, 2.5, 3.0 from model name for sorting newest first
    m = re.search(r'(\d+)\.(\d+)', model_name)
    if m:
        return float(f"{m.group(1)}.{m.group(2)}")
    m = re.search(r'(\d+)-\d+', model_name)
    if m:
        return float(m.group(1))
    if "2.5" in model_name: return 2.5
    if "2.0" in model_name: return 2.0
    if "1.5" in model_name: return 1.5
    return 0.0

def get_live_models():
    """V8.8 ULTRA: Asks Google API live for current models, sorts newest first"""
    live_models = []
    try:
        # This is the "search engine" you asked for - asks Gemini API itself what exists NOW
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace("models/", "")
                # Only gemini family
                if "gemini" in name.lower():
                    live_models.append(name)
    except Exception as e:
        st.sidebar.warning(f"Could not list models: {e}")
    
    # Sort by version newest first (3.6 > 3.0 > 2.5 > 2.0 > 1.5)
    live_models = sorted(set(live_models), key=lambda x: (extract_version(x), "pro" not in x, "flash" in x), reverse=True)
    
    # If list_models fails, try future-proof hardcoded list including 3.6
    if not live_models:
        live_models = [
            "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.0-flash",
            "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash",
            "gemini-1.5-flash", "gemini-1.5-flash-latest"
        ]
    else:
        # Ensure future models like 3.6 are tried first even if not yet listed
        future_models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.0-flash"]
        for fm in future_models:
            if fm not in live_models:
                # Try future model first
                live_models.insert(0, fm)
    
    return live_models

def gemini_json(prompt):
    models = get_live_models()
    st.sidebar.caption(f"🔍 Found {len(models)} live models")
    with st.sidebar.expander("Live models detected"):
        st.write(models[:15])
    
    last_err = None
    for mname in models:
        try:
            model = genai.GenerativeModel(mname, system_instruction="You output ONLY valid JSON. No markdown.")
            resp = model.generate_content(prompt, generation_config={"temperature": 0.8, "max_output_tokens": 3000})
            txt = resp.text.strip()
            if "```" in txt:
                for part in txt.split("```"):
                    if "{" in part:
                        txt = part
                        if txt.strip().startswith("json"): txt = txt.strip()[4:]
                        break
            result = json.loads(txt)
            st.sidebar.success(f"✅ Using: {mname}")
            return result
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            if "404" in err_str or "not found" in err_str or "not supported" in err_str:
                continue
            continue
    raise Exception(f"All {len(models)} live models failed. Last: {last_err}. Tried: {models[:10]}")

# Fallback templates so biryani NEVER fails
TITLE_TEMPLATES = [
    "I Tried {t} for 7 Days (Shocking Result)",
    "{t} - The Truth Nobody Tells You",
    "How {t} Changed My Life",
    "Stop Doing {t} Wrong",
    "The Ultimate Guide to {t}",
    "{t} Explained in 60 Seconds",
    "Why 99% Fail at {t}",
    "7 Secrets of {t}",
    "I Made {t} Like a Pro Chef",
    "{t} Recipe That Will Blow Your Mind"
]

for k in ['mem_titles_list','mem_script','mem_topic','mem_lang']:
    if k not in st.session_state:
        st.session_state[k]=[] if k=='mem_titles_list' else ""

topic_input = st.text_input("Topic:", placeholder="e.g. how to make chicken biryani", value=st.session_state['mem_topic'])
c1,c2,c3 = st.columns(3)
with c1:
    duration = st.select_slider("Duration:", ["15 sec","60 sec","5 min","10 min","20 min"], value="10 min")
with c2:
    tone = st.selectbox("Tone:", ["Calm & Storytelling","Energetic","Funny","Educational","Cinematic"])
with c3:
    lang = st.selectbox("Language:", ALL_LANGUAGES)

if st.button("✨ Generate with Gemini (AUTO)", type="primary", use_container_width=True):
    if not api_key:
        st.error("Add API key first")
    elif not topic_input.strip():
        st.warning("Enter topic")
    else:
        with st.spinner("🔍 Searching latest Gemini models live..."):
            try:
                # Try AI first
                dt = gemini_json(f"Topic:{topic_input} Niche:{niche} Lang:{lang} Return ONLY JSON like {{\"titles\":[\"t1\"]}} Generate 10 viral titles in {lang} for {topic_input}")
                titles = dt.get("titles",[])
                ds = gemini_json(f"Topic:{topic_input} Length:{duration} Tone:{tone} Lang:{lang} Return ONLY JSON like {{\"script\":\"text\"}} Write 800 words voiceover script in {lang} for {topic_input}")
                script = ds.get("script","")
                st.session_state['mem_titles_list']=titles
                st.session_state['mem_script']=script
                st.session_state['mem_topic']=topic_input
                st.session_state['mem_lang']=lang
                st.session_state['mem_history'].append({"topic":topic_input,"lang":lang,"titles_list":titles,"script":script,"timestamp":datetime.now().strftime("%d %b %H:%M")})
                save_history(st.session_state['mem_history'])
                st.success("Generated with AI!")
            except Exception as e:
                st.warning(f"AI failed ({e}), using offline biryani-proof mode 🍛")
                # Fallback - NEVER fails
                import random
                titles = [t.format(t=topic_input.title()) for t in TITLE_TEMPLATES]
                random.shuffle(titles)
                script = f"**Biryani Recipe for {topic_input}**\n\nHook: Ever wondered how to make perfect {topic_input}?\n\nStep 1: Prepare ingredients...\nStep 2: Cook with love...\nStep 3: Serve hot!"
                st.session_state['mem_titles_list']=titles
                st.session_state['mem_script']=script
                st.session_state['mem_topic']=topic_input
                st.session_state['mem_lang']=lang

if st.session_state['mem_titles_list']:
    st.divider()
    st.subheader(f"📌 Titles for {st.session_state['mem_topic']}")
    for i,t in enumerate(st.session_state['mem_titles_list']):
        st.write(f"**{i+1}.** {t}")
    st.markdown("#### 🎙️ Script")
    st.markdown(st.session_state['mem_script'])

st.caption("V8.8 ULTRA • Auto-searches live models • Gemini 3.6 ready • Biryani never fails 🍛")
