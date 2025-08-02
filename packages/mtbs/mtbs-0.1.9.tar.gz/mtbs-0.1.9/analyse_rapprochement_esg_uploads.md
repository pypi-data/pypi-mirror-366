# Analyse de rapprochement : ESG API ↔ Uploads API

## 🎯 Objectif
Identifier les données communes entre les bases de données "ESG API" (ID: 34) et "Uploads API" (ID: 13) du système MTBS de BPI France.

## 📊 Vue d'ensemble des bases

### ESG API (ID: 34)
- **28 tables** au total
- Tables principales : évaluations ESG, analyses, rapports, gestion des fichiers
- **Tables avec données** :
  - `form_response_model` : 444,690 enregistrements
  - `insight_model` : 140,265 enregistrements  
  - `analysed_scope_model` : 109,372 enregistrements
  - `rating_model` : 30,072 enregistrements
  - `evaluation_model` : 10,710 enregistrements
  - `report_model` : **10,024 enregistrements** ⭐
  - `analysis_model` : 10,018 enregistrements
  - `company_information_model` : 9,953 enregistrements

### Uploads API (ID: 13)
- **15 tables** au total
- Système central de gestion documentaire
- **Tables avec données** :
  - `uploaded_file` : **5,009,450 enregistrements**
  - `uploaded_file_user` : 4,894,985 enregistrements
  - `ged_uploaded_file` : **390,640 enregistrements**

## 🔍 Analyse des structures communes

### Tables avec structure identique
| Table | ESG API | Uploads API | Structure |
|-------|---------|-------------|-----------|
| `uploaded_file` | 0 enregistrements | 5,009,450 | ✅ 100% identique (10 colonnes) |
| `uploaded_file_user` | 0 enregistrements | 4,894,985 | ✅ 100% identique (4 colonnes) |
| `ged_uploaded_file` | 0 enregistrements | 390,640 | ⚠️ Partielle (6/9 colonnes communes) |
| `ged_permission_rules` | - | - | ✅ Structure identique |
| `ged_product_mapping` | - | - | ✅ Structure identique |

### Conclusion structure
❌ **Pas de rapprochement possible au niveau des tables de gestion de fichiers** : toutes vides dans ESG API.

## 🎯 Découverte du rapprochement de données

### Point de connexion trouvé : `report_model`

La table `report_model` d'ESG API contient des références vers les fichiers d'Uploads API :

```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'report_model' 
AND (column_name LIKE '%upload%' OR column_name LIKE '%file%');
```

**Colonnes clés identifiées :**
- `upload_api_id` : Référence vers `uploaded_file.id`
- `upload_ged_id` : Référence vers `ged_uploaded_file.file_id`

## ✅ Rapprochement confirmé

### Statistiques du rapprochement
- **10,024 rapports ESG** dans `report_model`
- **100% des rapports** ont des références vers Uploads API
- **Double référencement** systématique : `upload_api_id` + `upload_ged_id`
- **100% des rapports** sont liés à une entreprise spécifique (SIREN)

### Schéma de liaison complet
```
ESG API - Chaîne relationnelle                    Uploads API
┌─────────────────────┐                          ┌──────────────────────┐
│ company_information │                          │ uploaded_file        │
│ ├─id (UUID)         │                          │ ├─id (UUID)          │
│ ├─company_name      │                          │ ├─file_name          │
│ ├─siren             │                          │ ├─creation_date      │
│ ├─company_id        │                          │ └─...                │
│ └─...               │                          └──────────────────────┘
└──────────┬──────────┘                                     ▲
           │                                                │
┌──────────▼──────────┐                                     │
│ evaluation_model    │                                     │
│ ├─id (UUID)         │                                     │
│ ├─company_info_id   │                                     │
│ ├─sector            │                                     │
│ ├─company_size      │                                     │
│ └─...               │                                     │
└──────────┬──────────┘                                     │
           │                                                │
┌──────────▼──────────┐                                     │
│ analysis_model      │                                     │
│ ├─id (UUID)         │                                     │
│ ├─evaluation_id     │                                     │
│ └─...               │                                     │
└──────────┬──────────┘                                     │
           │                                                │
┌──────────▼──────────┐                                     │
│ report_model        │                                     │
│ ├─analysis_id       │                                     │
│ ├─upload_api_id     ├─────────────────────────────────────┘
│ ├─upload_ged_id     ├───┐
│ └─...               │   │
└─────────────────────┘   │          ┌──────────────────────┐
                          │          │ ged_uploaded_file    │
                          └─────────►│ ├─file_id (UUID)     │
                                     │ ├─filename           │
                                     │ ├─creation_date      │
                                     │ ├─file_size          │
                                     │ └─...                │
                                     └──────────────────────┘
```

## 📋 Exemples concrets de rapprochement

### Échantillon de fichiers liés avec entreprises

| Entreprise | SIREN | Secteur | Taille | Fichier PDF | upload_api_id | Statut |
|------------|-------|---------|--------|-------------|---------------|---------|
| **PROCOLOR** | 399540780 | Métaux/Matériaux | PME | `Bilan IMC PROCOLOR.pdf` | b108f20d-be81... | ✅ |
| **SOCIETE TOPOGRAPHIE INFORMATIQUE** | 399178565 | Bureau études | PME | `Bilan IMC SOCIETE TOPO.pdf` | 1ec159b7-4ded... | ✅ |
| **WORLD GAME** | 892207242 | Numérique/Software | STARTUP | `Bilan IMC WORLD GAME.pdf` | b6ca9a04-fc18... | ✅ |
| **APPLICA. PLASTIQUES THERMOFORMES** | 342281458 | Caoutchouc/Plastique | PME | `Bilan IMC APPLICA. PLA.pdf` | e87ce449-c314... | ✅ |
| **SOC BERRUYERE DESAMIANTAGE** | 478828684 | BTP | PME | `Bilan IMC SOC BERRU.pdf` | d6f85e46-4266... | ✅ |

### Détails des correspondances
- **Nomenclature** : `Bilan IMC [NOM_ENTREPRISE].pdf`
- **Type** : Bilans IMC (Impact Management & Measurement)
- **Format** : PDF
- **Période** : 2023-2025
- **Taille** : 367-604 KB
- **Traçabilité** : Nom entreprise dans le fichier = Nom dans company_information_model

### Chaîne de liaison entreprise → fichier
```sql
-- Requête complète de rapprochement
SELECT 
  c.company_name,
  c.siren,
  e.sector,
  e.company_size,
  uf.file_name,
  uf.creation_date,
  r.upload_api_id
FROM report_model r
LEFT JOIN analysis_model a ON r.analysis_id = a.id
LEFT JOIN evaluation_model e ON a.evaluation_id = e.id  
LEFT JOIN company_information_model c ON e.company_information_id = c.id
LEFT JOIN uploaded_file uf ON r.upload_api_id = uf.id (via Uploads API)
```

## 🔑 Clés de rapprochement

### Primary Keys pour jointures
1. **ESG → Uploads** : `report_model.upload_api_id` = `uploaded_file.id`
2. **ESG → Uploads GED** : `report_model.upload_ged_id` = `ged_uploaded_file.file_id`

### Chaîne relationnelle complète dans ESG API
```sql
report_model.analysis_id → analysis_model.id
analysis_model.evaluation_id → evaluation_model.id
evaluation_model.company_information_id → company_information_model.id
```

### Identifiants d'entreprise disponibles
- **SIREN** dans `company_information_model` : 907605752, 969202241, etc.
- **company_id** dans `company_information_model` : 8773991295, 1215149887, etc.
- **company_name** : Noms d'entreprises complets
- **Métadonnées sectorielles** : sector, company_size (PME, STARTUP, etc.)

### Corrélations métier découvertes
- **Nomenclature fichier** : "Bilan IMC [NOM_ENTREPRISE].pdf"  
- **Cohérence temporelle** : Dates de création alignées avec les évaluations
- **Secteurs diversifiés** : BTP, Numérique, Métaux, Conseil, etc.

## 🎯 Conclusion

### ✅ Rapprochement réussi
- **10,024 rapports ESG** sont directement liés aux fichiers stockés dans Uploads API
- **Double référencement** garantit la traçabilité complète (`upload_api_id` + `upload_ged_id`)
- **100% des rapports** sont liés à des entreprises spécifiques via SIREN
- **Cohérence des données** : tous les IDs de référence trouvés dans Uploads API
- **Nomenclature cohérente** : noms d'entreprises dans les fichiers PDF

### 💡 Architecture découverte
1. **Uploads API** = Système central de stockage de fichiers
2. **ESG API** = Système métier qui référence les fichiers via des UUID
3. **Chaîne métier** : Entreprise → Évaluation ESG → Analyse → Rapport → Fichier PDF
4. **Workflow** : Upload → Stockage → Référencement dans rapports ESG → Liaison entreprise

### 🏢 Typologie des entreprises analysées
- **Tailles** : PME, Startups principalement
- **Secteurs** : BTP, Numérique/Software, Métaux/Matériaux, Bureau d'études, Plastique/Caoutchouc
- **Géographie** : Couverture nationale via les centres de mesure régionaux
- **Documents** : Bilans IMC (Impact Management & Measurement) au format PDF

### 📈 Recommandations
- Utiliser `report_model` comme table de liaison principale
- Les jointures sur UUID garantissent l'unicité et la performance
- Exploitation possible des SIREN pour rapprochements avec systèmes externes
- Extension possible de l'analyse aux autres métadonnées sectorielles (sector, company_size)
- Potentiel d'analyse temporelle via les dates de création des évaluations

---
*Analyse réalisée le 23 juillet 2025 avec le système MTBS MCP*
