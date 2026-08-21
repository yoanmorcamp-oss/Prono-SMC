import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pronos SMC - Saison 2026-2027", page_icon="⚽", layout="wide"
)

st.title("⚽ Concours de Pronos - Stade Malherbe de Caen")

# --- GESTION DES FICHIERS CSV (PERSISTANCE) ---
MATCHS_FILE = "matchs.csv"
PRONOS_FILE = "pronos.csv"

# Effectif officiel actualisé du SMC
EFFECTIF_SMC = [
    "Aucun",
    "Anthony Mandréa",
    "Yannis Clémentia",
    "Parfait Mandanda",
    "Nassim Titebah",
    "Diabé Bolumbu",
    "Sacha M'Baka",
    "Dennis Appiah",
    "Nazim Babai",
    "Hugo Lamouliatte",
    "Josué Kimboma",
    "Freddy Bomo",
    "Gabin Tome",
    "Léo Milliner",
    "Zoumana Bagbema",
    "Mohamed El Idrissi",
    "Samuel Noireau-Dauriat",
    "Fahd El Khoumisti",
    "Ivann Botella",
    "Armand Gnanduillet",
    "Keelyan Portut",
    "Mohamed Hafid",
    "Salim Diakité",
    "Autre joueur",
]


def charger_donnees():
  if os.path.exists(MATCHS_FILE):
    matchs = pd.read_csv(MATCHS_FILE)
    for col in matchs.columns:
      matchs[col] = matchs[col].fillna("").astype(str)
  else:
    matchs = pd.DataFrame(
        columns=["ID Match", "Adversaire", "Résultat", "Score Réel", "Buteurs"]
    )

  if os.path.exists(PRONOS_FILE):
    pronos = pd.read_csv(PRONOS_FILE)
    for col in pronos.columns:
      if col != "Points":
        pronos[col] = pronos[col].fillna("").astype(str)
      else:
        pronos[col] = pd.to_numeric(pronos[col], errors="coerce").fillna(0)
  else:
    pronos = pd.DataFrame(
        columns=[
            "Participant",
            "Match",
            "Prono (1N2)",
            "Score",
            "Buteur 1",
            "Buteur 2",
            "Annonce Doublé",
            "Points",
        ]
    )

  return matchs, pronos


def sauvegarder_donnees(matchs, pronos):
  matchs.to_csv(MATCHS_FILE, index=False)
  pronos.to_csv(PRONOS_FILE, index=False)


df_matchs, df_pronos = charger_donnees()

# --- MENU LATÉRAL PROPRE ---
st.sidebar.title("Menu")
menu = st.sidebar.radio(
    "Aller vers :", ["📝 Faire mon Prono", "🏆 Classement", "⚙️ Espace Admin"]
)

# ---------------------------------------------------------------------------
# 1. ESPACE PARTICIPANTS
# ---------------------------------------------------------------------------
if menu == "📝 Faire mon Prono":
  st.header("🎯 Enregistrer ton Pronostic")

  if df_matchs.empty:
    st.info(
        "Aucun match n'est ouvert pour l'instant. Demande à l'admin d'en créer"
        " un !"
    )
  else:
    with st.form("form_user_prono"):
      nom_utilisateur = st.text_input("Ton Prénom / Pseudo")

      matchs_disponibles = df_matchs[df_matchs["Score Réel"] == ""][
          "ID Match"
      ].tolist()

      if not matchs_disponibles:
        st.warning("Tous les matchs enregistrés sont déjà terminés !")
      else:
        match_choisi = st.selectbox(
            "Choisis le match concerné", matchs_disponibles
        )

        col1, col2 = st.columns(2)
        with col1:
          prono_1n2 = st.selectbox(
              "Issue du match", ["1 (Victoire Caen)", "N (Nul)", "2 (Défaite)"]
          )
          prono_score = st.text_input("Score exact pronostiqué (ex: 2-0)")

        with col2:
          buteur_1 = st.selectbox("1er Buteur pronostiqué", EFFECTIF_SMC)
          buteur_2 = st.selectbox(
              "2ème Buteur pronostiqué (optionnel)", EFFECTIF_SMC
          )

        st.markdown("---")
        # Sélection claire pour le doublé en fonction des buteurs choisis
        buteurs_possibles_pour_double = ["Aucun"]
        if buteur_1 != "Aucun":
          buteurs_possibles_pour_double.append(buteur_1)
        if buteur_2 != "Aucun" and buteur_2 != buteur_1:
          buteurs_possibles_pour_double.append(buteur_2)

        annonce_double = st.selectbox(
            "Annonces-tu un doublé ? Si oui, de quel joueur ?",
            buteurs_possibles_pour_double,
        )

        submit_user_prono = st.form_submit_button("Valider mon pronostic 🚀")

        if submit_user_prono:
          if not nom_utilisateur.strip():
            st.error("⚠️ Tu dois entrer ton prénom ou pseudo !")
          else:
            choix_clean = prono_1n2.split()[0]

            existing_idx = df_pronos[
                (df_pronos["Participant"] == nom_utilisateur)
                & (df_pronos["Match"] == match_choisi)
            ].index

            if not existing_idx.empty:
              idx = existing_idx[0]
              df_pronos.loc[idx, "Prono (1N2)"] = choix_clean
              df_pronos.loc[idx, "Score"] = prono_score
              df_pronos.loc[idx, "Buteur 1"] = buteur_1
              df_pronos.loc[idx, "Buteur 2"] = buteur_2
              df_pronos.loc[idx, "Annonce Doublé"] = annonce_double
              st.success(
                  f"👍 Mis à jour {nom_utilisateur} pour {match_choisi} !"
              )
            else:
              new_row = pd.DataFrame({
                  "Participant": [nom_utilisateur],
                  "Match": [match_choisi],
                  "Prono (1N2)": [choix_clean],
                  "Score": [prono_score],
                  "Buteur 1": [buteur_1],
                  "Buteur 2": [buteur_2],
                  "Annonce Doublé": [annonce_double],
                  "Points": [0],
              })
              df_pronos = pd.concat([df_pronos, new_row], ignore_index=True)
              st.success(f"🎉 Validé {nom_utilisateur} !")

            sauvegarder_donnees(df_matchs, df_pronos)
            st.rerun()

    st.markdown("---")
    st.subheader("👀 Pronos enregistrés :")
    if not df_pronos.empty:
      st.dataframe(df_pronos, use_container_width=True)


# ---------------------------------------------------------------------------
# 2. CLASSEMENT
# ---------------------------------------------------------------------------
elif menu == "🏆 Classement":
  st.header("🏆 Classement Général de la Saison")

  if not df_pronos.empty:
    df_pronos["Points"] = pd.to_numeric(
        df_pronos["Points"], errors="coerce"
    ).fillna(0)
    classement = (
        df_pronos.groupby("Participant")["Points"].sum().reset_index()
    )
    classement = classement.sort_values(by="Points", ascending=False).reset_index(
        drop=True
    )
    classement.index += 1
    st.table(classement)

    st.subheader("📋 Historique complet")
    st.dataframe(df_pronos, use_container_width=True)
  else:
    st.info("Le classement est vide pour l'instant.")


# ---------------------------------------------------------------------------
# 3. ESPACE ADMIN
# ---------------------------------------------------------------------------
elif menu == "⚙️ Espace Admin":
  st.header("🔐 Espace Organisateur")

  st.subheader("1. Ajouter un match du SMC")
  with st.form("form_admin_match"):
    id_match = st.text_input("Nom du Match (ex: SMC - Bastia)")
    adversaire = st.text_input("Équipe adverse")
    resultat_reel = st.selectbox(
        "Résultat Réel (À remplir après le match)", ["", "1", "N", "2"]
    )
    score_reel = st.text_input("Score Réel (ex: 2-1)")
    buteurs_reels = st.text_input(
        "Buteurs réels (ex: Botella, Hafid)"
    )  # Séparés par des virgules

    submit_admin_match = st.form_submit_button("Enregistrer le match")

    if submit_admin_match:
      if id_match:
        existing_m_idx = df_matchs[df_matchs["ID Match"] == id_match].index
        if not existing_m_idx.empty:
          idx = existing_m_idx[0]
          df_matchs.loc[idx, "Résultat"] = resultat_reel
          df_matchs.loc[idx, "Score Réel"] = score_reel
          df_matchs.loc[idx, "Buteurs"] = buteurs_reels
          st.success(f"Match '{id_match}' mis à jour !")
        else:
          new_m = pd.DataFrame({
              "ID Match": [id_match],
              "Adversaire": [adversaire],
              "Résultat": [resultat_reel],
              "Score Réel": [score_reel],
              "Buteurs": [buteurs_reels],
          })
          df_matchs = pd.concat([df_matchs, new_m], ignore_index=True)
          st.success(f"Match '{id_match}' créé avec succès !")

        sauvegarder_donnees(df_matchs, df_pronos)
        st.rerun()

  st.subheader("Matchs configurés :")
  st.dataframe(df_matchs, use_container_width=True)

  st.markdown("---")
  st.subheader("2. Calculer les points")
  if st.button("⚡ Lancer le calcul des points"):
    compteur_maj = 0
    for index, prono in df_pronos.iterrows():
      pts = 0
      m_id = str(prono["Match"])
      match_correspondant = df_matchs[df_matchs["ID Match"] == m_id]

      if not match_correspondant.empty:
        res_reel = str(match_correspondant.iloc[0]["Résultat"]).strip()
        sc_reel = str(match_correspondant.iloc[0]["Score Réel"]).strip()
        buts_reel = str(match_correspondant.iloc[0]["Buteurs"]).lower()

        if res_reel != "":
          # 1N2
          if str(prono["Prono (1N2)"]).strip() == res_reel:
            pts += 2
          # Score exact
          if str(prono["Score"]).strip() == sc_reel:
            pts += 10

          liste_buteurs_reels = [
              b.strip().lower() for b in buts_reel.split(",") if b.strip() != ""
          ]

          # Gestion Buteur 1
          b1 = str(prono["Buteur 1"]).strip().lower()
          if b1 != "" and b1 != "aucun":
            nb_1 = liste_buteurs_reels.count(b1)
            if nb_1 > 0:
              pts += nb_1 * 3

          # Gestion Buteur 2
          b2 = str(prono["Buteur 2"]).strip().lower()
          if b2 != "" and b2 != "aucun":
            nb_2 = liste_buteurs_reels.count(b2)
            if nb_2 > 0:
              pts += nb_2 * 3

          # Gestion du doublé annoncé
          joueur_double = str(prono["Annonce Doublé"]).strip().lower()
          if joueur_double != "" and joueur_double != "aucun":
            nb_buts_joueur = liste_buteurs_reels.count(joueur_double)
            if nb_buts_joueur >= 2:
              pts += 5
            else:
              pts -= 3

          df_pronos.loc[index, "Points"] = pts
          compteur_maj += 1

    sauvegarder_donnees(df_matchs, df_pronos)
    st.success(
        f"Calcul terminé ! {compteur_maj} pronostics évalués avec succès."
    )
    st.rerun()