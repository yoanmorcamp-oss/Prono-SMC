import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pronos SMC - Saison 2026-2027", page_icon="⚽", layout="wide"
)

st.title("⚽ Concours de Pronos - Stade Malherbe de Caen")

# --- SIMULATION DE BASE DE DONNÉES EN MÉMOIRE ---
if "matchs" not in st.session_state:
  st.session_state.matchs = pd.DataFrame(
      columns=["ID Match", "Adversaire", "Résultat", "Score Réel", "Buteurs"]
  )

if "pronos" not in st.session_state:
  st.session_state.pronos = pd.DataFrame(
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

  if st.session_state.matchs.empty:
    st.info(
        "Aucun match n'est ouvert pour l'instant. Demande à l'admin d'en créer"
        " un !"
    )
  else:
    with st.form("form_user_prono"):
      nom_utilisateur = st.text_input("Ton Prénom / Pseudo")
      matchs_disponibles = st.session_state.matchs[
          st.session_state.matchs["Score Réel"] == ""
      ]["ID Match"].tolist()

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
          prono_score = st.text_input(
              "Score exact pronostiqué (ex: 2-0)"
          )  # ex: 2-1

        with col2:
          prono_buteur = st.text_input("Buteur pronostiqué (ex: Mendy)")
          annonce_double = st.selectbox(
              "Annonces-tu un doublé de ce buteur ?", ["NON", "OUI"]
          )

        submit_user_prono = st.form_submit_button("Valider mon pronostic 🚀")

        if submit_user_prono:
          if not nom_utilisateur.strip():
            st.error("⚠️ Tu dois entrer ton prénom ou pseudo !")
          else:
            choix_clean = prono_1n2.split()[0]
            existing = st.session_state.pronos[
                (st.session_state.pronos["Participant"] == nom_utilisateur)
                & (st.session_state.pronos["Match"] == match_choisi)
            ]

            if not existing.empty:
              idx = existing.index[0]
              st.session_state.pronos.at[idx, "Prono (1N2)"] = choix_clean
              st.session_state.pronos.at[idx, "Score"] = prono_score
              st.session_state.pronos.at[idx, "Buteur"] = prono_buteur
              st.session_state.pronos.at[idx, "Doublé ?"] = annonce_double
              st.success(
                  f"👍 Mis à jour {nom_utilisateur} pour {match_choisi} !"
              )
            else:
              new_prono = pd.DataFrame({
                  "Participant": [nom_utilisateur],
                  "Match": [match_choisi],
                  "Prono (1N2)": [choix_clean],
                  "Score": [prono_score],
                  "Buteur": [prono_buteur],
                  "Doublé ?": [annonce_double],
                  "Points": [0],
              })
              st.session_state.pronos = pd.concat(
                  [st.session_state.pronos, new_prono], ignore_index=True
              )
              st.success(f"🎉 Validé {nom_utilisateur} !")

    st.markdown("---")
    st.subheader("👀 Pronos enregistrés :")
    if not st.session_state.pronos.empty:
      st.dataframe(
          st.session_state.pronos[[
              "Participant",
              "Match",
              "Prono (1N2)",
              "Score",
              "Buteur",
              "Doublé ?",
          ]],
          use_container_width=True,
      )


# ---------------------------------------------------------------------------
# 2. CLASSEMENT
# ---------------------------------------------------------------------------
elif menu == "🏆 Classement":
  st.header("🏆 Classement Général de la Saison")

  if not st.session_state.pronos.empty:
    classement = (
        st.session_state.pronos.groupby("Participant")["Points"]
        .sum()
        .reset_index()
    )
    classement = classement.sort_values(by="Points", ascending=False).reset_index(
        drop=True
    )
    classement.index += 1
    st.table(classement)

    st.subheader("📋 Historique complet")
    st.dataframe(st.session_state.pronos, use_container_width=True)
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
    buteurs_reels = st.text_input("Buteurs réels (ex: Mendy, Mendy)")

    submit_admin_match = st.form_submit_button("Enregistrer le match")

    if submit_admin_match:
      if id_match:
        matchs_df = st.session_state.matchs
        if not matchs_df.empty and id_match in matchs_df["ID Match"].values:
          idx = matchs_df[matchs_df["ID Match"] == id_match].index[0]
          st.session_state.matchs.at[idx, "Résultat"] = resultat_reel
          st.session_state.matchs.at[idx, "Score Réel"] = score_reel
          st.session_state.matchs.at[idx, "Buteurs"] = buteurs_reels
          st.success(f"Match '{id_match}' mis à jour !")
        else:
          new_m = pd.DataFrame({
              "ID Match": [id_match],
              "Adversaire": [adversaire],
              "Résultat": [resultat_reel],
              "Score Réel": [score_reel],
              "Buteurs": [buteurs_reels],
          })
          st.session_state.matchs = pd.concat(
              [st.session_state.matchs, new_m], ignore_index=True
          )
          st.success(f"Match '{id_match}' créé avec succès !")

  st.subheader("Matchs configurés :")
  st.dataframe(st.session_state.matchs, use_container_width=True)

  st.markdown("---")
  st.subheader("2. Calculer les points")
  if st.button("⚡ Lancer le calcul des points"):
    compteur_maj = 0
    for index, prono in st.session_state.pronos.iterrows():
      pts = 0
      m_id = prono["Match"]
      match_correspondant = st.session_state.matchs[
          st.session_state.matchs["ID Match"] == m_id
      ]

      if not match_correspondant.empty:
        res_reel = str(match_correspondant.iloc[0]["Résultat"]).strip()
        sc_reel = str(match_correspondant.iloc[0]["Score Réel"]).strip()
        buts_reel = str(match_correspondant.iloc[0]["Buteurs"]).lower()

        if res_reel != "":
          if prono["Prono (1N2)"] == res_reel:
            pts += 2
          if prono["Score"].strip() == sc_reel:
            pts += 10

          buteur_prono = str(prono["Buteur"]).strip().lower()
          if buteur_prono != "" and buteur_prono != "aucun":
            liste_buteurs = [b.strip() for b in buts_reel.split(",")]
            nb_buts = liste_buteurs.count(buteur_prono)
            if nb_buts > 0:
              pts += nb_buts * 3

            if prono["Doublé ?"] == "OUI":
              if nb_buts >= 2:
                pts += 5
              else:
                pts -= 3

          st.session_state.pronos.at[index, "Points"] = pts
          compteur_maj += 1

    st.success(
        f"Calcul terminé ! {compteur_maj} pronostics évalués avec succès."
    )