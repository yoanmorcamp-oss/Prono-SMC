import base64
from datetime import datetime
import io
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pronos SMC - Saison 2026-2027", page_icon="?", layout="wide"
)

MOT_DE_PASSE_ADMIN = "yoan"

# CHANGEMENT DE NOM DES FICHIERS POUR ÉVITER LES VIEUX CACHES CORROMPUS
MATCHS_FILE = "matchs_v2.csv"
PRONOS_FILE = "pronos_v2.csv"
BONUS_FILE = "bonus_v2.csv"

PARTICIPANTS_INITIAUX = ["Nathéo", "Adri", "Allan", "Jo", "Vincent", "Tony", "Yoan"]
EFFECTIF_SMC = [
    "Anthony Mandréa",
    "Yannis Clémentia",
    "Parfait Mandanda",
    "Dennis Appiah",
    "Salim Diakité",
    "Mohamed Hafid",
    "Ivann Botella",
    "Armand Gnanduillet",
    "Fahd El Khoumisti",
]


def safe_read_csv(filepath, default_columns):
  if not os.path.exists(filepath):
    return pd.DataFrame(columns=default_columns)
  try:
    with open(filepath, "rb") as f:
      content_bytes = f.read()
    content_str = content_bytes.decode("utf-8", errors="ignore")
    df = pd.read_csv(io.StringIO(content_str))
  except Exception:
    df = pd.DataFrame(columns=default_columns)

  for col in default_columns:
    if col not in df.columns:
      df[col] = ""
  return df


def charger_donnees():
  matchs_cols = [
      "ID Match",
      "Adversaire",
      "Date",
      "Heure",
      "Résultat",
      "Score Réel",
      "Buteurs",
  ]
  pronos_cols = [
      "Participant",
      "Match",
      "Prono (1N2)",
      "Score",
      "Buteur",
      "Doublé ?",
      "Points",
  ]
  bonus_cols = ["Participant", "Points Bonus"]

  matchs = safe_read_csv(MATCHS_FILE, matchs_cols)
  pronos = safe_read_csv(PRONOS_FILE, pronos_cols)
  bonus = safe_read_csv(BONUS_FILE, bonus_cols)

  for col in matchs_cols:
    matchs[col] = matchs[col].fillna("").astype(str)
  for col in pronos_cols:
    if col != "Points":
      pronos[col] = pronos[col].fillna("").astype(str)

  pronos["Points"] = pd.to_numeric(pronos["Points"], errors="coerce").fillna(0)
  bonus["Points Bonus"] = pd.to_numeric(
      bonus["Points Bonus"], errors="coerce"
  ).fillna(0)

  return matchs, pronos, bonus


def sauvegarder_donnees(matchs, pronos, bonus):
  try:
    matchs.to_csv(MATCHS_FILE, index=False, encoding="utf-8")
    pronos.to_csv(PRONOS_FILE, index=False, encoding="utf-8")
    bonus.to_csv(BONUS_FILE, index=False, encoding="utf-8")
  except Exception:
    pass


df_matchs, df_pronos, df_bonus = charger_donnees()

# --- DESIGN & UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; color: #002D62; }
    h1 { color: #002D62 !important; font-weight: 800; text-transform: uppercase; }
    h2, h3, label, p, span { color: #002D62 !important; font-weight: 600; }
    .stButton > button { background-color: #E30613 !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; }
    [data-testid="stSidebar"] { background-color: #002D62; }
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label { color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("? Concours de Pronos - SMC")

menu = st.sidebar.radio(
    "Aller vers :", ["?? Faire mon Prono", "?? Classement", "?? Espace Admin"]
)


def obtenir_liste_participants():
  p_pronos = (
      df_pronos["Participant"].unique().tolist()
      if not df_pronos.empty and "Participant" in df_pronos.columns
      else []
  )
  p_bonus = (
      df_bonus["Participant"].unique().tolist()
      if not df_bonus.empty and "Participant" in df_bonus.columns
      else []
  )
  tous = set(PARTICIPANTS_INITIAUX + p_pronos + p_bonus)
  if "" in tous:
    tous.remove("")
  return sorted(list(tous))


if menu == "?? Faire mon Prono":
  st.header("?? Enregistrer ton Pronostic")
  if df_matchs.empty or len(df_matchs) == 0:
    st.info("Aucun match ouvert pour l'instant.")
  else:
    matchs_disponibles = df_matchs["ID Match"].tolist()
    choix_participant = st.selectbox(
        "Pseudo", obtenir_liste_participants() + ["? Nouveau"]
    )
    nom_utilisateur = (
        st.text_input("Nouveau pseudo :")
        if choix_participant == "? Nouveau"
        else choix_participant
    )
    match_choisi = st.selectbox("Match", matchs_disponibles)

    col1, col2 = st.columns(2)
    with col1:
      prono_1n2 = st.selectbox(
          "1N2", ["1 (Victoire Caen)", "N (Nul)", "2 (Défaite)"]
      )
      prono_score = st.text_input("Score exact (ex: 2-0)")
    with col2:
      buteurs_selectionnes = st.multiselect("Buteurs", EFFECTIF_SMC)

    annonce_double = st.selectbox(
        "Doublé ?", ["Aucun"] + buteurs_selectionnes
    )

    if st.button("Valider ??"):
      if nom_utilisateur and buteurs_selectionnes:
        choix_clean = prono_1n2.split()[0]
        buteurs_texte_str = ", ".join(buteurs_selectionnes)

        existing_idx = df_pronos[
            (df_pronos["Participant"] == nom_utilisateur)
            & (df_pronos["Match"] == match_choisi)
        ].index
        if not existing_idx.empty:
          idx = existing_idx[0]
          df_pronos.loc[idx, "Prono (1N2)"] = choix_clean
          df_pronos.loc[idx, "Score"] = prono_score
          df_pronos.loc[idx, "Buteur"] = buteurs_texte_str
          df_pronos.loc[idx, "Doublé ?"] = annonce_double
        else:
          new_row = pd.DataFrame({
              "Participant": [nom_utilisateur],
              "Match": [match_choisi],
              "Prono (1N2)": [choix_clean],
              "Score": [prono_score],
              "Buteur": [buteurs_texte_str],
              "Doublé ?": [annonce_double],
              "Points": [0],
          })
          df_pronos = pd.concat([df_pronos, new_row], ignore_index=True)

        sauvegarder_donnees(df_matchs, df_pronos, df_bonus)
        st.success("Prono enregistré !")
        st.rerun()

  if not df_pronos.empty:
    st.dataframe(df_pronos, use_container_width=True)

elif menu == "?? Classement":
  st.header("?? Classement Général")
  p_pronos_sum = (
      df_pronos.groupby("Participant")["Points"].sum().reset_index()
      if not df_pronos.empty
      else pd.DataFrame(columns=["Participant", "Points"])
  )
  if not p_pronos_sum.empty or not df_bonus.empty:
    classement_complet = pd.merge(
        p_pronos_sum, df_bonus, on="Participant", how="outer"
    ).fillna(0)
    classement_complet["Points Total"] = (
        classement_complet["Points"]
        + classement_complet["Points Bonus"].astype(float)
    )
    classement_final = (
        classement_complet[["Participant", "Points Total"]]
        .sort_values(by="Points Total", ascending=False)
        .reset_index(drop=True)
    )
    classement_final.index += 1
    st.dataframe(classement_final, use_container_width=True)
  else:
    st.info("Classement vide.")

elif menu == "?? Espace Admin":
  st.header("?? Espace Organisateur")
  mdp = st.text_input("Mot de passe :", type="password")
  if mdp == MOT_DE_PASSE_ADMIN:
    st.success("Connecté !")
    with st.form("f_match"):
      id_m = st.text_input("Nom du Match (ex: SMC - Bastia)")
      adv = st.text_input("Adversaire")
      res = st.selectbox("Résultat Réel", ["", "1", "N", "2"])
      sc_r = st.text_input("Score Réel (ex: 2-1)")
      but_r = st.text_input("Buteurs réels")
      if st.form_submit_button("Enregistrer Match"):
        if id_m:
          df_matchs = pd.concat(
              [
                  df_matchs,
                  pd.DataFrame({
                      "ID Match": [id_m],
                      "Adversaire": [adv],
                      "Date": ["2026-08-25"],
                      "Heure": ["20:00"],
                      "Résultat": [res],
                      "Score Réel": [sc_r],
                      "Buteurs": [but_r],
                  }),
              ],
              ignore_index=True,
          )
          sauvegarder_donnees(df_matchs, df_pronos, df_bonus)
          st.success("Match ajouté !")
          st.rerun()
    st.dataframe(df_matchs, use_container_width=True)
  elif mdp != "":
    st.error("Mot de passe incorrect.")