
import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime
import io

st.set_page_config(page_title="CreatorOS Pro", page_icon="🎬", layout="wide")

# === PERSISTENT HISTORY FILE ===
HISTORY_FILE = "creator_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1 { font-weight: 800; letter-spacing: -0.03em; }
.stButton>button { border-radius: 12px; font-weight: 700; padding: 0.7rem 1.4rem; }
[data-testid="stMetricValue"] { font-weight: 800; }
.stTextInput>div>div>input, .stSelectbox>div>div { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 CreatorOS Pro — War Edition")
st.caption("V8.4 WAR • Permanent History • Deploy Ready • Universal Niche • Any topic")

ALL_LANGUAGES = ['English','Hindi','Hinglish (Hindi + English Mix)','Bengali','Tamil','Telugu','Marathi','Gujarati','Bhojpuri','Kannada','Malayalam','Punjabi','Urdu','Odia','Assamese','Spanish','French','German','Portuguese','Russian','Japanese','Korean','Chinese (Mandarin)','Arabic','Italian','Dutch','Turkish','Polish','Vietnamese','Thai','Indonesian','Malay','Filipino (Tagalog)','Swahili','Greek','Hebrew','Persian (Farsi)','Nepali','Sinhala','Burmese','English (US)','English (UK)']

NICHES = ["Any Topic (Auto-Detect)","Money & Finance","Business & Startup","Motivation & Self-Help","Education & Explainers","Tech & AI","Health & Fitness","Relationship & Lifestyle","Gaming","Comedy & Roast","Documentary & Biography","News & Commentary","Spirituality","Food & Cooking","Travel & Vlog"]

# Load persistent history into session if empty
if 'mem_history' not in st.session_state:
    st.session_state['mem_history'] = load_history()
else:
    if not st.session_state['mem_history']:
        st.session_state['mem_history'] = load_history()

with st.sidebar:
    st.markdown("### 🎬 CreatorOS Pro V8.4")
    st.caption("WAR EDITION — Permanent + Deploy")
    api_key = st.text_input("🔑 Gemini API Key:", type="password", placeholder="Paste key here...")
    # For Streamlit Cloud, also check secrets
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
            if api_key:
                st.success("Using key from secrets")
        except:
            pass
    if api_key:
        genai.configure(api_key=api_key)
    st.divider()
    st.markdown("#### ⚙️ Niche Mode")
    selected_niche = st.selectbox("Select niche:", NICHES, index=0, help="Works for ANY niche.")
    st.divider()
    st.markdown("#### 📜 Permanent History")
    if not st.session_state['mem_history']:
        st.caption("No history yet — will be saved to file")
    else:
        st.caption(f"{len(st.session_state['mem_history'])} videos saved permanently")
        for idx, item in enumerate(reversed(st.session_state['mem_history'][-15:])):
            real_idx = len(st.session_state['mem_history'])-1 - idx
            if st.button(f"{item['topic'][:20]}... ({item.get('lang','')})", key=f"hist_{real_idx}", use_container_width=True):
                st.session_state['mem_titles_list'] = item['titles_list']
                st.session_state['mem_titles'] = "\n".join([f"{i+1}. {t}" for i,t in enumerate(item['titles_list'])])
                st.session_state['mem_script'] = item['script']
                st.session_state['mem_topic'] = item['topic']
                st.session_state['mem_lang'] = item['lang']
                st.session_state['mem_seo'] = item.get('seo','')
                st.session_state['mem_edit'] = item.get('edit','')
                st.session_state['mem_thumb_prompt'] = item.get('thumb_prompt','')
                st.session_state['mem_stock_timeline'] = item.get('stock_timeline',[])
                st.session_state['mem_stock_pack'] = item.get('stock_pack',{})
                st.session_state['mem_duration'] = item.get('duration','10 min')
                st.session_state['mem_niche'] = item.get('niche','Any')
                st.rerun()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clear File", use_container_width=True):
            st.session_state['mem_history']=[]
            save_history([])
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            st.rerun()
    with col_b:
        if st.button("Backup JSON", use_container_width=True):
            st.download_button("Download history.json", json.dumps(st.session_state['mem_history'], ensure_ascii=False, indent=2), file_name="creator_history.json", mime="application/json", use_container_width=True)
    st.divider()
    st.markdown("**Deploy Guide:**")
    st.caption("1. Upload to GitHub\n2. share.streamlit.io → Deploy\n3. Add GEMINI_API_KEY in Secrets")

def gemini_json(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction="You output ONLY valid JSON. No explanation, no markdown outside JSON.")
        resp = model.generate_content(prompt, generation_config={"temperature": 0.8, "max_output_tokens": 3000})
        txt = resp.text.strip()
        if "```" in txt:
            parts = txt.split("```")
            for part in parts:
                if "{" in part:
                    txt = part
                    if txt.strip().startswith("json"): txt = txt.strip()[4:]
                    break
        return json.loads(txt)
    except Exception as e:
        try:
            model = genai.GenerativeModel("gemini-pro", system_instruction="You output ONLY valid JSON.")
            resp = model.generate_content(prompt)
            txt = resp.text.strip()
            if "```" in txt:
                parts = txt.split("```")
                for part in parts:
                    if "{" in part:
                        txt = part
                        if txt.strip().startswith("json"): txt = txt.strip()[4:]
                        break
            return json.loads(txt)
        except Exception as e2:
            raise e2

for k in ['mem_titles','mem_script','mem_topic','mem_lang','mem_seo','mem_edit','mem_titles_list','mem_thumb_prompt','mem_stock_timeline','mem_stock_pack','mem_duration','mem_niche']:
    if k not in st.session_state: 
        if k in ['mem_titles_list','mem_stock_timeline']: st.session_state[k]=[]
        elif k=='mem_stock_pack': st.session_state[k]={}
        else: st.session_state[k]=""

tab1, tab2, tab3, tab4 = st.tabs(["🎬 IDEATION", "🖼️ SEO + THUMBNAIL", "✂️ EDIT LAB", "🚀 DEPLOY"])

with tab1:
    st.markdown("#### Works for ANY niche — biryani test = passed 🍛")
    topic_input = st.text_input("Topic:", placeholder="e.g. what is the history of biryani", value=st.session_state['mem_topic'], label_visibility="collapsed")
    c1,c2,c3 = st.columns(3)
    with c1:
        video_type = st.radio("Format:", ["Long Form", "Short Form"], horizontal=True, key="vt_v8")
        if video_type=="Long Form":
            duration = st.select_slider("Duration:", options=["5 min","8 min","10 min","12 min","15 min","20 min","30 min","45 min","60 min"], value="10 min", key="dur_long")
        else:
            duration = st.select_slider("Duration:", options=["15 sec","30 sec","45 sec","60 sec","90 sec"], value="60 sec", key="dur_short")
    with c2:
        tone = st.selectbox("Tone:", ["Motivational","Energetic & Casual","Calm & Storytelling","Funny / Roast","Documentary Style","Educational","Controversial / Bold","Cinematic"], key="tone_v8")
    with c3:
        language = st.selectbox(f"Language ({len(ALL_LANGUAGES)}):", ALL_LANGUAGES, key="lang_v8")

    niche_prompt = selected_niche if selected_niche!="Any Topic (Auto-Detect)" else "auto-detect niche from topic"
    if st.button("✨ Generate with Gemini", type="primary", use_container_width=True):
        if not api_key:
            st.error("Paste Gemini API Key in sidebar first — or add in Streamlit Secrets as GEMINI_API_KEY")
        elif not topic_input.strip():
            st.warning("Drop a topic first")
        else:
            with st.spinner(f"Generating {duration} — Niche: {niche_prompt} — {language}..."):
                try:
                    word_map = {"15 sec": "40", "30 sec": "80", "45 sec": "110", "60 sec": "130", "90 sec": "200", "5 min": "700", "8 min": "1100", "10 min": "1400", "12 min": "1700", "15 min": "2100", "20 min": "2800", "30 min": "4200", "45 min": "6300", "60 min": "8400"}
                    word_target = word_map.get(duration, "1400")
                    title_prompt = "Topic: " + topic_input + " Niche: " + niche_prompt + " Language: " + language + " Return ONLY JSON like {\"titles\": [\"t1\",\"t2\",\"t3\",\"t4\",\"t5\",\"t6\",\"t7\",\"t8\",\"t9\",\"t10\"]} Generate 10 viral high-CTR YouTube titles under 60 chars in " + language + ". Adapt to niche."
                    data_titles = gemini_json(title_prompt)
                    titles_list = data_titles.get("titles", [])
                    script_prompt = "Topic: " + topic_input + " Niche: " + niche_prompt + " Length: " + duration + " (" + word_target + " words) Tone: " + tone + " Language: " + language + " Return ONLY JSON like {\"script\": \"full voiceover\"} Write full voiceover with [0:00] timestamps in " + language + ", " + word_target + " words, adapt to niche " + niche_prompt + ". Include Hook, Main, Outro."
                    data_script = gemini_json(script_prompt)
                    script_text = data_script.get("script", "")
                    st.session_state['mem_titles_list']=titles_list
                    st.session_state['mem_titles']="\n".join([f"{i+1}. {t}" for i,t in enumerate(titles_list)])
                    st.session_state['mem_script']=script_text
                    st.session_state['mem_topic']=topic_input
                    st.session_state['mem_lang']=language
                    st.session_state['mem_duration']=duration
                    st.session_state['mem_niche']=niche_prompt
                    new_item = {
                        "topic": topic_input,
                        "lang": language,
                        "titles_list": titles_list,
                        "script": script_text,
                        "duration": duration,
                        "tone": tone,
                        "niche": niche_prompt,
                        "timestamp": datetime.now().strftime("%d %b %H:%M %Y"),
                        "seo": "",
                        "edit": "",
                        "thumb_prompt": "",
                        "stock_pack": {},
                        "stock_timeline": []
                    }
                    st.session_state['mem_history'].append(new_item)
                    save_history(st.session_state['mem_history'])
                    st.success(f"Generated + Saved permanently! Total: {len(st.session_state['mem_history'])}")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state['mem_titles_list']:
        st.divider()
        st.subheader(f"📌 10 Titles — {st.session_state['mem_topic'][:50]}")
        st.caption(f"Niche: {st.session_state.get('mem_niche','Any')} • Lang: {st.session_state['mem_lang']} • {st.session_state.get('mem_duration','')}")
        for i, t in enumerate(st.session_state['mem_titles_list']):
            with st.container(border=True):
                st.write(f"**{i+1}.** {t}")
        st.divider()
        wc = len(st.session_state['mem_script'].split())
        c1,c2 = st.columns(2)
        c1.metric("Words", wc)
        c2.metric("Read Time", f"{round(wc/150,1)} min")
        st.markdown("#### 🎙️ Voiceover Script")
        st.markdown(st.session_state['mem_script'])
        st.download_button("⬇️ Download Script", st.session_state['mem_script'], file_name="voiceover.txt", use_container_width=True)

with tab2:
    st.header("🖼️ Thumbnail + SEO")
    if not st.session_state['mem_topic']:
        st.info("Generate Ideation first")
    else:
        st.info(f"Locked — {st.session_state['mem_topic']} | {st.session_state.get('mem_niche','Any')} | {st.session_state['mem_lang']}")
        if st.button("Generate SEO Pack ✨", use_container_width=True):
            with st.spinner("Generating SEO..."):
                try:
                    seo_prompt = "Topic: " + st.session_state["mem_topic"] + " Niche: " + st.session_state.get("mem_niche","Any") + " Language: " + st.session_state["mem_lang"] + " Return ONLY JSON like {\"thumbnails\": [\"t1\",\"t2\"], \"design\": \"bg\", \"description\": \"desc\", \"tags\": [\"tag\"], \"hashtags\": [\"#tag\"], \"image_prompt\": \"prompt\"} Generate 5 thumbnail texts, design notes, SEO description, tags, hashtags, Midjourney prompt adapted to niche."
                    data = gemini_json(seo_prompt)
                    seo_text = "**Thumbnail Texts:**\n" + "\n".join([f"- {t}" for t in data.get("thumbnails",[])]) + f"\n\n**Design:** {data.get('design','')}\n\n**Description:** {data.get('description','')}\n\n**Tags:** {', '.join(data.get('tags',[]))}\n\n**Hashtags:** {', '.join(data.get('hashtags',[]))}"
                    st.session_state['mem_seo']=seo_text
                    st.session_state['mem_thumb_prompt']=data.get('image_prompt','')
                    if st.session_state['mem_history']:
                        st.session_state['mem_history'][-1]['seo']=seo_text
                        st.session_state['mem_history'][-1]['thumb_prompt']=data.get('image_prompt','')
                        save_history(st.session_state['mem_history'])
                except Exception as e:
                    st.error(f"{e}")
        if st.session_state['mem_seo']:
            st.divider()
            st.markdown(st.session_state['mem_seo'])
            if st.session_state['mem_thumb_prompt']:
                st.code(st.session_state['mem_thumb_prompt'])

with tab3:
    st.header("✂️ Edit Lab + Stock Pack")
    if not st.session_state['mem_topic']:
        st.info("Generate Ideation first")
    else:
        st.info(f"Topic: {st.session_state['mem_topic']} | Niche: {st.session_state.get('mem_niche','Any')}")
        if st.button("Generate Edit Plan + Stock Terms ✂️", type="primary", use_container_width=True):
            with st.spinner("Creating edit plan..."):
                try:
                    edit_prompt = "Topic: " + st.session_state["mem_topic"] + " Niche: " + st.session_state.get("mem_niche","Any") + " Language: " + st.session_state["mem_lang"] + " Duration: " + st.session_state.get("mem_duration","10 min") + " Return ONLY JSON like {\"timeline\": [{\"time\": \"0:00-0:30\", \"visual\": \"scene\", \"text\": \"on screen\", \"sfx\": \"music\", \"stock_search\": \"keywords\", \"stock_type\": \"video\"}], \"stock_pack\": {\"pexels_keywords\": [\"kw\"], \"story_blocks\": [\"kw\"], \"broll_ideas\": [\"kw\"]}} 6-8 segments, adapt to niche."
                    data = gemini_json(edit_prompt)
                    txt = ""
                    stock_list = []
                    for seg in data.get("timeline",[]):
                        txt += f"**{seg.get('time','')}** | Visual: {seg.get('visual','')} | Stock: {seg.get('stock_search','')} ({seg.get('stock_type','video')})\n\n"
                        stock_list.append({"time": seg.get('time',''), "search": seg.get('stock_search',''), "type": seg.get('stock_type','video'), "visual": seg.get('visual','')})
                    st.session_state['mem_edit']=txt
                    st.session_state['mem_stock_timeline']=stock_list
                    st.session_state['mem_stock_pack']=data.get("stock_pack", {})
                    if st.session_state['mem_history']:
                        st.session_state['mem_history'][-1]['edit']=txt
                        st.session_state['mem_history'][-1]['stock_pack']=data.get("stock_pack", {})
                        st.session_state['mem_history'][-1]['stock_timeline']=stock_list
                        save_history(st.session_state['mem_history'])
                except Exception as e:
                    st.error(f"{e}")
        if st.session_state.get('mem_stock_timeline'):
            st.divider()
            for item in st.session_state['mem_stock_timeline']:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2,3,3])
                    with col1: st.markdown(f"**{item['time']}**"); st.caption(item['visual'][:80])
                    with col2: st.code(item['search'])
                    with col3:
                        q = item['search'].replace(" ", "+")
                        st.markdown(f"[Pexels](https://www.pexels.com/search/videos/{q}/) | [Pixabay](https://pixabay.com/videos/search/{q}/)")
        if st.session_state['mem_edit']:
            st.divider()
            st.markdown(st.session_state['mem_edit'])

with tab4:
    st.header("🚀 Deploy Online — Fix 'site cant be reached'")
    st.markdown("""
    **Your app is now deploy-ready! Follow these 3 steps:**
    #### Step 1: GitHub
    1. Go to github.com → New Repository → `creatoros-pro`
    2. Upload `app.py` + `requirements.txt`
    
    #### Step 2: Streamlit Cloud
    1. Go to share.streamlit.io → Login with GitHub
    2. Click New App → Select repo `creatoros-pro` → File `app.py` → Deploy
    3. Wait 2 min → you get link like `https://creatoros-pro.streamlit.app`
    
    #### Step 3: Add API Key Securely
    In Streamlit Cloud dashboard → App Settings → Secrets → Paste:
    ```
    GEMINI_API_KEY = "your_key_here"
    ```
    Save + Reboot app. No more pasting key daily!
    
    #### Permanent History Fixed!
    Now history saves to `creator_history.json` file, not just RAM. Even if you refresh, biryani doc stays!
    On Streamlit Cloud, history resets on reboot, but you can download backup from sidebar.
    
    #### Why site cant be reached happened before?
    - You used local run `py -m streamlit run app.py` → only works on your laptop
    - Now deploying to cloud → works worldwide 24/7
    """)
    if st.button("Download requirements.txt for Deploy"):
        st.code("streamlit\ngoogle-generativeai>=0.8.0\nreportlab", language=None)

st.divider()
st.caption("CreatorOS Pro V8.4 WAR — Permanent History + Deploy Ready • Biryani test passed 🍛")
