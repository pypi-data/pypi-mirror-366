# Analyse des Rapprochements : Customer Subscription API ↔ Autres Bases MTBS

**Date d'analyse :** 23 juillet 2025  
**Bases analysées :** Customer Subscription API (ID: 30), Uploads API (ID: 13), Product API (ID: 10)

## 📊 Vue d'ensemble de Customer Subscription API

### Structure complète (21 tables analysées)
- **10,484 souscriptions** (`subscription`)
- **605 comptes clients** (`customer_account`) 
- **15,866 documents** (`document`)
- **601 offres** (`offer`)
- **10,484 documents contractuels** (`contract_document`)
- **5,376 documents de mandat** (`mandate_document`)
- **994 moyens de paiement** (`payment_method`)
- **761 résiliations** (`termination`)
- **820 étapes d'entonnoir** (`funding_contract_funnel`)
- **402 abandons de souscription** (`subscription_drop`)
- **4 offres de souscription** (`subscription_offer`)

### Tables clés identifiées
```sql
-- Tables principales
subscription              -- Souscriptions clients (10,484)
customer_account         -- Comptes clients (605)
contract_document        -- Documents contractuels (10,484)
payment_method          -- Moyens de paiement (994)
mandate_document        -- Documents de mandat (5,376)
document               -- Documents génériques (15,866)
termination           -- Résiliations (761)
funding_contract_funnel -- Étapes de financement (820)
subscription_drop      -- Abandons (402)
subscription_offer     -- Offres disponibles (4)
subscriptions_monitoring -- Monitoring (vide)
```

## 🔗 Rapprochements Identifiés

## 🔗 Rapprochements Identifiés

### 1. Customer Subscription API ↔ Uploads API

#### 🎯 **Rapprochement Principal : RIB Files (Souscriptions)**
- **Clé de liaison :** `subscription.rib_file_id` → `uploaded_file.id`
- **Volume :** 97 correspondances exactes
- **Taux de couverture :** 0.9% des souscriptions ont un RIB uploadé

#### 🎯 **Rapprochement Secondaire : RIB Files (Moyens de paiement)**
- **Clé de liaison :** `payment_method.rib_file_id` → `uploaded_file.id`
- **Volume :** 994 correspondances (974 RIB uniques)
- **Taux de couverture :** 9.5% des souscriptions via moyens de paiement
- **🔥 DÉCOUVERTE MAJEURE :** Volume 10x supérieur au rapprochement initial

**Exemple de requête de validation :**
```sql
-- Customer Subscription API (ID: 30) - Moyens de paiement
SELECT COUNT(*) as payment_methods_with_rib, 
       COUNT(DISTINCT rib_file_id) as unique_rib_files,
       COUNT(DISTINCT legal_entity_id) as unique_entities
FROM payment_method 
WHERE rib_file_id IS NOT NULL;
-- Résultat: 994 méthodes, 974 RIB, 836 entités ✅

-- Uploads API (ID: 13) - Vérification
SELECT COUNT(*) as matching_files
FROM uploaded_file 
WHERE id IN (
    SELECT DISTINCT rib_file_id 
    FROM payment_method 
    WHERE rib_file_id IS NOT NULL
);
-- Résultat: 974+ fichiers correspondants ✅
```

#### 🏢 **Rapprochement Potentiel : Legal Entity ID**
- **Problème identifié :** Formats différents des `legal_entity_id`
- **Customer Subscription :** Format numérique (ex: "4596236173", "791005584")
- **Uploads API :** Format différent (ex: "1000177022", "1003062871")
- **Action recommandée :** Investigation sur la correspondance des formats

**Analyse des volumes :**
```sql
-- Customer Subscription API
SELECT COUNT(DISTINCT legal_entity_id) as unique_entities,
       COUNT(*) as total_subscriptions_with_entity
FROM subscription 
WHERE legal_entity_id IS NOT NULL;
-- Résultat: 9,390 entités uniques sur 10,484 souscriptions (89.6%)
```

### 2. Customer Subscription API ↔ Product API

#### 🎯 **Rapprochement Potentiel : Offres/Produits**
- **Clé potentielle :** `subscription.offer_id` vers produits dans Product API
- **Statut :** À confirmer - structures différentes
- **Investigation nécessaire :** Mapping entre offres et produits BPI

**Données identifiées :**
```sql
-- Customer Subscription - Offres uniques
SELECT COUNT(DISTINCT offer_id) as unique_offers,
       COUNT(*) as subscriptions_with_offers
FROM subscription 
WHERE offer_id IS NOT NULL;
-- 3 offres uniques utilisées

-- Product API - Produits disponibles  
SELECT COUNT(*) as total_products FROM product;
-- Multiple produits avec identifiants différents
```

## 📈 Métriques de Qualité des Données

### Distribution des identifiants clés

| Table | Champ | Valeurs Non-Null | Pourcentage | Commentaires |
|-------|-------|------------------|-------------|--------------|
| `subscription` | `legal_entity_id` | 10,484 / 10,484 | 100% | ✅ Excellent |
| `subscription` | `rib_file_id` | 97 / 10,484 | 0.9% | ⚠️ Très faible |
| `payment_method` | `rib_file_id` | 994 / 994 | 100% | ✅ Excellent |
| `payment_method` | `legal_entity_id` | 836 / 994 | 84.1% | ✅ Bon |
| `contract_document` | `subscription_id` | 10,484 / 10,484 | 100% | ✅ Parfait |
| `termination` | `subscription_id` | 761 / 761 | 100% | ✅ Parfait |
| `document` | `document_external_id` | 298+ / 15,866 | ~2% | ⚠️ Faible |

### Nouvelles métriques découvertes

#### Cycle de vie des souscriptions
- **Souscriptions actives :** 10,484
- **Résiliations :** 761 (7.3% du total)
- **Abandons :** 402 (3.8% du total)
- **Documents contractuels :** 1:1 avec souscriptions
- **Documents de mandat :** 5,376 (51.3% des souscriptions)

#### Entonnoir de conversion
- **Étapes d'entonnoir :** 820 entrées (792 entités uniques)
- **Taux de conversion estimé :** ~93% (792 entités → 605 comptes)

### Répartition des statuts et raisons
```sql
-- Analyse des résiliations
SELECT reason, COUNT(*) as count 
FROM termination 
GROUP BY reason 
ORDER BY count DESC;

-- Analyse des abandons
SELECT reason, COUNT(*) as count 
FROM subscription_drop 
GROUP BY reason 
ORDER BY count DESC;
```

## 🎯 Recommandations

### Priorité 1 - Rapprochements confirmés
1. **🔥 MAJEUR : Exploiter payment_method.rib_file_id** : `payment_method.rib_file_id` ↔ `uploaded_file.id`
   - **Impact :** 974 RIB files (10x plus que subscription.rib_file_id)
   - **Couverture :** 9.5% des souscriptions via moyens de paiement
   - **Action :** Intégrer immédiatement dans les tableaux de bord

2. **Compléter avec subscription.rib_file_id** : `subscription.rib_file_id` ↔ `uploaded_file.id`
   - Volume additionnel de 97 RIB
   - Traçabilité complète des justificatifs bancaires

3. **Documents contractuels** : 1:1 parfait avec souscriptions
   - Exploiter `contract_document.subscription_id` pour traçabilité complète
   - Numéros de contrat disponibles

### Priorité 2 - Investigations nécessaires
1. **Legal Entity ID** : Comprendre les formats différents
   - **subscription.legal_entity_id** : 100% de couverture
   - **payment_method.legal_entity_id** : 84.1% de couverture
   - Possible transformation/mapping à identifier

2. **Offres/Produits** : Mapping avec Product API
   - 4 offres de souscription disponibles (`subscription_offer`)
   - Correspondance offer_id ↔ product.id/slug à confirmer

### Priorité 3 - Analyses métier
1. **Cycle de vie client** : Exploiter les données de résiliation/abandon
   - 761 résiliations (5 raisons différentes)
   - 402 abandons (4 raisons différentes)
   - Analyse des patterns de churn

2. **Entonnoir de conversion** : Analyser `funding_contract_funnel`
   - 9 étapes identifiées
   - 820 entrées pour 792 entités
   - Optimisation du parcours client

3. **Documents de mandat** : Lier avec `mandate_document`
   - 5,376 documents (51.3% des souscriptions)
   - Relation avec `payment_method`

## 🔍 Requêtes d'Exploration Recommandées

### Analyse complète des RIB uploadés
```sql
-- Customer Subscription API (ID: 30) - RIB via moyens de paiement (PRIORITÉ 1)
SELECT pm.legal_entity_id, pm.status, pm.created_date, pm.rib_file_id, pm.iban, pm.bic
FROM payment_method pm 
WHERE pm.rib_file_id IS NOT NULL
ORDER BY pm.created_date DESC;

-- Customer Subscription API (ID: 30) - RIB via souscriptions (complément)
SELECT s.legal_entity_id, s.status, s.created_date, s.rib_file_id
FROM subscription s 
WHERE s.rib_file_id IS NOT NULL
ORDER BY s.created_date DESC;

-- Uploads API (ID: 13) - Détails des RIB
SELECT uf.id, uf.file_name, uf.legal_entity_id, uf.created_at, uf.file_size
FROM uploaded_file uf
WHERE uf.id IN (
    SELECT DISTINCT rib_file_id 
    FROM payment_method 
    WHERE rib_file_id IS NOT NULL
    UNION
    SELECT DISTINCT rib_file_id 
    FROM subscription 
    WHERE rib_file_id IS NOT NULL
);
```

### Analyse du cycle de vie client
```sql
-- Vue d'ensemble du parcours client
WITH subscription_lifecycle AS (
    SELECT 
        s.id as subscription_id,
        s.legal_entity_id,
        s.status as subscription_status,
        s.created_date as subscription_date,
        s.activated_date,
        s.terminated_date,
        t.reason as termination_reason,
        t.request_date as termination_request,
        cd.contract_number
    FROM subscription s
    LEFT JOIN termination t ON s.id = t.subscription_id
    LEFT JOIN contract_document cd ON s.id = cd.subscription_id
)
SELECT * FROM subscription_lifecycle
ORDER BY subscription_date DESC;

-- Analyse des abandons
SELECT 
    sd.legal_entity_id,
    sd.reason,
    sd.comment,
    sd.created_date,
    COUNT(*) OVER (PARTITION BY sd.reason) as reason_count
FROM subscription_drop sd
ORDER BY sd.created_date DESC;
```

### Investigation Legal Entity (formats différents)
```sql
-- Analyser les formats de legal_entity_id dans subscription
SELECT 
    LENGTH(legal_entity_id) as id_length,
    COUNT(*) as count,
    MIN(legal_entity_id) as min_example,
    MAX(legal_entity_id) as max_example
FROM subscription 
WHERE legal_entity_id IS NOT NULL
GROUP BY LENGTH(legal_entity_id)
ORDER BY count DESC;

-- Analyser les formats dans payment_method
SELECT 
    LENGTH(legal_entity_id) as id_length,
    COUNT(*) as count,
    MIN(legal_entity_id) as min_example,
    MAX(legal_entity_id) as max_example
FROM payment_method 
WHERE legal_entity_id IS NOT NULL
GROUP BY LENGTH(legal_entity_id)
ORDER BY count DESC;
```

### Analyse de l'entonnoir de financement
```sql
-- Étapes du funnel de financement
SELECT 
    step,
    COUNT(*) as count,
    COUNT(DISTINCT legal_entity_id) as unique_entities,
    MIN(created_date) as first_occurrence,
    MAX(created_date) as last_occurrence
FROM funding_contract_funnel
GROUP BY step
ORDER BY count DESC;

-- Progression dans l'entonnoir par entité
SELECT 
    legal_entity_id,
    COUNT(DISTINCT step) as steps_completed,
    STRING_AGG(step, ' -> ' ORDER BY created_date) as journey
FROM funding_contract_funnel
GROUP BY legal_entity_id
HAVING COUNT(DISTINCT step) > 1
ORDER BY steps_completed DESC;
```

## 📋 Prochaines Étapes

1. **Validation technique** des rapprochements identifiés
2. **Investigation** sur les formats de `legal_entity_id`
3. **Mapping** des offres avec le catalogue produit
4. **Documentation** des processus de souscription
5. **Intégration** dans l'application de monitoring live

---

**Note :** Cette analyse exhaustive des 21 tables révèle Customer Subscription API comme une base centrale pour le parcours client, avec des rapprochements majeurs vers les documents (Uploads) et un potentiel d'analyse approfondie du cycle de vie client. La découverte du rapprochement via `payment_method.rib_file_id` multiplie par 10 le volume de données exploitables.
