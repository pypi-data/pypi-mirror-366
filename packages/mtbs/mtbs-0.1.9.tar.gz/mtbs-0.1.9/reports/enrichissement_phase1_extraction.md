# Analyse d'Enrichissement - Phase 1 : Extraction des UUIDs

## 🔍 Découverte Majeure dans Subscription API

### Structure des UUIDs dans provided_info

Les UUIDs de fichiers sont stockés au format **JSON array** dans le champ `value` quand `data_type = 'FILE'` :

#### Statistiques
- **Total d'entrées FILE** : 11 884 680
- **Avec valeur** : 2 288 923 (19,3%)
- **Longueur moyenne** : 8,8 caractères (indique des arrays JSON)

#### Exemples d'UUIDs Extraits

```json
// Entreprise 2699614162 (SIREN: 832905327)
["00000c38-5835-4d9d-b211-54d4cae71bbd","96268241-1d79-4438-99f0-8bd2f1880548"]

// Entreprise 9581332006 (SIREN: 813673688)  
["00001067-ec57-438c-82b5-aa8e40452977"]

// Entreprise 8285216990 (SIREN: 901434357)
["000011a9-3a0a-46a7-b308-ba86387217fa","41cf52fb-9aca-495e-a681-9c95c315ee55"]
```

### Méthodologie d'Extraction

Pour chaque UUID trouvé dans `provided_info`, nous avons :
- **company_id** : Identifiant entreprise BPI France
- **siren** : Numéro SIREN officiel
- **project_id** : Identifiant du projet associé
- **info_type_technical_name** : Type de document technique

## 🎯 Processus d'Enrichissement Identifié

### Étape 1 : Extraction JSON
```sql
-- Parsing des arrays JSON pour extraire les UUIDs individuels
SELECT 
  JSON_EXTRACT(pi.value, '$[0]') as first_uuid,
  p.company_id,
  p.siren
FROM provided_info pi
JOIN project p ON p.id = pi.project_id
WHERE pi.data_type = 'FILE' AND pi.value IS NOT NULL
```

### Étape 2 : Correspondance avec uploaded_file
```sql
-- Test de présence dans uploaded_file
SELECT uf.id, uf.legal_entity_id, uf.directory_id
FROM uploaded_file uf
WHERE uf.id IN (/* UUIDs extraits */)
  AND (uf.legal_entity_id IS NULL OR uf.directory_id IS NULL)
```

### Étape 3 : Proposition d'Enrichissement
```sql
-- Mise à jour potentielle
UPDATE uploaded_file 
SET legal_entity_id = /* company_id trouvé */
WHERE id = /* UUID correspondant */
  AND legal_entity_id IS NULL
```

## 📊 Impact Potentiel

### Volume d'Enrichissement Estimé
- **UUIDs disponibles** : ~2,3 millions  
- **Fichiers sans propriétaire** : 4,98 millions
- **Correspondances potentielles** : À déterminer par tests

### Bénéfices Métier
1. **Traçabilité améliorée** : Lien direct projet ↔ fichier
2. **Compliance renforcée** : Association SIREN ↔ document
3. **Audits facilités** : Suivi par entreprise
4. **Processus optimisés** : Moins de fichiers orphelins

## 🚀 Prochaines Actions

1. **Extraction systématique** des UUIDs JSON
2. **Test de correspondance** avec uploaded_file  
3. **Validation de cohérence** des données
4. **Génération du script** de mise à jour

---
*Phase 1 complétée - 23 juillet 2025*
