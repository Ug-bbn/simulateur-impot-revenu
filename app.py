import altair as alt
import pandas as pd
import streamlit as st

from impot import calcul_impot, revenu_imposable

st.set_page_config(page_title="Simulateur impôt sur le revenu 2026", page_icon="🧮")
st.title("Simulateur d'impôt sur le revenu 2026")
st.caption("Revenus 2025 · salariés · barème de la loi de finances pour 2026")

situation = st.radio("Situation", ["celibataire", "couple"], horizontal=True,
                     format_func=lambda s: "Célibataire" if s == "celibataire" else "Marié / pacsé")
enfants = st.number_input("Enfants à charge", 0, 10, 0)
saisie = st.radio(
    "Je saisis", ["salaires", "revenu"], horizontal=True,
    format_func=lambda s: "Mes salaires (fiche de paie / case 1AJ)" if s == "salaires"
    else "Mon revenu net imposable (déjà après déduction des 10 %)",
    help="Le « net imposable » de la fiche de paie est AVANT la déduction de 10 %. "
         "Le « revenu net imposable » de l'avis d'impôt (et de nombreux simulateurs) est APRÈS.",
)
if saisie == "salaires":
    salaires = [st.number_input("Salaire net imposable annuel — déclarant 1 (€)", 0, 2_000_000, 30_000, step=1_000)]
    if situation == "couple":
        salaires.append(st.number_input("Salaire net imposable annuel — déclarant 2 (€)", 0, 2_000_000, 30_000, step=1_000))
    revenu = revenu_imposable(*salaires)
    revenus_percus = sum(salaires)  # la déduction de 10 % est fiscale : l'argent perçu reste le salaire
else:
    revenu = revenus_percus = st.number_input("Revenu net imposable du foyer (€)", 0, 4_000_000, 27_000, step=1_000)
r = calcul_impot(revenu, situation, enfants)

c1, c2, c3 = st.columns(3)
c1.metric("Impôt à payer", f"{r['a_payer']:,} €".replace(",", " "))
c2.metric("Taux moyen", f"{r['taux_moyen']:.2%}")
c3.metric("Parts", f"{r['parts']:g}")

st.subheader("Détail du calcul")
st.markdown(
    f"- Revenu net imposable (base du barème) : **{revenu:,.0f} €**\n"
    f"- Impôt brut : **{r['impot_brut']:,.0f} €**"
    + (" (plafonnement du quotient familial appliqué)" if r["plafonnement_qf"] else "") + "\n"
    f"- Décote : **{r['decote']:,.0f} €**\n"
    f"- Impôt net : **{r['impot_net']:,} €**"
    + (" — inférieur à 61 €, non mis en recouvrement" if r["impot_net"] and not r["a_payer"] else "")
)
st.dataframe(
    pd.DataFrame(r["tranches"], columns=["Montant par part (€)", "Taux", "Impôt par part (€)"])
    .style.format({"Montant par part (€)": "{:,.0f}", "Taux": "{:.0%}", "Impôt par part (€)": "{:,.0f}"}),
    hide_index=True,
)

st.subheader("Pression fiscale")
if revenus_percus:
    parts_revenu = pd.DataFrame({
        "Part": ["Revenu disponible", "Impôt sur le revenu"],
        "Montant": [revenus_percus - r["a_payer"], r["a_payer"]],
    })
    parts_revenu["Libellé"] = parts_revenu["Montant"].map(lambda m: f"{m:,.0f} €".replace(",", " "))
    base = alt.Chart(parts_revenu).encode(
        theta=alt.Theta("Montant:Q", stack=True),
        color=alt.Color("Part:N", scale=alt.Scale(range=["#1f3a93", "#f5b700"]), legend=alt.Legend(title=None)),
        tooltip=["Part", "Libellé"],
    )
    st.altair_chart(
        base.mark_arc(innerRadius=70, outerRadius=120)
        + base.mark_text(radius=145, size=14).encode(text="Libellé:N"),
        width="stretch",
    )

st.caption("Simulation indicative. Seuls les salaires sont traités, sans réductions ni crédits d'impôt.")
