import streamlit as st
from groq import Groq
import os
import pandas as pd
from pypdf import PdfReader

# ─── CONFIG ───────────────────────────────────────────────
st.set_page_config(page_title="DevAssist", page_icon="🖥️", layout="wide")

# ─── CSS GLOBAL ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
body { background-color: #f4f6f9; }
.hero { background: linear-gradient(135deg, #1e3a5f, #2d5986); padding: 50px 40px; border-radius: 12px; color: white; margin-bottom: 30px; }
.hero h1 { font-size: 32px; font-weight: 700; margin-bottom: 8px; }
.hero p { font-size: 15px; opacity: 0.8; }
.card { background: white; border-radius: 10px; padding: 22px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 20px; border-top: 3px solid #2d5986; }
.card h3 { color: #1e3a5f; font-size: 15px; margin-bottom: 8px; }
.card p { color: #666; font-size: 13px; line-height: 1.6; }
.stat-card { background: white; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.06); border-bottom: 3px solid #2d5986; }
.stat-number { font-size: 32px; font-weight: 700; color: #1e3a5f; }
.stat-label { font-size: 12px; color: #888; margin-top: 4px; }
.login-box { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
.login-hero { background: linear-gradient(135deg, #1e3a5f, #2d5986); padding: 40px 35px; color: white; }
.login-hero h2 { font-size: 26px; font-weight: 700; margin-bottom: 8px; }
.login-hero p { font-size: 14px; opacity: 0.8; }
.login-body { background: #f8fafc; padding: 35px; }
.login-body h4 { color: #1e3a5f; font-size: 15px; margin-bottom: 20px; }
.stButton > button { background: linear-gradient(135deg, #1e3a5f, #2d5986) !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 10px 28px !important; font-weight: 500 !important; font-size: 14px !important; }
.stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
.navbar-logo { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #1e3a5f; }
</style>
""", unsafe_allow_html=True)

# ─── FONCTIONS DONNÉES ────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["GROQ_API_KEY"]
    except:
        with open(".env") as f:
            for line in f:
                if line.startswith("GROQ_API_KEY"):
                    return line.split("=")[1].strip()

@st.cache_data
def lire_pdfs():
    texte = ""
    dossier = "docs"
    if os.path.exists(dossier):
        for fichier in os.listdir(dossier):
            if fichier.endswith(".pdf"):
                try:
                    reader = PdfReader(os.path.join(dossier, fichier))
                    for page in reader.pages:
                        texte += page.extract_text() or ""
                except:
                    pass
    return texte

def lire_excel():
    tickets = []
    dossier = "docs"
    if os.path.exists(dossier):
        for fichier in os.listdir(dossier):
            if fichier.endswith(".xlsx") or fichier.endswith(".xls"):
                try:
                    df = pd.read_excel(os.path.join(dossier, fichier))
                    for _, row in df.iterrows():
                        ticket = f"Device: {row.get('Device','')} | Service: {row.get('Service','')} | Sujet: {row.get('Subject','')} | Solution: {row.get('TECHOPS','')} | Justification: {row.get('Case Justification L2','')}"
                        tickets.append(ticket)
                except:
                    pass
    return tickets

@st.cache_data
def lire_excel_df():
    dfs = []
    dossier = "docs"
    if os.path.exists(dossier):
        for fichier in os.listdir(dossier):
            if fichier.endswith(".xlsx") or fichier.endswith(".xls"):
                try:
                    df = pd.read_excel(os.path.join(dossier, fichier))
                    dfs.append(df)
                except:
                    pass
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return None

# ─── SESSION STATE ────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "contexte_pdf" not in st.session_state:
    st.session_state.contexte_pdf = ""
if "tickets_data" not in st.session_state:
    st.session_state.tickets_data = []

# ─── NAVBAR ───────────────────────────────────────────────
def show_navbar():
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
    with col1:
        st.markdown("""
        <div class="navbar-logo">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Alten_logo.svg/320px-Alten_logo.svg.png" height="28">
            <span>DevAssist</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🏠 Home"):
            st.session_state.page = "home"
            st.rerun()
    with col3:
        if st.button("🤖 AI Bot"):
            st.session_state.page = "aibot"
            st.rerun()
    with col4:
        if st.button("🎫 Tickets"):
            st.session_state.page = "tickets"
            st.rerun()
    with col5:
        if st.button("📱 Devices"):
            st.session_state.page = "devices"
            st.rerun()
    with col6:
        if st.button("🚪"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()
    st.markdown("---")

# ─── PAGE LOGIN ───────────────────────────────────────────
def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-box">
            <div class="login-hero">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Alten_logo.svg/320px-Alten_logo.svg.png" height="40" style="margin-bottom:15px"><br>
                <h2>Hello 👋</h2>
                <p>DevAssist — SN2-Platform</p>
            </div>
            <div class="login-body">
                <h4>Login to your account below ⬇️</h4>
            </div>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("📧 Email", placeholder="prenom.nom@alten.com")
        password = st.text_input("🔒 Password", type="password", placeholder="••••••••")

        if st.button("Login →", use_container_width=True):
            if email.endswith("@alten.com") and password == "ALTEN26":
                st.session_state.logged_in = True
                st.session_state.page = "home"
                st.session_state.contexte_pdf = lire_pdfs()
                st.session_state.tickets_data = lire_excel()
                st.rerun()
            else:
                st.error("❌ Email ou mot de passe incorrect")

# ─── PAGE HOME ────────────────────────────────────────────
def page_home():
    show_navbar()

    st.markdown("""
    <div class="hero">
        <h1>Welcome to DevAssist 🖥️</h1>
        <p>Smart support platform for multimedia devices — SN2 Team</p>
    </div>
    """, unsafe_allow_html=True)

    df = lire_excel_df()
    total = len(df) if df is not None else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total}</div><div class="stat-label">Total Tickets</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div class="stat-number">4</div><div class="stat-label">Devices supportés</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><div class="stat-number">L1/L3</div><div class="stat-label">Verdict automatique</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-card"><div class="stat-number">24/7</div><div class="stat-label">AI disponible</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## How does it work?")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card">
            <h3>🤖 AI-Powered Assistant</h3>
            <p>Décrivez un incident — le chatbot analyse et propose une solution basée sur les procédures internes et l'historique des tickets.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h3>⚡ Verdict L1 / L3</h3>
            <p>Le système décide automatiquement si l'incident peut être résolu en L1 ou nécessite une escalade L3 — sans réunion.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="card">
            <h3>📊 Tickets Dashboard</h3>
            <p>Consultez et filtrez tous les tickets historiques. Un graphique montre quels devices génèrent le plus d'incidents.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🤖 Ask AI Bot →"):
        st.session_state.page = "aibot"
        st.rerun()

# ─── PAGE AI BOT ──────────────────────────────────────────
def page_aibot():
    show_navbar()

    st.markdown("""
    <div class="hero">
        <h1>🤖 AI Bot</h1>
        <p>Ask your question — Get the right answer</p>
    </div>
    """, unsafe_allow_html=True)

    client = Groq(api_key=get_api_key())
    contexte_excel = "\n".join(st.session_state.tickets_data[:50])

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Décrivez votre problème technique...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        system_prompt = f"""Tu es un assistant support IT pour l'équipe SN2 (ALTEN).
Tu aides les consultants à résoudre des incidents techniques sur les devices multimedia.

Réponds EXACTEMENT dans ce format avec des sauts de ligne entre chaque section :

**Type de problème :**
[type du problème]

**Device concerné :**
[nom du device]

**Solution recommandée :**
[solution détaillée étape par étape]

**Verdict :**
[écrire uniquement L1 ou L3]

**Résumé escalade :**
[si L3 : résumé prêt à envoyer. Si L1 : Non applicable]

PROCÉDURES INTERNES :
{st.session_state.contexte_pdf[:2000]}

HISTORIQUE TICKETS :
{contexte_excel[:2000]}

Réponds toujours en français, de façon concise et professionnelle."""

        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.messages
                    ],
                    max_tokens=1000
                )
                reponse = response.choices[0].message.content
                st.write(reponse)

                if "Verdict :** L1" in reponse or "Verdict :\nL1" in reponse or "Verdict : L1" in reponse:
                    st.success("✅ ACTION : Envoyer la solution au L1")
                elif "Verdict :** L3" in reponse or "Verdict :\nL3" in reponse or "Verdict : L3" in reponse:
                    st.error("🔴 ACTION : Escalade vers L3 — Résumé préparé ci-dessus")

        st.session_state.messages.append({"role": "assistant", "content": reponse})

# ─── PAGE TICKETS ─────────────────────────────────────────
def page_tickets():
    show_navbar()

    st.markdown("""
    <div class="hero">
        <h1>🎫 Tickets Dashboard</h1>
        <p>Historique des incidents — Mois 3 & 4</p>
    </div>
    """, unsafe_allow_html=True)

    df_all = lire_excel_df()

    if df_all is not None and len(df_all) > 0:
        st.success(f"✅ {len(df_all)} tickets chargés")

        search = st.text_input("🔍 Rechercher un ticket (numéro, device, description...)", placeholder="Ex: OpenR Link, FOTA, 4-25350316...")

        col1, col2 = st.columns(2)
        with col1:
            devices = ["Tous"] + sorted(list(df_all["Device"].dropna().unique()))
            device_filter = st.selectbox("🖥️ Filtrer par Device", devices)
        with col2:
            services = ["Tous"] + sorted(list(df_all["Service"].dropna().unique()))
            service_filter = st.selectbox("🔧 Filtrer par Service", services)

        df_filtered = df_all.copy()
        if device_filter != "Tous":
            df_filtered = df_filtered[df_filtered["Device"] == device_filter]
        if service_filter != "Tous":
            df_filtered = df_filtered[df_filtered["Service"] == service_filter]

        if search:
            mask = df_filtered.apply(
                lambda row: row.astype(str).str.contains(search, case=False, na=False).any(),
                axis=1
            )
            df_filtered = df_filtered[mask]

        st.markdown(f"**{len(df_filtered)} tickets trouvés**")

        cols_show = ["Case Number", "Device", "Service", "Subject", "TECHOPS", "Case Justification L2"]
        cols_exist = [c for c in cols_show if c in df_filtered.columns]
        st.dataframe(df_filtered[cols_exist], use_container_width=True, height=400)

        st.markdown("### 📊 Incidents par Device")
        st.bar_chart(df_all["Device"].value_counts())

        st.markdown("### 📊 Top 10 Services")
        st.bar_chart(df_all["Service"].value_counts().head(10))

    else:
        st.warning("⚠️ Aucun fichier Excel trouvé dans docs/")

# ─── PAGE DEVICES ─────────────────────────────────────────
def page_devices():
    show_navbar()

    st.markdown("""
    <div class="hero">
        <h1>📱 Devices</h1>
        <p>Informations sur les devices multimedia supportés</p>
    </div>
    """, unsafe_allow_html=True)

    devices = [
        {"nom": "OpenR Link", "desc": "Système multimédia dernière génération. Grand écran tactile avec Google Maps, Google Assistant et Google Play. Disponible sur Mégane E-Tech, Scenic, Austral.", "icon": "🖥️"},
        {"nom": "EasyLink", "desc": "Plateforme infotainment avec écran 7-9.3 pouces. Supporte navigation, Apple CarPlay et Android Auto. Disponible sur Zoe, Captur, Clio.", "icon": "📱"},
        {"nom": "MediaNav Live", "desc": "Système de navigation connecté avec mises à jour cartographiques en ligne. Disponible sur Sandero, Duster, Logan.", "icon": "🗺️"},
        {"nom": "DUO / BENTO", "desc": "Application Mobilize pour gestion du véhicule électrique. Digital key, programmation de charge et suivi autonomie.", "icon": "🔑"},
    ]

    col1, col2 = st.columns(2)
    for i, device in enumerate(devices):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
            <div class="card">
                <h3>{device['icon']} {device['nom']}</h3>
                <p>{device['desc']}</p>
            </div>""", unsafe_allow_html=True)

# ─── ROUTER ───────────────────────────────────────────────
if not st.session_state.logged_in:
    page_login()
else:
    if st.session_state.page == "home":
        page_home()
    elif st.session_state.page == "aibot":
        page_aibot()
    elif st.session_state.page == "tickets":
        page_tickets()
    elif st.session_state.page == "devices":
        page_devices()
    else:
        page_home()