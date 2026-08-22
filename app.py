import base64
from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pronos SMC - Saison 2026-2027", page_icon="?", layout="wide"
)

MOT_DE_PASSE_ADMIN = "yoan"

# --- DESIGN ---
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

# --- LOGO & TITRE ---
col_logo, col_titre = st.columns([1, 8])
with col_logo:
  if os.path.exists("logo_smc.png"):
    with open("logo_smc.png", "rb") as f:
      encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<img src="data:image/png;base64,{encoded}" width="65"'
        ' style="border-radius: 8px; margin-top: 5px;" />',
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        """
        <div style="background-color: #002D62; border: 2px solid #E30613; border-radius: 10px; text-align: center; padding: 10px; width: 65px;">
            <span style="color: white; font-weight: 900; font-size: 18px;">SMC</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_titre:
  st.markdown(
      "<h1 style='border-bottom: 4px solid #E30613; padding-bottom: 8px;"
      " margin-top: 5px;'>Concours de Pronos - SMC</h1>",
      unsafe_allow_html=True,
  )

# --- GESTION DES FICHIERS ---
MATCHS_FILE = "matchs.csv"
PRONOS_FILE = "pronos.csv"
BONUS_FILE = "bonus.csv"

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


def charger_donnees():
  # Matchs
  if os.path.exists(MATCHS_FILE):
    try:
      matchs = pd.read_csv(MATCHS_FILE)
    except Exception:
      matchs = pd.DataFrame(
          columns=[
              "ID Match",
              "Adversaire",
              "Date",
              "Heure",
              "Résultat",
              "Score Réel",
              "Buteurs",
          ]
      )
  else:
    matchs = pd.DataFrame(
        columns=[
            "ID Match",
            "Adversaire",
            "Date",
            "Heure",
            "Résultat",
            "Score Réel",
            "Buteurs",
        ]
    )

  # Pronos
  if os.path.exists(PRONOS_FILE):
    try:
      pronos = pd.read_csv(PRONOS_FILE)
    except Exception:
      pronos = pd.DataFrame(
          columns=[
              "Participant",
              "Match",
              "Prono (1N2)",
              "Score",
              "Buteur",
              "Doublé ?",
              "Points",
          ]
      )
  else:
    pronos = pd.DataFrame(
        columns=[
            "Participant",
            "Match",
            "Prono (1N2)",
            "Score",
            "Buteur",
            "Doublé ?",
            "Points",
        ]
    )

  # Bonus
  if os.path.exists(BONUS_FILE):
    try:
      bonus = pd.read_csv(BONUS_FILE)
    except Exception:
      bonus = pd.DataFrame(columns=["Participant", "Points Bonus"])
  else:
    bonus = pd.DataFrame(columns=["Participant", "Points Bonus"])

  # Nettoyage des colonnes manquantes ou NaN
  for col in [
      "ID Match",
      "Adversaire",
      "Date",
      "Heure",
      "Résultat",
      "Score Réel",
      "Buteurs",
  ]:
    if col not in matchs.columns:
      matchs[col] = ""
    matchs[col] = matchs[col].fillna("").astype(str)

  for col in [
      "Participant",
      "Match",
      "Prono (1N2)",
      "Score",
      "Buteur",
      "Doublé ?",
  ]:
    if col not in pronos.columns:
      pronos[col] = ""
    pronos[col] = pronos[col].fillna("").astype(str)

  if "Points" not in pronos.columns:
    pronos["Points"] = 0
  else:
    pronos["Points"] = pd.to_numeric(pronos["Points"], errors="coerce").fillna(0)

  if "Participant" not in bonus.columns:
    bonus["Participant"] = ""
  if "Points Bonus" not in bonus.columns:
    bonus["Points Bonus"] = 0
  bonus["Points Bonus"] = pd.to_numeric(
      bonus["Points Bonus"], errors="coerce"
  ).fillna(0)

  return matchs, pronos, bonus


def sauvegarder_donnees(matchs, pronos, bonus):
  matchs.to_csv(MATCHS_FILE, index=False)
  pronos.to_csv(PRONOS_FILE, index=False)
  bonus.to_csv(BONUS_FILE, index=False)


df_matchs, df_pronos, df_bonus = charger_donnees()

# --- MENU ---
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


# 1. PRONOS
if menu == "?? Faire mon Prono":
  st.header("?? Enregistrer ton Pronostic")

  if df_matchs.empty or len(df_matchs) == 0:
    st.info(
        "Aucun match n'est ouvert pour l'instant. Demande à Yoan d'en créer"
        " un dans l'Espace Admin !"
    )
  else:
    matchs_disponibles = df_matchs["ID Match"].tolist()
    tous_participants = obtenir_liste_participants()
    options_participants = tous_participants + ["? Nouveau participant"]

    choix_participant = st.selectbox(
        "Choisis ton Prénom / Pseudo", options_participants
    )
    if choix_participant == "? Nouveau participant":
      nom_utilisateur = st.text_input(
          "Entre ton nouveau prénom / pseudo :"
      ).strip()
    else:
      nom_utilisateur = choix_participant

    match_choisi = st.selectbox("Choisis le match concerné", matchs_disponibles)

    col1, col2 = st.columns(2)
    with col1:
      prono_1n2 = st.selectbox(
          "Issue du match", ["1 (Victoire Caen)", "N (Nul)", "2 (Défaite)"]
      )
      prono_score = st.text_input("Score exact pronostiqué (ex: 2-0)")
    with col2:
      buteurs_selectionnes = st.multiselect(
          "Buteur(s) pronostiqué(s)", EFFECTIF_SMC
      )

    options_double = ["Aucun"] + buteurs_selectionnes
    annonce_double = st.selectbox("Annonces-tu un doublé ?", options_double)

    if st.button("Valider mon pronostic ??"):
      if not nom_utilisateur:
        st.error("?? Entre un pseudo valide !")
      elif not buteurs_selectionnes:
        st.error("?? Sélectionne au moins un buteur !")
      else:
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
        st.success(f"?? Prono enregistré pour {nom_utilisateur} !")
        st.rerun()

  st.markdown("---")
  st.subheader("?? Pronos enregistrés :")
  if not df_pronos.empty:
    st.dataframe(df_pronos, use_container_width=True)

# 2. CLASSEMENT
elif menu == "?? Classement":
  st.header("?? Classement Général")

  p_pronos_sum = (
      df_pronos.groupby("Participant")["Points"].sum().reset_index()
      if not df_pronos.empty and "Participant" in df_pronos.columns
      else pd.DataFrame(columns=["Participant", "Points"])
  )
  p_bonus_sum = (
      df_bonus.copy()
      if not df_bonus.empty and "Participant" in df_bonus.columns
      else pd.DataFrame(columns=["Participant", "Points Bonus"])
  )

  if not p_pronos_sum.empty or not p_bonus_sum.empty:
    classement_complet = pd.merge(
        p_pronos_sum, p_bonus_sum, on="Participant", how="outer"
    ).fillna(0)
    classement_complet["Points Total"] = (
        classement_complet["Points"] + classement_complet["Points Bonus"]
    )
    classement_final = (
        classement_complet[["Participant", "Points Total"]]
        .sort_values(by="Points Total", ascending=False)
        .reset_index(drop=True)
    )
    classement_final.index += 1

    st.dataframe(classement_final, use_container_width=True)
  else:
    st.info("Classement vide pour le moment.")

# 3. ADMIN
elif menu == "?? Espace Admin":
  st.header("?? Espace Organisateur")
  mdp = st.text_input("Mot de passe :", type="password")

  if mdp == MOT_DE_PASSE_ADMIN:
    st.success("Accès autorisé.")

    st.subheader("1. Points bonus initiaux")
    with st.form("f_bonus"):
      part = st.selectbox("Participant", obtenir_liste_participants())
      pts_b = st.number_input("Points des 2 premiers matchs", value=0, step=1)
      if st.form_submit_button("Enregistrer Bonus"):
        existing_b = df_bonus[df_bonus["Participant"] == part].index
        if not existing_b.empty:
          df_bonus.loc[existing_b[0], "Points Bonus"] = pts_b
        else:
          df_bonus = pd.concat(
              [
                  df_bonus,
                  pd.DataFrame(
                      {"Participant": [part], "Points Bonus": [pts_b]}
                  ),
              ],
              ignore_index=True,
          )
        sauvegarder_donnees(df_matchs, df_pronos, df_bonus)
        st.success("Bonus mis à jour !")
        st.rerun()

    st.markdown("---")
    st.subheader("2. Ajouter un match")
    with st.form("f_match"):
      id_m = st.text_input("Nom du Match (ex: SMC - Bastia)")
      adv = st.text_input("Adversaire")
      res = st.selectbox("Résultat Réel", ["", "1", "N", "2"])
      sc_r = st.text_input("Score Réel (ex: 2-1)")
      but_r = st.text_input("Buteurs réels (ex: Botella, Hafid)")

      if st.form_submit_button("Enregistrer Match"):
        if id_m:
          existing_m = df_matchs[df_matchs["ID Match"] == id_m].index
          if not existing_m.empty:
            df_matchs.loc[existing_m[0], "Résultat"] = res
            df_matchs.loc[existing_m[0], "Score Réel"] = sc_r
            df_matchs.loc[existing_m[0], "Buteurs"] = but_r
          else:
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
          st.success("Match enregistré !")
          st.rerun()

    st.markdown("---")
    st.subheader("3. Calculer les points")
    if st.button("? Calculer"):
      for index, prono in df_pronos.iterrows():
        pts = 0
        m_id = str(prono["Match"])
        m_corr = df_matchs[df_matchs["ID Match"] == m_id]
        if not m_corr.empty:
          res_reel = str(m_corr.iloc[0]["Résultat"]).strip()
          sc_reel = str(m_corr.iloc[0]["Score Réel"]).strip()
          buts_reel = str(m_corr.iloc[0]["Buteurs"]).lower()

          if res_reel != "":
            if str(prono["Prono (1N2)"]).strip() == res_reel:
              pts += 2
            if str(prono["Score"]).strip() == sc_reel:
              pts += 10

            liste_buteurs_reels = [
                b.strip() for b in buts_reel.split(",") if b.strip() != ""
            ]
            buteurs_pronos = [
                b.strip()
                for b in str(prono["Buteur"]).lower().split(",")
                if b.strip() != ""
            ]
            for bp in buteurs_pronos:
              if bp in liste_buteurs_reels:
                pts += 3

            df_pronos.loc[index, "Points"] = pts

      sauvegarder_donnees(df_matchs, df_pronos, df_bonus)
      st.success("Calcul des points effectué !")
      st.rerun()
  elif mdp != "":
    st.error("Mot de passe incorrect.")