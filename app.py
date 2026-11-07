import pandas as pd
import streamlit as st

from impot import calcul_impot, revenu_imposable

st.set_page_config(page_title="Simulateur impôt sur le revenu 2026", page_icon="🧮")
st.title("Simulateur d'impôt sur le revenu 2026")
st.caption("Revenus 2025 · salariés · barème de la loi de finances pour 2026")

situation = st.radio("Situation", ["celibataire", "couple"], horizontal=True,
                     format_func=lambda s: "Célibataire" if s == "celibataire" else "Marié / pacsé")
enfants = st.number_input("Enfants à charge", 0, 10, 0)
salaires = [st.number_input("Salaire net imposable annuel — déclarant 1 (€)", 0, 2_000_000, 30_000, step=1_000)]
if situation == "couple":
    salaires.append(st.number_input("Salaire net imposable annuel — déclarant 2 (€)", 0, 2_000_000, 30_000, step=1_000))

revenu = revenu_imposable(*salaires)
r = calcul_impot(revenu, situation, enfants)

c1, c2, c3 = st.columns(3)
c1.metric("Impôt à payer", f"{r['a_payer']:,} €".replace(",", " "))
c2.metric("Taux moyen", f"{r['taux_moyen']:.1%}")
c3.metric("Parts", f"{r['parts']:g}")

st.subheader("Détail du calcul")
st.markdown(
    f"- Revenu net imposable (après déduction de 10 %) : **{revenu:,.0f} €**\n"
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

st.subheader("Impôt selon le revenu imposable")
courbe = pd.DataFrame({"Revenu imposable (€)": range(0, 200_001, 2_000)})
courbe["Impôt net (€)"] = [calcul_impot(x, situation, enfants)["impot_net"] for x in courbe["Revenu imposable (€)"]]
st.line_chart(courbe, x="Revenu imposable (€)", y="Impôt net (€)")

st.caption("Simulation indicative. Seuls les salaires sont traités, sans réductions ni crédits d'impôt.")
