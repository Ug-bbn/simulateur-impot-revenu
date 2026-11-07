"""Calcul de l'impôt sur le revenu 2026 (revenus 2025) pour des salariés.

Paramètres : loi de finances pour 2026 (barème revalorisé de 0,9 %) et
aide-mémoire DGFiP 2026 pour la déduction forfaitaire de 10 %.
"""

# Tranches par part : (borne haute, taux). None = pas de borne.
BAREME = [(11_600, 0.0), (29_579, 0.11), (84_577, 0.30), (181_917, 0.41), (None, 0.45)]
PLAFOND_DEMI_PART = 1_807  # avantage max par demi-part de quotient familial
DECOTE = {"celibataire": (1_982, 897), "couple": (3_277, 1_483)}  # (seuil impôt brut, forfait)
TAUX_DECOTE = 0.4525
ABATTEMENT_MIN, ABATTEMENT_MAX = 509, 14_555  # déduction de 10 %, par salarié
SEUIL_RECOUVREMENT = 61  # en dessous, l'impôt n'est pas mis en recouvrement


def revenu_imposable(*salaires: float) -> float:
    """Somme des salaires après déduction forfaitaire de 10 % appliquée à chacun."""
    total = 0.0
    for s in salaires:
        if s < 0:
            raise ValueError("salaire négatif")
        if s > 0:
            total += s - min(max(s * 0.10, ABATTEMENT_MIN), ABATTEMENT_MAX, s)
    return total


def nombre_parts(situation: str, enfants: int) -> float:
    # shortcut: pas de cas particuliers (parent isolé, invalidité, ancien combattant) ; à ajouter si un client en a besoin
    if situation not in DECOTE:
        raise ValueError(f"situation inconnue : {situation}")
    if enfants < 0:
        raise ValueError("nombre d'enfants négatif")
    base = 1 if situation == "celibataire" else 2
    return base + 0.5 * min(enfants, 2) + max(enfants - 2, 0)


def bareme(quotient: float) -> list[tuple[float, float, float]]:
    """Détail par tranche pour une part : (montant dans la tranche, taux, impôt)."""
    detail, bas = [], 0.0
    for haut, taux in BAREME:
        dans_tranche = max(0.0, (quotient if haut is None else min(quotient, haut)) - bas)
        detail.append((dans_tranche, taux, dans_tranche * taux))
        if haut is None or quotient <= haut:
            break
        bas = haut
    return detail


def _impot_parts(revenu: float, parts: float) -> float:
    return parts * sum(i for _, _, i in bareme(revenu / parts))


def calcul_impot(revenu: float, situation: str = "celibataire", enfants: int = 0) -> dict:
    """Impôt dû sur un revenu net imposable, avec le détail de chaque étape."""
    if revenu < 0:
        raise ValueError("revenu négatif")
    parts = nombre_parts(situation, enfants)
    parts_base = 1 if situation == "celibataire" else 2

    avec_qf = _impot_parts(revenu, parts)
    sans_qf = _impot_parts(revenu, parts_base)
    plafond = PLAFOND_DEMI_PART * (parts - parts_base) * 2
    brut = max(avec_qf, sans_qf - plafond)

    seuil, forfait = DECOTE[situation]
    decote = min(max(forfait - TAUX_DECOTE * brut, 0), brut) if brut < seuil else 0.0
    net = round(brut - decote)

    return {
        "revenu": revenu,
        "parts": parts,
        "impot_brut": round(brut, 2),
        "plafonnement_qf": brut > avec_qf,
        "decote": round(decote, 2),
        "impot_net": net,
        "a_payer": net if net >= SEUIL_RECOUVREMENT else 0,
        "taux_moyen": net / revenu if revenu else 0.0,
        "tranches": bareme(revenu / parts),
    }
