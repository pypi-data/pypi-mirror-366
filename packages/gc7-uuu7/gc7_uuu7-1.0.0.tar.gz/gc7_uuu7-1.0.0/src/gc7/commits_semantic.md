### 📦 Version SemVer : MAJOR.MINOR.PATCH

| Type de changement          | Préfixe anglais           | Traduction française                               | Incrément                       |
|-----------------------------|---------------------------|----------------------------------------------------|---------------------------------|
| 🧨 Rupture de compatibilité | `BREAKING CHANGE:` ou `!` | Changement majeur (rupture API, suppression, etc.) | **MAJOR** (ex: `1.2.3 → 2.0.0`) |
| ✨ Nouvelle fonctionnalité   | `feat:`                   | Fonctionnalité (ajout sans rupture)                | **MINOR** (ex: `1.2.3 → 1.3.0`) |
| 🐛 Correction de bug        | `fix:`                    | Correction (bug, typo, etc.)                       | **PATCH** (ex: `1.2.3 → 1.2.4`) |


### 🧠 Autres types de commits (ne changent pas la version)

| Préfixe anglais | Traduction française           | Impact sur version                                          |
|-----------------|--------------------------------|-------------------------------------------------------------|
| `docs:`         | Documentation                  | Aucun                                                       |
| `style:`        | Formatage (indentation, etc.)  | Aucun                                                       |
| `refactor:`     | Refactorisation                | Aucun                                                       |
| `perf:`         | Optimisation de performance    | Aucun                                                       |
| `test:`         | Ajout ou modification de tests | Aucun                                                       |
| `chore:`        | Tâches diverses                | Aucun                                                       |
| `ci:`           | Intégration continue           | Aucun                                                       |
| `build:`        | Configuration de build         | Aucun                                                       |
| `revert:`       | Annulation d’un commit         | Aucun (sauf si le commit annulé était un `feat:` ou `fix:`) |
