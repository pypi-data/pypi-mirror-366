streamlit run reports/app/main.py --server.port 8501

# MTBS Rapprochements Explorer

Application web interactive pour explorer les rapprochements découverts entre les bases de données MTBS de BPI France.

## 🎯 Fonctionnalités

### 🏠 Accueil
- Vue d'ensemble des rapprochements découverts
- Métriques clés et statistiques

### 📊 Vue d'ensemble  
- Graphiques de répartition des documents par base
- Réseau des connexions entre bases de données
- Métriques principales

### 🔗 Rapprochements
- Exploration détaillée de chaque rapprochement :
  - **ESG API** ↔ **Uploads API** : Rapports ESG et entreprises
  - **Investor Dashboard** ↔ **Uploads API** : Documents d'investissement  
  - **Offers** ↔ **Uploads API** : Documents commerciaux
  - **BOost API** ↔ **Uploads API** : Dossiers KYC
- Requêtes SQL d'exemple
- Résultats de tests

### 📈 Analytics
- Taux de couverture des rapprochements
- Timeline des découvertes
- Insights et tendances

### 🛠️ Outils
- **Requêteur SQL interactif** avec toutes les bases MTBS
- Requêtes prédéfinies par base
- Export des résultats en CSV

## 🚀 Installation et lancement

### Prérequis
```bash
# Installer les dépendances
pip install -r requirements.txt
```

### Lancement
```bash
# Depuis le répertoire app/
streamlit run main.py

# Ou depuis la racine du projet
streamlit run reports/app/main.py
```

L'application sera accessible à l'adresse : http://localhost:8501

## 🔧 Configuration

### Mode connecté (recommandé)
Si le module MTBS est disponible, l'application peut exécuter de vraies requêtes SQL sur les bases de données.

### Mode démo
Si le module MTBS n'est pas disponible, l'application fonctionne avec des données d'exemple.

## 📊 Données supportées

L'application permet d'explorer :

- **5 bases de données** : ESG API, Uploads API, Investor Dashboard, Offers, BOost API
- **6 rapprochements** découverts
- **5M+ documents** liés
- **Identifiants d'entreprises** : SIREN, company_id, legal_entity_id
- **Types de documents** : Rapports ESG, documents KYC, bulletins de souscription, etc.

## 🎨 Interface

- **Navigation** intuitive via sidebar
- **Visualisations** interactives avec Plotly
- **Tableaux** de données avec Pandas
- **Métriques** temps réel
- **Export** des résultats

## 🔍 Cas d'usage

### Pour les équipes métier
- **Démonstration** des rapprochements découverts
- **Validation** des hypothèses d'analyse
- **Exploration** interactive des données

### Pour les équipes techniques
- **Tests** de requêtes SQL
- **Validation** des performances
- **Export** des données pour analyses avancées

### Pour la direction
- **Tableaux de bord** des connexions entre systèmes
- **Métriques** de couverture et qualité des données
- **ROI** des rapprochements identifiés

## 🛡️ Sécurité

- Aucune données sensible stockée dans l'application
- Requêtes en lecture seule via le système MTBS existant
- Mode démo sans connexion aux vraies bases

## 🔮 Extensions possibles

- **Alertes** temps réel sur nouveaux rapprochements
- **API REST** pour intégrations externes  
- **Tableaux de bord** personnalisés par utilisateur
- **Machine Learning** pour découverte automatique de rapprochements
- **Notifications** par email/Slack des anomalies détectées

---
*Application développée le 23 juillet 2025*
