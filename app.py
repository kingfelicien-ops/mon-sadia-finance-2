import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ET THEME ---
st.set_page_config(page_title="Fisc-Analyst Pro | Finance & IFRS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stMetric { border: 1px solid #e0e6ed; padding: 15px; border-radius: 10px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .report-header { color: #1a73e8; font-weight: bold; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- MOTEUR DE CALCUL FINANCIER ---

class FinancialEngine:
    def __init__(self, df):
        # Convertir les comptes en chaînes de caractères pour éviter les erreurs
        self.data = dict(zip(df['Compte'].astype(str), df['Solde']))
        self.df = df
    
    def get_val(self, prefixes):
        if isinstance(prefixes, str): prefixes = [prefixes]
        return sum(v for k, v in self.data.items() if any(k.startswith(p) for p in prefixes))

    def calculate_all(self):
        # 1. Masses Bilancielles
        cp = self.get_val(['10', '11', '12', '13']) # Capitaux propres + Résultat
        dfin = self.get_val('16') # Dettes financières
        immo_brutes = self.get_val('2')
        
        # FRNG, BFR et Trésorerie
        ressources_stables = cp + dfin
        emplois_stables = immo_brutes
        frng = ressources_stables - emplois_stables
        
        actif_circulant = self.get_val(['3', '41', '42', '43', '44', '46'])
        passif_circulant = self.get_val(['40', '42', '43', '44', '46']) # Passif hors trésorerie
        bfr = actif_circulant - passif_circulant
        
        treso_nette = frng - bfr
        
        # 2. Compte de Résultat
        ca = self.get_val('70')
        achats = self.get_val('60')
        services_ext = self.get_val(['61', '62', '63'])
        va = ca - achats - services_ext
        ebe = va - self.get_val('66') # Charges de personnel
        rex = ebe - self.get_val('68') # Dotations
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
st.sidebar.title("📈 Fisc-Analyst Pro")
st.sidebar.caption("Analyse Financière & Stratégique")

menu = st.sidebar.radio("Navigation", [
    "📥 1. Importation & Audit", 
    "📊 2. Tableau de Bord", 
    "⚖️ 3. Équilibre & BFR",
    "📈 4. Comparaison N/N-1",
    "🌍 5. Transposition IFRS",
    "📄 6. Rapport d'Expert"
])

# Variables de session
if 'df_n' not in st.session_state: st.session_state.df_n = None
if 'df_n1' not in st.session_state: st.session_state.df_n1 = None

# --- MODULE 1 : IMPORTATION ---
if menu == "📥 1. Importation & Audit":
    st.title("Importation des États Financiers")
    st.write("Importez vos balances au format Excel. Le logiciel reconnaîtra les comptes SYSCOHADA automatiquement.")
    
    col1, col2 = st.columns(2)
    with col1:
        f_n = st.file_uploader("Importer Balance N (Obligatoire)", type=['xlsx'], key="file_n")
        if f_n: st.session_state.df_n = pd.read_excel(f_n)
    with col2:
        f_n1 = st.file_uploader("Importer Balance N-1 (Pour comparaison)", type=['xlsx'], key="file_n1")
        if f_n1: st.session_state.df_n1 = pd.read_excel(f_n1)

    if st.session_state.df_n is not None:
        st.success("✅ Données de l'année N prêtes pour l'analyse.")
        
        with st.expander("Voir les données brutes (Top 5 lignes)"):
            st.dataframe(st.session_state.df_n.head())

# --- MODULE 2 : TABLEAU DE BORD ---
elif menu == "📊 2. Tableau de Bord":
    if st.session_state.df_n is not None:
        eng = FinancialEngine(st.session_state.df_n)
        res = eng.calculate_all()
        
        st.header("Cockpit de Performance Financière")
        
        # Métriques principales
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Chiffre d'Affaires", f"{res['CA']:,.0f} FCFA")
        c2.metric("Marge Nette", f"{res['Marge_Nette']:.1f} %")
        c3.metric("Délai Client (DSO)", f"{int(res['DSO'])} jrs")
        c4.metric("Délai Fournisseur (DPO)", f"{int(res['DPO'])} jrs")

        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Formation du Résultat (SIG)")
            sig_df = pd.DataFrame({
                "Indicateur": ["Chiffre d'Affaires", "Valeur Ajoutée", "EBE", "Résultat Net"],
                "Valeur": [res['CA'], res['VA'], res['EBE'], res['RN']]
            })
            fig_sig = px.funnel(sig_df, x='Valeur', y='Indicateur', color_discrete_sequence=['#1a73e8'])
            st.plotly_chart(fig_sig, use_container_width=True)

        with col_chart2:
            st.subheader("Profil de Risque (Radar)")
            fig_radar = go.Figure(go.Scatterpolar(
                r=[res['Autonomie']*10, min(res['Liquidite']*5, 10), min(res['ROE']/2, 10), 10-(res['DSO']/20)],
                theta=['Solvabilité','Liquidité','Rentabilité (ROE)','Efficacité Recouvrement'],
                fill='toself', marker_color='#ff5722'
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])))
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.warning("Veuillez importer les données dans le module 1.")

# --- MODULE 3 : ÉQUILIBRE ET BFR ---
elif menu == "⚖️ 3. Équilibre & BFR":
    if st.session_state.df_n is not None:
        res = FinancialEngine(st.session_state.df_n).calculate_all()
        
        st.header("Analyse de la Structure Financière")
        st.write("La règle d'or financière : FRNG - BFR = Trésorerie Nette")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Fonds de Roulement (FRNG)", f"{res['FRNG']:,.0f} FCFA")
        c2.metric("Besoin en Fonds de Roulement (BFR)", f"{res['BFR']:,.0f} FCFA")
        c3.metric("Trésorerie Nette", f"{res['Treso_Nette']:,.0f} FCFA")
        
        # Graphique Waterfall pour l'équilibre
        fig_waterfall = go.Figure(go.Waterfall(
            name = "Équilibre", orientation = "v",
            measure = ["relative", "relative", "total"],
            x = ["FRNG", "BFR (Dédouit)", "Trésorerie Nette"],
            textposition = "outside",
            y = [res['FRNG'], -res['BFR'], res['Treso_Nette']],
            connector = {"line":{"color":"rgb(63, 63, 63)"}}
        ))
        fig_waterfall.update_layout(title="Passage du FRNG à la Trésorerie")
        st.plotly_chart(fig_waterfall)

# --- MODULE 4 : COMPARAISON ---
elif menu == "📈 4. Comparaison N/N-1":
    if st.session_state.df_n is not None and st.session_state.df_n1 is not None:
        res_n = FinancialEngine(st.session_state.df_n).calculate_all()
        res_n1 = FinancialEngine(st.session_state.df_n1).calculate_all()
        
        st.header("Benchmarking Temporel (N vs N-1)")
        
        df_comp = pd.DataFrame({
            "Indicateur": ["Chiffre d'Affaires", "EBE", "Résultat Net", "BFR", "Trésorerie"],
            "Année N-1": [res_n1['CA'], res_n1['EBE'], res_n1['RN'], res_n1['BFR'], res_n1['Treso_Nette']],
            "Année N": [res_n['CA'], res_n['EBE'], res_n['RN'], res_n['BFR'], res_n['Treso_Nette']]
        })
        
        df_comp['Variation (%)'] = ((df_comp['Année N'] / df_comp['Année N-1']) - 1) * 100
        
        st.dataframe(df_comp.style.format({
            'Année N-1': '{:,.0f}', 'Année N': '{:,.0f}', 'Variation (%)': '{:+.2f}%'
        }))
        
        fig_bar = px.bar(df_comp, x='Indicateur', y=['Année N-1', 'Année N'], barmode='group', title="Évolution des masses clés")
        st.plotly_chart(fig_bar)
    else:
        st.warning("Importez les bilans N et N-1 dans le module 1 pour activer la comparaison.")

# --- MODULE 5 : IFRS ---
elif menu == "🌍 5. Transposition IFRS":
    st.header("Simulateur de Retraitements IFRS")
    st.write("Ce module permet de simuler l'impact des normes internationales sur votre bilan OHADA.")
    
    st.subheader("IFRS 16 : Contrats de location")
    loyer = st.number_input("Saisissez le montant des loyers annuels (Crédit-bail / Loc. simple)", min_value=0, value=0)
    duree = st.slider("Durée moyenne restante des contrats (en années)", 1, 20, 5)
    
    if loyer > 0:
        droit_utilisation = loyer * duree
        st.info(f"**Impact Bilan :** Création d'un actif (Droit d'utilisation) et d'un passif (Dette locative) de **{droit_utilisation:,.0f} FCFA**.")
        st.success("**Impact Compte de Résultat :** Annulation des charges de loyer, remplacées par des dotations aux amortissements et des charges financières.")

# --- MODULE 6 : RAPPORT ---
elif menu == "📄 6. Rapport d'Expert":
    if st.session_state.df_n is not None:
        res = FinancialEngine(st.session_state.df_n).calculate_all()
        
        st.markdown('<div class="report-header"><h2>RAPPORT D\'ANALYSE FINANCIÈRE</h2></div>', unsafe_allow_html=True)
        st.write(f"**Date d'édition :** {datetime.now().strftime('%d/%m/%Y')}")
        
        st.write("### 1. Structure et Solvabilité")
        if res['Autonomie'] > 0.5:
            st.write("✅ L'entreprise démontre une excellente indépendance financière. Les capitaux propres couvrent largement l'endettement externe.")
        else:
            st.write("⚠️ L'indépendance financière est faible. L'entreprise dépend fortement de ses créanciers pour financer son activité.")
            
        st.write("### 2. Équilibre Financier (FRNG / BFR)")
        if res['FRNG'] > res['BFR']:
            st.write(f"✅ Le Fonds de Roulement ({res['FRNG']:,.0f} FCFA) est suffisant pour financer le Besoin en Fonds de Roulement ({res['BFR']:,.0f} FCFA). La trésorerie est donc structurellement excédentaire.")
        else:
            st.write(f"❌ Le Fonds de Roulement est insuffisant pour couvrir le BFR. L'entreprise consomme de la trésorerie pour son cycle d'exploitation.")

        st.write("### 3. Performance et Rentabilité")
        st.write(f"L'entreprise génère une Valeur Ajoutée de {res['VA']:,.0f} FCFA et termine l'exercice avec une marge nette de {res['Marge_Nette']:.1f}%.")

        st.write("### 4. Cycle de Gestion")
        st.write(f"Les clients paient en moyenne à **{int(res['DSO'])} jours**, tandis que les fournisseurs sont payés à **{int(res['DPO'])} jours**.")
        if res['DSO'] > res['DPO']:
            st.write("⚠️ **Vigilance :** L'entreprise paie ses fournisseurs plus vite qu'elle n'est payée par ses clients, ce qui dégrade sa trésorerie.")

        st.markdown("---")
        st.button("🖨️ Sauvegarder le Rapport (Ctrl + P / Cmd + P)")
