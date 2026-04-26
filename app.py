import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION DE LA PAGE (Doit être la première commande) ---
st.set_page_config(page_title="Fisc-Analyst Pro", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

# --- DESIGN MODERNE (CSS INJECTÉ) ---
st.markdown("""
    <style>
    /* Importation d'une police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #F8FAFC; /* Gris très clair et moderne */
    }
    
    /* Titres principaux */
    h1, h2, h3 {
        color: #0F172A;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Design des blocs de chiffres (Métriques) */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }
    
    /* Animation au survol de la souris */
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: #4F46E5; /* Bordure Indigo au survol */
    }

    /* Personnalisation de la Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Boutons modernes */
    .stButton>button {
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #4338CA;
        transform: scale(1.02);
    }
    
    /* Header du rapport */
    .report-header { 
        color: #4F46E5; 
        font-weight: 800; 
        border-bottom: 3px solid #4F46E5; 
        padding-bottom: 10px; 
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SYSTÈME DE SÉCURITÉ ---
def check_password():
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "Burkina2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h1 style='text-align: center; color: #4F46E5;'>Fisc-Analyst Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748B;'>Veuillez vous identifier pour accéder à votre espace de travail.</p>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            st.text_input("Identifiant", key="username")
            st.text_input("Mot de passe", type="password", key="password")
            st.button("Connexion Sécurisée", on_click=password_entered, use_container_width=True)
        return False
    elif not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Identifiant", key="username")
            st.text_input("Mot de passe", type="password", key="password")
            st.button("Connexion Sécurisée", on_click=password_entered, use_container_width=True)
            st.error("😕 Identifiant ou mot de passe incorrect.")
        return False
    else:
        return True

# --- SI LA CONNEXION EST RÉUSSIE ---
if check_password():

    # --- MOTEUR DE CALCUL FINANCIER ---
    class FinancialEngine:
        def __init__(self, df):
            self.data = dict(zip(df['Compte'].astype(str), df['Solde']))
            self.df = df
        
        def get_val(self, prefixes):
            if isinstance(prefixes, str): prefixes = [prefixes]
            return sum(v for k, v in self.data.items() if any(k.startswith(p) for p in prefixes))

        def calculate_all(self):
            cp = self.get_val(['10', '11', '12', '13']) 
            dfin = self.get_val('16') 
            immo_brutes = self.get_val('2')
            
            ressources_stables = cp + dfin
            emplois_stables = immo_brutes
            frng = ressources_stables - emplois_stables
            
            actif_circulant = self.get_val(['3', '41', '42', '43', '44', '46'])
            passif_circulant = self.get_val(['40', '42', '43', '44', '46']) 
            bfr = actif_circulant - passif_circulant
            
            treso_nette = frng - bfr
            
            ca = self.get_val('70')
            achats = self.get_val('60')
            services_ext = self.get_val(['61', '62', '63'])
            va = ca - achats - services_ext
            ebe = va - self.get_val('66') 
            rex = ebe - self.get_val('68') 
            rn = self.get_val('13')

            return {
                "CP": cp, "DF": dfin, "CA": ca, "RN": rn, "VA": va, "EBE": ebe, "REX": rex,
                "FRNG": frng, "BFR": bfr, "Treso_Nette": treso_nette,
                "Autonomie": cp / (cp + dfin) if (cp + dfin) != 0 else 0,
                "Liquidite": actif_circulant / passif_circulant if passif_circulant != 0 else 0,
                "DSO": (self.get_val('41') / (ca * 1.18) * 360) if ca != 0 else 0,
                "DPO": (self.get_val('40') / (achats * 1.18) * 360) if achats != 0 else 0,
                "ROE": (rn / cp * 100) if cp != 0 else 0,
                "Marge_Nette": (rn / ca * 100) if ca != 0 else 0
            }

    # --- INTERFACE PRINCIPALE ---
    st.sidebar.markdown("<h2 style='color: #4F46E5; text-align: center;'>💎 Fisc-Analyst</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Menu de Navigation", [
        "📥 1. Espace Importation", 
        "📊 2. Dashboard Directeur", 
        "⚖️ 3. Équilibre & BFR",
        "📈 4. Benchmarking N/N-1",
        "🌍 5. Retraitements IFRS",
        "📄 6. Édition du Rapport"
    ])
    
    st.sidebar.markdown("<br><hr>", unsafe_allow_html=True)
    if st.sidebar.button("🔴 Déconnexion sécurisée", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()

    if 'df_n' not in st.session_state: st.session_state.df_n = None
    if 'df_n1' not in st.session_state: st.session_state.df_n1 = None

    # Configuration des graphiques (Thème Plotly moderne)
    chart_config = {'displayModeBar': False} # Cache la barre d'outils plotly
    plotly_template = "plotly_white"
    color_primary = "#4F46E5"
    color_secondary = "#10B981"
    color_danger = "#EF4444"

    # --- MODULES ---
    if menu == "📥 1. Espace Importation":
        st.title("Hub d'Importation Financière")
        st.markdown("Déposez vos balances générales exportées depuis votre ERP ou logiciel comptable.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            f_n = st.file_uploader("📁 Balance Exercice N (Format Excel)", type=['xlsx'], key="file_n")
            if f_n: st.session_state.df_n = pd.read_excel(f_n)
        with col2:
            f_n1 = st.file_uploader("📁 Balance Exercice N-1 (Optionnel)", type=['xlsx'], key="file_n1")
            if f_n1: st.session_state.df_n1 = pd.read_excel(f_n1)

        if st.session_state.df_n is not None:
            st.success("✅ Base de données N synchronisée et prête pour l'analyse globale.")

    elif menu == "📊 2. Dashboard Directeur":
        if st.session_state.df_n is not None:
            res = FinancialEngine(st.session_state.df_n).calculate_all()
            
            st.title("Cockpit de Performance")
            st.markdown("Vue d'ensemble des indicateurs critiques de l'entreprise.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Chiffre d'Affaires", f"{res['CA']:,.0f} FCFA")
            c2.metric("Marge Nette", f"{res['Marge_Nette']:.1f} %")
            c3.metric("Délai Client (DSO)", f"{int(res['DSO'])} Jours")
            c4.metric("Délai Fournisseur", f"{int(res['DPO'])} Jours")

            st.markdown("<br><br>", unsafe_allow_html=True)
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("#### Formation du Résultat (SIG)")
                sig_df = pd.DataFrame({
                    "Indicateur": ["Chiffre d'Affaires", "Valeur Ajoutée", "EBE", "Résultat Net"],
                    "Valeur": [res['CA'], res['VA'], res['EBE'], res['RN']]
                })
                fig_sig = px.funnel(sig_df, x='Valeur', y='Indicateur')
                fig_sig.update_traces(marker=dict(color=color_primary))
                fig_sig.update_layout(template=plotly_template, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_sig, use_container_width=True, config=chart_config)

            with col_chart2:
                st.markdown("#### Profil de Risque & Solvabilité")
                fig_radar = go.Figure(go.Scatterpolar(
                    r=[res['Autonomie']*10, min(res['Liquidite']*5, 10), min(res['ROE']/2, 10), 10-(res['DSO']/20)],
                    theta=['Solvabilité','Liquidité','Rentabilité (ROE)','Efficacité Clients'],
                    fill='toself', marker_color=color_secondary, line_color=color_secondary
                ))
                fig_radar.update_layout(template=plotly_template, polar=dict(radialaxis=dict(visible=True, range=[0, 10])), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=40, r=40, t=30, b=30))
                st.plotly_chart(fig_radar, use_container_width=True, config=chart_config)
        else:
            st.info("ℹ️ L'espace Dashboard nécessite l'importation de la balance N.")

    elif menu == "⚖️ 3. Équilibre & BFR":
        if st.session_state.df_n is not None:
            res = FinancialEngine(st.session_state.df_n).calculate_all()
            
            st.title("Structure & Équilibre Financier")
            st.markdown("Analyse de la capacité de l'entreprise à financer son cycle d'exploitation.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Fonds de Roulement (FRNG)", f"{res['FRNG']:,.0f} FCFA")
            c2.metric("Besoin en Fonds de Roulement", f"{res['BFR']:,.0f} FCFA")
            c3.metric("Trésorerie Nette", f"{res['Treso_Nette']:,.0f} FCFA")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            fig_waterfall = go.Figure(go.Waterfall(
                name = "Équilibre", orientation = "v",
                measure = ["relative", "relative", "total"],
                x = ["FRNG (Ressources Stables)", "BFR (Besoin Exploitation)", "Trésorerie Nette (Résultante)"],
                textposition = "outside",
                y = [res['FRNG'], -res['BFR'], res['Treso_Nette']],
                connector = {"line":{"color":"#94A3B8"}},
                decreasing = {"marker":{"color":color_danger}},
                increasing = {"marker":{"color":color_secondary}},
                totals = {"marker":{"color":color_primary}}
            ))
            fig_waterfall.update_layout(template=plotly_template, title="Cascade de l'Équilibre Financier", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_waterfall, use_container_width=True, config=chart_config)

    elif menu == "📈 4. Benchmarking N/N-1":
        if st.session_state.df_n is not None and st.session_state.df_n1 is not None:
            res_n = FinancialEngine(st.session_state.df_n).calculate_all()
            res_n1 = FinancialEngine(st.session_state.df_n1).calculate_all()
            
            st.title("Benchmarking Temporel")
            st.markdown("Comparaison des performances entre les deux exercices.")
            
            df_comp = pd.DataFrame({
                "Indicateur": ["Chiffre d'Affaires", "EBE", "Résultat Net", "BFR", "Trésorerie"],
                "Année N-1": [res_n1['CA'], res_n1['EBE'], res_n1['RN'], res_n1['BFR'], res_n1['Treso_Nette']],
                "Année N": [res_n['CA'], res_n['EBE'], res_n['RN'], res_n['BFR'], res_n['Treso_Nette']]
            })
            
            df_comp['Variation (%)'] = ((df_comp['Année N'] / df_comp['Année N-1']) - 1) * 100
            
            fig_bar = px.bar(df_comp, x='Indicateur', y=['Année N-1', 'Année N'], barmode='group', color_discrete_sequence=["#94A3B8", color_primary])
            fig_bar.update_layout(template=plotly_template, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True, config=chart_config)
        else:
            st.info("ℹ️ Importez les bilans N et N-1 dans l'Espace Importation pour activer ce module.")

    elif menu == "🌍 5. Retraitements IFRS":
        st.title("Moteur de Transposition IFRS")
        st.markdown("Simulation des impacts bilanciels selon les normes internationales.")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Norme IFRS 16 (Contrats de Location)")
            loyer = st.number_input("Montant des loyers annuels (FCFA)", min_value=0, value=0)
            duree = st.slider("Durée moyenne restante (Années)", 1, 20, 5)
        
        with col2:
            st.markdown("#### Impact au Bilan")
            if loyer > 0:
                droit_utilisation = loyer * duree
                st.success(f"📈 Actif : Création d'un Droit d'Utilisation de {droit_utilisation:,.0f} FCFA")
                st.error(f"📉 Passif : Constatation d'une Dette Locative de {droit_utilisation:,.0f} FCFA")
                st.info("💡 Résultat : Amélioration mécanique de l'EBE (Remplacement de la charge externe par une dotation).")
            else:
                st.write("Saisissez un loyer pour simuler l'impact.")

    elif menu == "📄 6. Édition du Rapport":
        if st.session_state.df_n is not None:
            res = FinancialEngine(st.session_state.df_n).calculate_all()
            
            with st.container():
                st.markdown('<div class="report-header">RAPPORT D\'EXPERTISE FINANCIÈRE INTELLIGENT</div>', unsafe_allow_html=True)
                st.markdown(f"<p style='color: #64748B;'>Édité le {datetime.now().strftime('%d/%m/%Y')} par Fisc-Analyst Pro</p>", unsafe_allow_html=True)
                
                st.markdown("### 1. Diagnostic de Solvabilité")
                if res['Autonomie'] > 0.5:
                    st.success("✅ La structure financière est robuste. L'entreprise est indépendante vis-à-vis de ses créanciers.")
                else:
                    st.error("⚠️ Risque identifié : Forte dépendance aux financements externes. Capitaux propres insuffisants.")
                    
                st.markdown("### 2. Équilibre du Cycle d'Exploitation")
                if res['FRNG'] > res['BFR']:
                    st.success(f"✅ Le Fonds de Roulement couvre intégralement le BFR. La trésorerie d'exploitation est positive et saine.")
                else:
                    st.error(f"❌ Déséquilibre : L'entreprise doit recourir à des concours bancaires de court terme pour financer son exploitation.")

                st.markdown("### 3. Efficacité de Recouvrement")
                st.info(f"📊 Le délai moyen de recouvrement client s'établit à **{int(res['DSO'])} jours**. Le délai de règlement fournisseur est de **{int(res['DPO'])} jours**.")
                
                if res['DSO'] > res['DPO']:
                    st.warning("⚠️ L'entreprise paie ses fournisseurs plus rapidement qu'elle n'encaisse ses clients. Ce ciseau dégrade la trésorerie immédiate.")
                
                st.markdown("<br><hr>", unsafe_allow_html=True)
                st.button("🖨️ Exporter en PDF (Mode Impression Navigateur)", use_container_width=True)
