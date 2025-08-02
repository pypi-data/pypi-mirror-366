# Plan d'Enrichissement des Données - uploaded_file

## 🎯 Objectif

Rechercher dans toutes les bases de données MTBS des UUIDs de documents présents dans la table `uploaded_file` de l'API Uploads, et pour chaque UUID trouvé, identifier son propriétaire via :
- `company_id`
- `directory_id` 
- `legal_entity_id`
- `siren`
- `ret_id`

**But final** : Mettre à jour les champs `legal_entity_id` et `directory_id` dans `uploaded_file` pour améliorer la traçabilité.

## 📊 État Actuel de uploaded_file

- **Total de fichiers** : 5 017 941
- **Avec legal_entity_id** : 32 552 (0,65%)
- **Avec directory_id** : 806 (0,02%)
- **Sans propriétaire** : 4 984 584 (99,33%)

## 🔍 Méthodologie d'Analyse

### Phase 1 : Identification des Sources d'UUIDs
Analyser chaque base MTBS pour identifier :
1. Tables contenant des colonnes UUID/file_id
2. Tables avec des références de documents  
3. Tables avec des identifiants d'entité (company_id, legal_entity_id, etc.)

### Phase 2 : Extraction et Correspondance
Pour chaque source identifiée :
1. Extraire les UUIDs de documents
2. Vérifier leur présence dans `uploaded_file`
3. Récupérer les identifiants de propriétaire associés

### Phase 3 : Validation et Mise à Jour
1. Valider la cohérence des correspondances
2. Proposer les mises à jour de `legal_entity_id`/`directory_id`
3. Estimer l'impact de l'enrichissement

## 🗄️ Bases de Données à Analyser

### Priorité Haute (APIs de Documents)
- [ ] **Subscription API (5)** - provided_info avec 2,3M UUIDs
- [ ] **Customer Subscription API (30)** - payment_method.rib_file_id
- [ ] **Customer Documents API (51)** - Documents clients
- [ ] **OCR API (33)** - Documents traités OCR
- [ ] **Checklist API (15)** - Documents de vérification

### Priorité Moyenne (APIs Métier)
- [ ] **Decision API (40)** - Documents de décision
- [ ] **Contract API (2)** - Documents contractuels
- [ ] **Compliance API (50)** - Documents de conformité
- [ ] **Risk API (17)** - Documents d'évaluation risque
- [ ] **Fraud Detection API (18)** - Documents d'analyse fraude

### Priorité Basse (APIs Support)
- [ ] **Workflow API (6)** - Documents de processus
- [ ] **Messaging API (8)** - Pièces jointes
- [ ] **Secure Space (44)** - Documents sécurisés
- [ ] **Autres APIs** - Analyse au cas par cas

## 📈 Résultats Attendus

### Métriques de Succès
- Nombre d'UUIDs enrichis avec legal_entity_id
- Nombre d'UUIDs enrichis avec directory_id  
- Pourcentage d'amélioration du taux d'identification
- Validation de la cohérence des données

### Impact Métier
- Amélioration de la traçabilité des documents
- Facilitation des audits et contrôles
- Optimisation des processus de gestion documentaire
- Meilleure analyse des flux documentaires par entité

## 🚀 Prochaines Étapes

1. **Analyse Subscription API** - Extraction des 2,3M UUIDs de provided_info
2. **Test Customer Subscription API** - Vérification des rib_file_id  
3. **Exploration systématique** - Analyse de toutes les autres bases
4. **Consolidation des résultats** - Rapport d'enrichissement final

---
*Rapport généré le 23 juillet 2025*
