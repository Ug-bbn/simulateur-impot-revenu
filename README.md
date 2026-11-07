# Simulateur d'impôt sur le revenu 2026

![tests](https://github.com/Ug-bbn/simulateur-impot-revenu/actions/workflows/tests.yml/badge.svg)

> 🇬🇧 *A French income-tax calculator (2026 rules) in Python: fully tested business logic and an interactive Streamlit app. It shows how I turn written regulations into reliable, tested code.*

## Le problème

Les règles de calcul métier (fiscalité, retraite, paie, primes) vivent souvent dans des fichiers Excel que personne n'ose modifier. Les formules sont difficiles à relire et ne sont jamais testées. Une erreur passe inaperçue jusqu'au jour où un client ou un contrôleur la découvre.

## La solution

Ce projet traduit les règles officielles de l'impôt sur le revenu en un code Python **lisible et testé** :

- les paramètres officiels sont regroupés en tête de `impot.py` : barème, plafonnement du quotient familial, décote, déduction de 10 %, seuil de recouvrement ;
- chaque étape du calcul est exposée, et l'application l'affiche ;
- des **cas de référence** sont listés dans un simple CSV (`tests/cas_reference.csv`) et vérifiés automatiquement à chaque modification (pytest + GitHub Actions). Pour ajouter un cas, il suffit d'ajouter une ligne, sans écrire de code ;
- des tests de propriétés complètent ces cas : par exemple, l'impôt ne diminue jamais quand le revenu augmente.

C'est la même démarche que j'ai appliquée à la Direction de la Sécurité sociale : un module de calcul actuariel sur 12 caisses de retraite, dont les tests étaient vérifiés contre un simulateur officiel.

## Lancer le projet

```bash
pip install -r requirements.txt
streamlit run app.py   # l'application
pytest                 # les tests
```

## Règles couvertes

| Règle | Valeur (revenus 2025) |
|---|---|
| Barème par part | 0 % / 11 % / 30 % / 41 % / 45 %, seuils 11 600 · 29 579 · 84 577 · 181 917 € |
| Déduction forfaitaire de 10 % (par salarié) | min 509 €, max 14 555 € |
| Quotient familial | ½ part par enfant pour les deux premiers, 1 part à partir du 3ᵉ, avantage plafonné à 1 807 € par ½ part |
| Décote | 897 € − 45,25 % × impôt (célibataire), 1 483 € − 45,25 % × impôt (couple) |
| Seuil de recouvrement | 61 € |

**Attention aux termes :** le « net imposable » d'une fiche de paie est le montant *avant* la déduction de 10 %. Le « revenu net imposable » d'un avis d'impôt est le montant *après*. L'application demande lequel on saisit, et la colonne `revenu` de `tests/cas_reference.csv` désigne toujours le revenu après déduction. Un cas est recoupé avec le simulateur de Boursorama (45 000 €, célibataire : 6 604 €, résultat identique).

**Hors périmètre :** revenus autres que les salaires, parent isolé (case T) et autres demi-parts spécifiques, réductions et crédits d'impôt, contribution sur les hauts revenus.

## Sources

- [Barème IR 2026, quotient familial et décote — Légifiscal](https://www.legifiscal.fr/actualites-fiscales/4474-ir-bareme-2026-quotient-familial-decote.html)
- [Aide-mémoire impôt sur le revenu 2026 — DGFiP](https://www.impots.gouv.fr/www2/fichiers/documentation/brochure/ir_2026/pdf_som/aide_memoire.pdf)

---
Hugues Barbier, data scientist Python freelance : automatisation Excel, ETL et fiabilisation de données.
