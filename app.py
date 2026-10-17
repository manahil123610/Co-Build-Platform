"""Streamlit interface for the CoBuild teammate matcher."""

import streamlit as st

from explain import draft_intro, explain
from extract import extract_profile
from match import load_profiles, top_matches

st.set_page_config(page_title="CoBuild | Find your people", page_icon="🧩", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink: #202c2b; --moss: #315d4a; --leaf: #dcedc7; --coral: #d96f50; --paper: #f8f7f1; }
    .stApp { background: radial-gradient(ellipse at 90% 0%, #e7efe1 0, transparent 34%), var(--paper); color: var(--ink); }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--ink); }
    h1 { font-size: 2.6rem; letter-spacing: 0; }
    .eyebrow { color: var(--moss); text-transform: uppercase; font-weight: 700; font-size: .76rem; letter-spacing: .08em; }
    .match-card { background: rgba(255,255,255,.82); border: 1px solid #dce3d8; border-left: 4px solid var(--moss); padding: 1.15rem 1.3rem; margin: .7rem 0 1rem; border-radius: 6px; }
    .score { color: var(--moss); font-weight: 700; font-size: 1.2rem; }
    .stButton > button[kind="primary"] { background: var(--moss); border: 0; }
    .footnote { color: #64716c; font-size: .82rem; border-top: 1px solid #d9dfd4; padding-top: 1rem; margin-top: 2.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">Small teams, good chemistry</div>', unsafe_allow_html=True)
st.title("Find your build partner.")
st.write("Paste a teammate post. CoBuild will map the skills you bring and the ones you need.")
post = st.text_area("Teammate post", height=190, placeholder="We're building... I can help with... Looking for...")

if st.button("Find partners", type="primary", disabled=not post.strip()):
    with st.spinner("Reading your post..."):
        try:
            st.session_state["profile"] = extract_profile(post)
            st.session_state.pop("matching_error", None)
        except Exception:
            st.session_state["matching_error"] = "Could not analyze this post. Check your Gemini API key and connection, then try again."
            st.session_state.pop("profile", None)

if st.session_state.get("matching_error"):
    st.error(st.session_state["matching_error"])

if "profile" in st.session_state:
    original = st.session_state["profile"]
    st.subheader("Your profile")
    st.caption("Review or adjust the extracted details before matching.")
    with st.form("profile_form"):
        project = st.text_input("Project", value=original["project"])
        offers = st.text_input("Skills you offer (comma separated)", value=", ".join(original["offers"]))
        needs = st.text_input("Skills you need (comma separated)", value=", ".join(original["needs"]))
        col1, col2, col3 = st.columns(3)
        with col1:
            hours = st.number_input("Hours per week", min_value=0, max_value=168, value=original["hours_per_week"] or 0)
        with col2:
            timezone = st.text_input("Timezone", value=original["timezone"] or "")
        with col3:
            level = st.selectbox("Experience level", ["beginner", "intermediate", "advanced", "Not specified"], index=["beginner", "intermediate", "advanced", None].index(original["level"]))
        submitted = st.form_submit_button("Show matches", type="primary")

    if submitted:
        st.session_state["profile"] = {
            "project": project.strip(),
            "offers": [item.strip() for item in offers.split(",") if item.strip()],
            "needs": [item.strip() for item in needs.split(",") if item.strip()],
            "hours_per_week": int(hours) if hours else None,
            "timezone": timezone.strip() or None,
            "level": None if level == "Not specified" else level,
        }

    profile = st.session_state["profile"]
    matches = top_matches(profile, load_profiles())
    st.subheader("Your top matches")
    for rank, result in enumerate(matches, start=1):
        candidate = result["profile"]
        st.markdown('<div class="match-card">', unsafe_allow_html=True)
        st.markdown(f"**{rank}. {candidate['project']}** <span class='score'>{result['score']:.0%} fit</span>", unsafe_allow_html=True)
        st.write(explain(profile, candidate, result))
        st.caption("Skills connecting you: " + (", ".join(result["matched_skills"]) or "compare your needs and offers"))
        st.text_area("Draft intro", value=draft_intro(profile, candidate), key=f"intro_{candidate['id']}", height=120)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footnote">Demo uses synthetic profiles. Posts are not stored.</div>', unsafe_allow_html=True)
