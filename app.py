
import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime

st.set_page_config(page_title="CreatorOS Pro", page_icon="🎬", layout="wide")

HISTORY_FILE = "creator_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            import json as js
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return js.load(f)
        except: return []
    return []

def save_history(h):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1 { font-weight: 800; letter-spacing: -0.03em; }
.stButton>button { border-radius: 12px; font-weight: 700; padding: 0.7rem 1.4rem; }
</style>""", unsafe_allow_html=True)

st.title("🎬 CreatorOS Pro — War Edition")
st.caption("V8.6 AUTO • Auto-Model • Never 404 • Permanent History • Universal Niche")

ALL_LANGUAGES = ['English','Hindi','Hinglish (Hindi + English Mix)','Bengali','Tamil','Telugu','Marathi','Gujarati','Bhojpuri','Kannada','Malayalam','Punjabi','Urdu','Odia','Assamese','Spanish','French','German','Portuguese','Russian','Japanese','Korean','Chinese (Mandarin)','Arabic','Italian','Dutch','Turkish','Polish','Vietnamese','Thai','Indonesian']
NICHES = ["Any Topic (Auto-Detect)","Money & Finance","Business & Startup","Motivation & Self-Help","Education & Explainers","Tech & AI","Health & Fitness","Relationship & Lifestyle","Gaming","Comedy & Roast","Documentary & Biography","News & Commentary","Spirituality","Food & Cooking","Travel & Vlog"]

if 'mem_history' not in st.session_state:
    st.session_state['mem_history'] = load_history()

with st.sidebar:
    st.markdown("### 🎬 CreatorOS Pro V8.6 AUTO")
    api_key = st.text_input("🔑 Gemini API Key:", type="password", placeholder="Paste key here...")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
            if api_key: st.success("Using key from secrets")
        except: pass
    if api_key:
        genai.configure(api_key=api_key)
    st.divider()
    selected_niche = st.selectbox("Niche:", NICHES, index=0)
    st.divider()
    st.markdown("#### 📜 History")
    if not st.session_state['mem_history']:
        st.caption("No history yet")
    else:
        for idx, item in enumerate(reversed(st.session_state['mem_history'][-10:])):
            real_idx = len(st.session_state['mem_history'])-1-idx
            if st.button(f"{item['topic'][:20]}...", key=f"h_{real_idx}", use_container_width=True):
                st.session_state['mem_titles_list']=item['titles_list']
                st.session_state['mem_script']=item['script']
                st.session_state['mem_topic']=item['topic']
                st.session_state['mem_lang']=item['lang']
                st.rerun()

# V8.6 AUTO-MODEL: Lists models from API and auto-picks working one — never 404 again
def gemini_json(prompt):
    # Step 1: Try to get list of available models dynamically
    available_models = []
    try:
        for m in genai.list_models():
            # Only models that support generateContent
            if 'generateContent' in m.supported_generation_methods:
                # Extract short name like "gemini-2.0-flash"
                name = m.name.replace("models/", "")
                available_models.append(name)
    except:
        pass

    # Preferred order — newest first
    preferred = ["gemini-2.0-flash", "gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-flash-001", "gemini-1.5-flash-latest", "gemini-1.5-pro", "gemini-pro"]

    # Build final try list: available models that match preferred, plus fallback to preferred
    models_to_try = []
    for p in preferred:
        if p in available_models:
            models_to_try.append(p)
    # If list_models failed or empty, use preferred directly
    if not models_to_try:
        models_to_try = preferred
    else:
        # Also add any other available gemini models not in preferred list
        for am in available_models:
            if am not in models_to_try and "gemini" in am:
                models_to_try.append(am)

    last_err = None
    for mname in models_to_try:
        try:
            model = genai.GenerativeModel(mname, system_instruction="You output ONLY valid JSON. No markdown, no explanation.")
            resp = model.generate_content(prompt, generation_config={"temperature": 0.8, "max_output_tokens": 3000})
            txt = resp.text.strip()
            if "```" in txt:
                parts = txt.split("```")
                for part in parts:
                    if "{" in part:
                        txt = part
                        if txt.strip().startswith("json"): txt = txt.strip()[4:]
                        break
            result = json.loads(txt)
            # Show which model worked (in sidebar logs)
            print(f"✅ Working model: {mname}")
            return result
        except Exception as e:
            last_err = e
            # If 404, try next model automatically
            if "404" in str(e) or "not found" in str(e).lower():
                continue
            # For other errors, also try next but keep error
            continue
    raise Exception(f"All models failed. Last error: {last_err}. Available models found: {available_models}")

for k in ['mem_titles_list','mem_script','mem_topic','mem_lang','mem_seo']:
    if k not in st.session_state:
        st.session_state[k]=[] if k=='mem_titles_list' else ""

tab1, tab2 = st.tabs(["🎬 IDEATION", "🖼️ SEO"])

with tab1:
    topic_input = st.text_input("Topic:", placeholder="e.g. how to make chicken biryani at home", value=st.session_state['mem_topic'])
    c1,c2,c3 = st.columns(3)
    with c1:
        vt = st.radio("Format:", ["Long Form","Short Form"], horizontal=True)
        duration = st.select_slider("Duration:", ["5 min","10 min","20 min"] if vt=="Long Form" else ["15 sec","30 sec","60 sec"], value="10 min" if vt=="Long Form" else "60 sec")
    with c2:
        tone = st.selectbox("Tone:", ["Motivational","Energetic & Casual","Calm & Storytelling","Funny / Roast","Documentary Style","Educational","Cinematic"])
    with c3:
        language = st.selectbox("Language:", ALL_LANGUAGES)
    niche_prompt = selected_niche if selected_niche!="Any Topic (Auto-Detect)" else "auto-detect"
    if st.button("✨ Generate with Gemini", type="primary", use_container_width=True):
        if not api_key: st.error("Add Gemini API key in sidebar")
        elif not topic_input.strip(): st.warning("Enter topic")
        else:
            with st.spinner("Generating..."):
                try:
                    wm = {"15 sec":"40","30 sec":"80","60 sec":"130","5 min":"700","10 min":"1400","20 min":"2800"}
                    wt = wm.get(duration,"1400")
                    dt = gemini_json(f"Topic:{topic_input} Niche:{niche_prompt} Lang:{language} Return ONLY JSON like {{\"titles\":[\"t1\"]}} Generate 10 viral titles in {language}")
                    titles = dt.get("titles",[])
                    ds = gemini_json(f"Topic:{topic_input} Niche:{niche_prompt} Length:{duration} ({wt} words) Tone:{tone} Lang:{language} Return ONLY JSON like {{\"script\":\"text\"}} Write {wt} words voiceover script in {language} with Hook, Main, Outro.")
                    script = ds.get("script","")
                    st.session_state['mem_titles_list']=titles
                    st.session_state['mem_script']=script
                    st.session_state['mem_topic']=topic_input
                    st.session_state['mem_lang']=language
                    st.session_state['mem_history'].append({"topic":topic_input,"lang":language,"titles_list":titles,"script":script,"timestamp":datetime.now().strftime("%d %b %H:%M")})
                    save_history(st.session_state['mem_history'])
                    st.success("Done!")
                except Exception as e:
                    st.error(f"Error: {e}")
    if st.session_state['mem_titles_list']:
        for i,t in enumerate(st.session_state['mem_titles_list']):
            st.write(f"**{i+1}.** {t}")
        st.markdown(st.session_state['mem_script'])

with tab2:
    st.info("Generate Ideation first, then SEO here")
    if st.session_state['mem_topic'] and st.button("Generate SEO"):
        try:
            d = gemini_json(f"Topic:{st.session_state['mem_topic']} Return ONLY JSON like {{\"description\":\"desc\",\"tags\":[\"t\"]}} Generate SEO")
            st.write(d)
        except Exception as e:
            st.error(f"{e}")

st.caption("V8.6 AUTO — Auto-detects best model • Biryani test 🍛 • Never 404")
