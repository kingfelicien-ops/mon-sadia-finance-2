import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION DE SÉCURITÉ ---
def check_password():
    """Retourne True si l'utilisateur a saisi le bon mot de passe."""
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "Burkina2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # On ne garde pas le mot de passe en mémoire
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Affichage du formulaire de connexion
        st.title("🔐 Accès Sécurisé - Fisc-Analyst Pro")
        st.text_input("Identifiant", key="username")
        st.text_input("Mot de passe", type="password", key="password")
        st.button("Se connecter", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Mauvais mot de passe
        st.title("🔐 Accès Sécurisé - Fisc-Analyst Pro")
        st.text_input("Identifiant", key="username")
        st.text_input("Mot de passe", type="password", key="password")
        st.button("Se connecter", on_click=password_entered)
        st.error("😕 Identifiant ou mot de passe incorrect.")
        return False
    else:
        return True

# --- SI LA CONNEXION EST RÉUSSIE, ON LANCE LE LOGICIEL ---
if check_password():

    # Configuration de la page
    st.set_page_config(page_title="Fisc-Analyst Pro", layout="wide")

    # --- STYLE ---
    st.markdown("""
        <style>
        .main { background-color: #f4f6f9; }
        .stMetric { border: 1px solid #e0e6ed; padding: 15px; border-radius: 10px; background: white; }
        </style>
        """, unsafe_allow_html=True)

    # --- MOTEUR DE CALCUL ---
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
            ca = self.get_val('70')
            achats = self.get_val('60')
            rn = self.get_val('13')
            # Ratios simples pour le test
            return {
                "CA": ca, "RN": rn,
                "Autonomie": cp / (cp + dfin) if (cp + dfin) != 0 else 0,
                "Marge": (rn / ca * 100) if ca != 0 else 0
            }

    # --- INTERFACE ---
    st.sidebar.title("📈 Fisc-Analyst Pro")
    if st.sidebar.button("Se déconnecter"):
        st.session_state["password_correct"] = False
        st.rerun()

    menu = st.sidebar.radio("Navigation", ["📥 Importation", "📊 Tableau de Bord", "📄 Rapport"])

    if menu == "📥 Importation":
        st.header("Importation des données")
        file = st.file_uploader("Choisir une balance Excel", type=['xlsx'])
        if file:
            st.session_state['data'] = pd.read_excel(file)
            st.success("Fichier chargé avec succès !")

    elif menu == "📊 Tableau de Bord":
        if 'data' in st.session_state:
            res = FinancialEngine(st.session_state['data']).calculate_all()
            st.header("Analyse en direct")
            c1, c2 = st.columns(2)
            c1.metric("Chiffre d'Affaires", f"{res['CA']:,.0f} FCFA")
            c2.metric("Marge Nette", f"{res['Marge']:.1f} %")
        else:
            st.warning("Veuillez importer un fichier d'abord.")

    elif menu == "📄 Rapport":
        st.write("Le module de rapport est prêt.")
