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
    # S'assurer que les colonnes Date et Heure existent dans les vieux fichiers CSV
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
    maintenant = datetime.now()
    matchs_disponibles = []

    # On filtre les matchs dont le coup d'envoi n'est PAS encore passé
    for idx, row in df_matchs.iterrows():
      m_id = row["ID Match"]
      date_str = row.get("Date", "2026-01-01")
      heure_str = row.get("Heure", "00:00")
      try:
        coup_envoi = datetime.strptime(
            f"{date_str} {heure_str}", "%Y-%m-%d %H:%M"
        )
        # Le match est dispo si on est AVANT le coup d'envoi ET qu'il n'a pas déjà un score réel validé
        if maintenant < coup_envoi and str(row["Score Réel"]).strip() == "":
          matchs_disponibles.append(m_id)
      except Exception:
        # En cas de format de date invalide par sécurité, on regarde juste si le score n'est pas rentré
        if str(row["Score Réel"]).strip() == "":
          matchs_disponibles.append(m_id)

    if not matchs_disponibles:
      st.warning(
          "🔒 Aucun match n'est ouvert actuellement (le coup d'envoi est passé ou"
          " les matchs sont terminés)."
      )
    else:
      nom_utilisateur = st.text_input("Ton Prénom / Pseudo")
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
        if not nom_utilisateur.strip():
          st.error("⚠️ Tu dois entrer ton prénom ou pseudo !")
        elif not buteurs_selectionnes:
          st.error("⚠️ Tu dois sélectionner au moins un buteur !")
        else:
          # Double vérification de sécurité au moment du clic
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

    sauvegarder_donnees(df_matchs, df_pronos)
    st.success(
        f"Calcul terminé ! {compteur_maj} pronostics évalués avec succès."
    )
    st.rerun()