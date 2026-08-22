from datetime import datetime
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
BONUS_FILE = "bonus.csv"

# Liste officielle de vos participants (avec "Jo")
PARTICIPANTS_INITIAUX = [
    "Nathéo",
    "Adri",
    "Allan",
    "Jo",
    "Vincent",
    "Tony",
    "Yoan",
]

# Effectif officiel actualisé du SMC
EFFECTIF_SMC = [
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
]


def charger_donnees():
  if os.path.exists(MATCHS_FILE):
    matchs = pd.read_csv(MATCHS_FILE)
    for col in matchs.columns:
      matchs[col] = matchs[col].fillna("").astype(str)
    if "Date" not in matchs.columns:
      matchs["Date"] = "2026-08-25"
    if "Heure" not in matchs.columns:
      matchs["Heure"] = "20:00"
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
            "Buteurs Pronostiqués",
            "Annonce Doublé",
            "Points",
        ]
    )

  if os.path.exists(BONUS_FILE):
    bonus = pd.read_csv(BONUS_FILE)
    bonus["Points Bonus"] = pd.to_numeric(
        bonus["Points Bonus"], errors="coerce"
    ).fillna(0)
  else:
    bonus = pd.DataFrame(columns=["Participant", "Points Bonus"])

  return matchs, pronos, bonus


def sauvegarder_donnees(matchs, pronos, bonus):
  matchs.to_csv(MATCHS_FILE, index=False)
  pronos.to_csv(PRONOS_FILE, index=False)
  bonus.to_csv(BONUS_FILE, index=False)


df_matchs, df_pronos, df_bonus = charger_donnees()

# --- MENU LATÉRAL PROPRE ---
st.sidebar.title("Menu")
menu = st.sidebar.radio(
    "Aller vers :", ["📝 Faire mon Prono", "🏆 Classement", "⚙️ Espace Admin"]
)


def obtenir_liste_participants():
  p_pronos = (
      df_pronos["Participant"].unique().tolist()
      if not df_pronos.empty
      else []
  )
  p_bonus = (
      df_bonus["Participant"].unique().tolist() if not df_bonus.empty else []
  )
  tous = sorted(list(set(PARTICIPANTS_INITIAUX + p_pronos + p_bonus)))
  return tous


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
    maintenant = datetime.now()
    matchs_disponibles = []

    for idx, row in df_matchs.iterrows():
      m_id = row["ID Match"]
      date_str = row.get("Date", "2026-01-01")
      heure_str = row.get("Heure", "00:00")
      try:
        coup_envoi = datetime.strptime(
            f"{date_str} {heure_str}", "%Y-%m-%d %H:%M"
        )
        if maintenant < coup_envoi and str(row["Score Réel"]).strip() == "":
          matchs_disponibles.append(m_id)
      except Exception:
        if str(row["Score Réel"]).strip() == "":
          matchs_disponibles.append(m_id)

    if not matchs_disponibles:
      st.warning(
          "🔒 Aucun match n'est ouvert actuellement (le coup d'envoi est passé ou"
          " les matchs sont terminés)."
      )
    else:
      tous_participants = obtenir_liste_participants()
      options_participants = tous_participants + ["➕ Nouveau participant"]

      choix_participant = st.selectbox(
          "Choisis ton Prénom / Pseudo", options_participants
      )

      if choix_participant == "➕ Nouveau participant":
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
            "Buteur(s) pronostiqué(s) (choisis-en un ou plusieurs)", EFFECTIF_SMC
        )

      st.markdown("---")

      options_double = ["Aucun"] + buteurs_selectionnes
      annonce_double = st.selectbox(
          "Annonces-tu un doublé ? (Choisis parmi tes buteurs ci-dessus)",
          options_double,
      )

      if st.button("Valider mon pronostic 🚀"):
        if not nom_utilisateur:
          st.error("⚠️ Tu dois entrer ou sélectionner un prénom/pseudo valide !")
        elif not buteurs_selectionnes:
          st.error("⚠️ Tu dois sélectionner au moins un buteur !")
        else:
          match_info = df_matchs[df_matchs["ID Match"] == match_choisi].iloc[0]
          try:
            coup_envoi = datetime.strptime(
                f"{match_info.get('Date', '2026-01-01')} {match_info.get('Heure', '00:00')}",
                "%Y-%m-%d %H:%M",
            )
            if datetime.now() >= coup_envoi:
              st.error(
                  "❌ Trop tard ! Le coup d'envoi de ce match a été donné, les"
                  " pronos sont verrouillés."
              )
              st.stop()
          except Exception:
            pass

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
            df_pronos.loc[idx, "Buteurs Pronostiqués"] = buteurs_texte_str
            df_pronos.loc[idx, "Annonce Doublé"] = annonce_double
            st.success(f"👍 Mis à jour {nom_utilisateur} pour {match_choisi} !")
          else:
            new_row = pd.DataFrame({
                "Participant": [nom_utilisateur],
                "Match": [match_choisi],
                "Prono (1N2)": [choix_clean],
                "Score": [prono_score],
                "Buteurs Pronostiqués": [buteurs_texte_str],
                "Annonce Doublé": [annonce_double],
                "Points": [0],
            })
            df_pronos = pd.concat([df_pronos, new_row], ignore_index=True)
            st.success(f"🎉 Validé {nom_utilisateur} !")

          sauvegarder_donnees(df_matchs, df_pronos, df_bonus)
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

  p_pronos_sum = (
      df_pronos.groupby("Participant")["Points"].sum().reset_index()
      if not df_pronos.empty
      else pd.DataFrame(columns=["Participant", "Points"])
  )
  p_bonus_sum = (
      df_bonus.copy()
      if not df_bonus.empty
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

    st.table(classement_final)

    st.subheader("📋 Historique complet des pronos et points")
    st.dataframe(df_pronos, use_container_width=True)
  else:
    st.info("Le classement est vide pour l'instant.")


# ---------------------------------------------------------------------------
# 3. ESPACE ADMIN
# ---------------------------------------------------------------------------
elif menu == "⚙️ Espace Admin":
  st.header("🔐 Espace Organisateur")

  st.subheader(
      "1. Attribuer les points des 2 premiers matchs (Classement initial)"
  )
  with st.form("form_admin_bonus"):
    tous_participants_admin = obtenir_liste_participants()

    participant_init = st.selectbox("Participant", tous_participants_admin)
    points_initiaux = st.number_input(
        "Points obtenus lors des 2 premiers matchs", value=0, step=1
    )
    submit_bonus = st.form_submit_button("Enregistrer / Mettre à jour les points")

    if submit_bonus:
      if participant_init.strip():
        p_nom = participant_init.strip()
        existing_b = df_bonus[df_bonus["Participant"] == p_nom].index
        if not existing_b.empty:
          df_bonus.loc[existing_b[0], "Points Bonus"] = points_initiaux
        else:
          new_b = pd.DataFrame(
              {"Participant": [p_nom], "Points Bonus": [points_initiaux]}
          )
          df_bonus = pd.concat([df_bonus, new_b], ignore_index=True)

        sauvegarder_donnees(df_matchs, df_pronos, df_bonus)
        st.success(
            f"Points initiaux enregistrés pour {p_nom} : {points_initiaux} pts"
            " !"
        )
        st.rerun()

  if not df_bonus.empty:
    st.subheader("Points initiaux enregistrés :")
    st.dataframe(df_bonus, use_container_width=True)

  st.markdown("---")
  st.subheader("2. Ajouter un match du SMC")
  with st.form("form_admin_match"):
    id_match = st.text_input("Nom du Match (ex: SMC - Bastia)")
    adversaire = st.text_input("Équipe adverse")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
      date_match = st.text_input("Date du match (AAAA-MM-JJ)", value="2026-08-29")
    with col_d2:
      heure_match = st.text_input(
          "Heure du coup d'envoi (HH:MM)", value="20:00"
      )

    resultat_reel = st.selectbox(
        "Résultat Réel (À remplir après le match)", ["", "1", "N", "2"]
    )
    score_reel = st.text_input("Score Réel (ex: 2-1)")
    buteurs_reels = st.text_input("Buteurs réels (ex: Botella, Hafid)")

    submit_admin_match = st.form_submit_button("Enregistrer le match")

    if submit_admin_match:
      if id_match:
        existing_m_idx = df_matchs[df_matchs["ID Match"] == id_match].index
        if not existing_m_idx.empty:
          idx = existing_m_idx[0]
          df_matchs.loc[idx, "Date"] = date_match
          df_matchs.loc[idx, "Heure"] = heure_match
          df_matchs.loc[idx, "Résultat"] = resultat_reel
          df_matchs.loc[idx, "Score Réel"] = score_reel
          df_matchs.loc[idx, "Buteurs"] = buteurs_reels
          st.success(f"Match '{id_match}' mis à jour !")
        else:
          new_m = pd.DataFrame({
              "ID Match": [id_match],
              "Adversaire": [adversaire],
              "Date": [date_match],
              "Heure": [heure_match],
              "Résultat": [resultat_reel],
              "Score Réel": [score_reel],
              "Buteurs": [buteurs_reels],
          })
          df_matchs = pd.concat([df_matchs, new_m], ignore_index=True)
          st.success(f"Match '{id_match}' créé avec succès !")

        sauvegarder_donnees(df_matchs, df_pronos, df_bonus)
        st.rerun()

  st.subheader("Matchs configurés :")
  st.dataframe(df_matchs, use_container_width=True)

  st.markdown("---")
  st.subheader("3. Calculer les points des matchs de l'appli")
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

          buteurs_pronos_texte = str(
              prono["Buteurs Pronostiqués"]
          ).lower()
          liste_buteurs_pronos = [
              b.strip()
              for b in buteurs_pronos_texte.split(",")
              if b.strip() != ""
          ]

          for b_prono in liste_buteurs_pronos:
            if b_prono in liste_buteurs_reels:
              pts += 3

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

    sauvegarder_donnees(df_matchs, df_pronos, df_bonus)
    st.success(
        f"Calcul terminé ! {compteur_maj} pronostics évalués avec succès."
    )
    st.rerun()