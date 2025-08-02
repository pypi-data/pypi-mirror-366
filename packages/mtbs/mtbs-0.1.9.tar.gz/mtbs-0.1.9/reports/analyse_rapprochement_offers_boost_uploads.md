# Analyse de rapprochement : Offers & BOost API ↔ Uploads API

## 🎯 Objectif
Identifier les données communes entre les bases de données "offers" (ID: 48) et "BOost API" (ID: 28) avec "Uploads API" (ID: 13) du système MTBS de BPI France.

## 📊 Vue d'ensemble des bases

### Offers (ID: 48) - Gestion documentaire d'offres
- **5 tables** au total
- Tables principales : documents, audit de documents
- **Tables avec données** :
  - `documents_aud` : 276,361 enregistrements (audit)
  - `documents` : **159,741 enregistrements** ⭐

### BOost API (ID: 28) - Système de dossiers de financement
- **17 tables** au total  
- Tables principales : projets, documents, événements
- **Tables avec données** :
  - `event` : 1,869,720 enregistrements
  - `document` : **759,754 enregistrements** ⭐
  - `project` : **66,535 enregistrements** ⭐

### Uploads API (ID: 13)
- **15 tables** au total
- Système central de gestion documentaire
- **Tables avec données** :
  - `uploaded_file` : **5,009,450 enregistrements**
  - `ged_uploaded_file` : 390,640 enregistrements

## 🔍 Points de connexion découverts

### 1. Base "Offers" ✅

#### Structure de liaison
| Table | Colonne clé | Fonction |
|-------|-------------|----------|
| `documents` | `uploaded_file_id` | Référence vers Uploads API |
| `documents` | `company_id` | Identifiant d'entreprise |

#### Rapprochement confirmé
**Statistiques :**
- **159,741 documents** dans la base Offers
- **100% de correspondance** testée avec Uploads API via `uploaded_file_id`
- **Double traçabilité** : file_id + company_id

**Exemples de rapprochement :**

| Company ID | Document Type | Status | File Name (Uploads) | uploaded_file_id |
|------------|---------------|--------|---------------------|------------------|
| 4930906969 | TAX_REPORT | PENDING | Marius Aurenti - Liasse 2021.pdf | fdb9c32d-6241... |
| 2108123909 | TAX_REPORT | PENDING | CR ex clos le 31 12 2023.pdf | 943aa4e7-7959... |
| 3077148152 | CAPITALIZATION_TABLE | PENDING | Table de capitalisation SOKAMI.pdf | 2d02ff3b-a225... |
| 6632853631 | COMPANY_STATUSES | PENDING | Statuts constitutifs GENARO mis à jour.pdf | d7b931db-8614... |

### 2. Base "BOost API" ✅

#### Structure de liaison
| Table | Colonne clé | Fonction |
|-------|-------------|----------|
| `document` | `file_id` | Référence vers Uploads API |
| `project_search_fields` | `company_siren` | **SIREN des entreprises** ⭐ |

#### Rapprochement confirmé
**Statistiques :**
- **759,754 documents** dans BOost API
- **66,535 projets** avec métadonnées d'entreprises
- **Correspondance testée** avec Uploads API via `file_id`

**Exemples de projets avec SIREN :**

| SIREN | Company Name | Project Holder | Nb Projets | Type Document |
|-------|--------------|----------------|------------|---------------|
| 903533321 | - | pa@bib-batteries.fr | 19 | Documents projet |
| 918340233 | - | bd.intermed@gmail.com | 19 | Documents projet |
| 837663400 | - | yannis@lafare1789.com | 18 | Documents projet |
| 503338105 | - | mayimona.gauthier@gmail.com | 18 | Documents projet |

**Types de fichiers BOost :**
- `identity_first_document` : Pièces d'identité
- `proof_of_address` : Justificatifs de domicile  
- `rib` : Relevés d'identité bancaire
- `network_decision_proof` : Preuves de décision réseau

## 🏗️ Architecture de données

### Schéma de liaison complet

```
Base OFFERS                                      Uploads API
┌─────────────────────┐                        ┌──────────────────────┐
│ documents           │                        │ uploaded_file        │
│ ├─uploaded_file_id  ├───────────────────────►│ ├─id (UUID)          │
│ ├─company_id        │                        │ ├─file_name          │
│ ├─document_type     │                        │ ├─legal_entity_id    │
│ ├─document_status   │                        │ └─...                │
│ └─...               │                        └──────────────────────┘
└─────────────────────┘                                     ▲
                                                            │
Base BOost API                                              │
┌─────────────────────┐    ┌──────────────────────┐        │
│ project             │    │ project_search_fields│        │
│ ├─project_id        ├───►│ ├─company_siren      │        │
│ ├─search_fields_id  │    │ ├─company_name       │        │
│ └─...               │    │ ├─project_holder_*   │        │
└──────────┬──────────┘    │ └─...                │        │
           │               └──────────────────────┘        │
┌──────────▼──────────┐                                    │
│ document            │                                    │
│ ├─file_id           ├────────────────────────────────────┘
│ ├─project_id        │
│ └─...               │
└─────────────────────┘
```

## 📋 Identifiants d'entreprises découverts

### ✅ Base "Offers" - Identifiants trouvés :

| Type d'identifiant | Table | Colonne | Format | Exemple | Utilisation |
|-------------------|-------|---------|---------|---------|-------------|
| **Company ID** | `documents` | `company_id` | 10 chiffres | 4930906969 | Identifiant d'entreprise |
| **Uploaded File ID** | `documents` | `uploaded_file_id` | UUID | fdb9c32d-6241... | Référence fichier |
| **Directory ID** | `documents` | `directory_id` | String | - | Organisation documentaire |

### ✅ Base "BOost API" - Identifiants trouvés :

| Type d'identifiant | Table | Colonne | Format | Exemple | Utilisation |
|-------------------|-------|---------|---------|---------|-------------|
| **SIREN** | `project_search_fields` | `company_siren` | 9 chiffres | 903533321 | **SIREN officiel** ⭐ |
| **Company Name** | `project_search_fields` | `company_name` | String | - | Nom d'entreprise |
| **Project ID** | `project` | `project_id` | Bigint | 504025 | Identifiant projet |
| **File ID** | `document` | `file_id` | UUID | ca865a9d-906f... | Référence fichier |

## 🔑 Clés de rapprochement

### Primary Keys pour jointures

#### Base Offers ↔ Uploads API
1. **Documents** : `documents.uploaded_file_id` = `uploaded_file.id`
2. **Entreprises** : `documents.company_id` = `uploaded_file.legal_entity_id` (potentiel)

#### Base BOost API ↔ Uploads API  
1. **Documents** : `document.file_id` = `uploaded_file.id`
2. **Projets** : `project.project_id` → `project_search_fields` → `company_siren`

### Chaînes relationnelles

**Pour Offers :**
```sql
documents.company_id → Entreprise
documents.uploaded_file_id → uploaded_file.id
```

**Pour BOost API :**
```sql
project.project_search_fields_id → project_search_fields.company_siren
project.project_id → document.project_id → document.file_id → uploaded_file.id
```

## 📈 Statistiques de rapprochement

### Types de documents par base

#### Base "Offers" - Documents d'offres commerciales
- **TAX_REPORT** : Rapports fiscaux
- **CAPITALIZATION_TABLE** : Tables de capitalisation
- **COMPANY_STATUSES** : Statuts d'entreprise
- **Statut** : Principalement PENDING (en attente)

#### Base "BOost API" - Documents de dossiers de financement
- **IDENTITY** : Pièces d'identité des porteurs de projet
- **PROOF_OF_ADDRESS** : Justificatifs de domicile
- **RIB** : Relevés d'identité bancaire
- **NETWORK_DECISION** : Preuves de décision réseau

### Couverture géographique et sectorielle
- **BOost** : 66,535 projets avec SIREN → Couverture nationale
- **Offers** : 159,741 documents → Focus offres commerciales
- **Porteurs de projet** : Emails identifiés pour suivi client

## 🎯 Conclusion

### ✅ Double rapprochement réussi

#### Base "Offers"
- **Liaison directe** avec Uploads API via `uploaded_file_id`
- **Traçabilité entreprise** via `company_id`
- **Documents commerciaux** : Fiscalité, capitalisation, statuts
- **Processus** : Gestion d'offres en cours (PENDING)

#### Base "BOost API" 
- **Liaison directe** avec Uploads API via `file_id`
- **SIREN officiels** disponibles via `project_search_fields`
- **Documents KYC** : Identité, domicile, RIB
- **Processus** : Constitution de dossiers de financement

### 💡 Architecture découverte

1. **Uploads API** = Hub documentaire central pour tous les processus
2. **Offers** = Module commercial avec documents entreprises
3. **BOost** = Module instruction avec documents porteurs de projet
4. **Workflow** : 
   - **Offers** : Prospection → Documents commerciaux → Stockage
   - **BOost** : Instruction → Documents KYC → Stockage

### 🏢 Écosystème BPI France révélé

**Trois publics cibles identifiés :**
1. **Entreprises clientes** (ESG API + Offers) → SIREN, company_id
2. **Porteurs de projet** (BOost API) → SIREN, identité, KYC
3. **Investisseurs particuliers** (Investor Dashboard) → ret_id, codes ISIN

### 📊 Recommandations

#### Exploitation des données
- **Crosselling** : Lier les bases Offers ↔ BOost via SIREN communs
- **Suivi client** : Tracer le parcours Prospect → Client → Financement
- **Analytics** : Analyser les taux de conversion par secteur/région

#### Optimisations techniques
- **Index** : Créer des index sur company_id, company_siren pour performances
- **Consolidation** : Possibilité de vue unifiée des entreprises via SIREN
- **Alertes** : Système d'alertes sur changements de statuts documents

### 🔮 Extensions possibles
- Analyse temporelle : Délais entre dépôt BOost et signature Offers
- Cartographie réseau : Écosystème des partenaires via emails projet
- Scoring : Évaluation automatique des dossiers via historique documentaire
- Reporting : Tableaux de bord unifiés BOost + Offers + ESG par entreprise

---
*Analyse réalisée le 23 juillet 2025 avec le système MTBS MCP*
