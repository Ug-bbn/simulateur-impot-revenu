import csv
from pathlib import Path

import pytest

from impot import calcul_impot, nombre_parts, revenu_imposable

CAS = list(csv.DictReader(open(Path(__file__).with_name("cas_reference.csv"), encoding="utf-8")))


@pytest.mark.parametrize("cas", CAS, ids=[c["description"] for c in CAS])
def test_cas_reference(cas):
    r = calcul_impot(float(cas["revenu"]), cas["situation"], int(cas["enfants"]))
    assert r["impot_net"] == int(cas["impot_net"])
    assert r["a_payer"] == int(cas["a_payer"])


@pytest.mark.parametrize("situation,enfants,parts", [
    ("celibataire", 0, 1), ("couple", 0, 2), ("couple", 1, 2.5),
    ("couple", 2, 3), ("couple", 3, 4), ("celibataire", 4, 4),
])
def test_parts(situation, enfants, parts):
    assert nombre_parts(situation, enfants) == parts


def test_abattement_min_et_max():
    assert revenu_imposable(4_000) == 4_000 - 509
    assert revenu_imposable(30_000) == 27_000
    assert revenu_imposable(200_000) == 200_000 - 14_555
    assert revenu_imposable(300) == 0  # l'abattement ne dépasse pas le salaire
    assert revenu_imposable(30_000, 30_000) == 54_000  # abattement par salarié


def test_plafonnement_detecte():
    assert calcul_impot(180_000, "couple", 1)["plafonnement_qf"]
    assert not calcul_impot(54_000, "couple", 2)["plafonnement_qf"]


def test_impot_croissant_avec_le_revenu():
    for situation, enfants in [("celibataire", 0), ("couple", 2)]:
        impots = [calcul_impot(r, situation, enfants)["impot_net"] for r in range(0, 300_001, 500)]
        assert impots == sorted(impots)


@pytest.mark.parametrize("args", [(-1,), (1000, "pacse"), (1000, "couple", -1)])
def test_entrees_invalides(args):
    with pytest.raises(ValueError):
        calcul_impot(*args)
