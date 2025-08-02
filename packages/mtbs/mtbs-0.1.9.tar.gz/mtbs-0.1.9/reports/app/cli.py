#!/usr/bin/env python3
"""
MTBS Rapprochements CLI
Interface en ligne de commande pour explorer les rapprochements entre bases MTBS
"""

import argparse
import json
import sys
import os
from tabulate import tabulate
from datetime import datetime

# Ajouter le chemin parent pour importer les modules mtbs
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from src.mtbs.mcp_server import _mtbs
    MTBS_AVAILABLE = True
    print("✅ Module MTBS disponible - Mode connecté")
except ImportError:
    MTBS_AVAILABLE = False
    print("⚠️  Module MTBS non disponible - Mode démo")

# Données de configuration
DATABASES = {
    "esg": {"id": 34, "name": "ESG API"},
    "uploads": {"id": 13, "name": "Uploads API"},
    "investor": {"id": 49, "name": "Investor Dashboard"},
    "offers": {"id": 48, "name": "Offers"},
    "boost": {"id": 28, "name": "BOost API"},
    "customer_subscription": {"id": 30, "name": "Customer Subscription API"},
    "subscription": {"id": 5, "name": "Subscription API"},
    "product": {"id": 10, "name": "Product API"}
}

CONNECTIONS = [
    {
        "name": "ESG → Uploads (Rapports)",
        "from_db": "esg",
        "to_db": "uploads",
        "key": "report_model.upload_api_id → uploaded_file.id",
        "count": 10024
    },
    {
        "name": "ESG → Uploads (Entreprises)",
        "from_db": "esg",
        "to_db": "uploads", 
        "key": "company_id → legal_entity_id",
        "count": "Variable"
    },
    {
        "name": "Investor → Uploads (Fonds)",
        "from_db": "investor",
        "to_db": "uploads",
        "key": "fund_document.file_id → uploaded_file.id",
        "count": 34
    },
    {
        "name": "Investor → Uploads (Investissements)",
        "from_db": "investor", 
        "to_db": "uploads",
        "key": "investment_document.file_id → uploaded_file.id",
        "count": 9359
    },
    {
        "name": "Offers → Uploads",
        "from_db": "offers",
        "to_db": "uploads",
        "key": "documents.uploaded_file_id → uploaded_file.id",
        "count": 159741
    },
    {
        "name": "BOost → Uploads",
        "from_db": "boost",
        "to_db": "uploads",
        "key": "document.file_id → uploaded_file.id", 
        "count": 759754
    },
    {
        "name": "Customer Subscription → Uploads (RIB)",
        "from_db": "customer_subscription",
        "to_db": "uploads",
        "key": "subscription.rib_file_id → uploaded_file.id",
        "count": 97
    },
    {
        "name": "Customer Subscription → Uploads (RIB via payment_method)",
        "from_db": "customer_subscription",
        "to_db": "uploads",
        "key": "payment_method.rib_file_id → uploaded_file.id",
        "count": 974
    },
    {
        "name": "Subscription → Uploads (Documents projets GED)",
        "from_db": "subscription",
        "to_db": "uploads",
        "key": "gdc_selected_document.file_id → uploaded_file.id",
        "count": 14038
    },
    {
        "name": "🚀 Subscription → Uploads (Provided Info Files - MAJEUR)",
        "from_db": "subscription",
        "to_db": "uploads",
        "key": "provided_info.value (JSON UUIDs) → uploaded_file.id",
        "count": 2288897
    },
    {
        "name": "Customer Subscription → Product (Offres)",
        "from_db": "customer_subscription", 
        "to_db": "product",
        "key": "subscription.offer_id → product.id",
        "count": "À confirmer"
    }
]

PREDEFINED_QUERIES = {
    "uploads": {
        "count": "SELECT COUNT(*) as total_files FROM uploaded_file;",
        "legal_entities": "SELECT legal_entity_id, COUNT(*) as count FROM uploaded_file WHERE legal_entity_id IS NOT NULL GROUP BY legal_entity_id ORDER BY count DESC LIMIT 10;"
    },
    "esg": {
        "companies": "SELECT company_name, siren, company_id FROM company_information_model WHERE company_name IS NOT NULL LIMIT 10;",
        "reports": "SELECT COUNT(*) as total_reports FROM report_model;"
    },
    "investor": {
        "funds": "SELECT name, id FROM fund;",
        "investors": "SELECT COUNT(*) as total_users FROM users;"
    },
    "offers": {
        "documents": "SELECT document_type, COUNT(*) as count FROM documents GROUP BY document_type ORDER BY count DESC;",
        "companies": "SELECT company_id, COUNT(*) as docs FROM documents WHERE company_id IS NOT NULL GROUP BY company_id ORDER BY docs DESC LIMIT 10;"
    },
    "boost": {
        "projects": "SELECT COUNT(*) as total_projects FROM project;",
        "sirens": "SELECT company_siren, COUNT(*) as projects FROM project_search_fields WHERE company_siren IS NOT NULL GROUP BY company_siren ORDER BY projects DESC LIMIT 10;"
    },
    "customer_subscription": {
        "subscriptions": "SELECT COUNT(*) as total_subscriptions FROM subscription;",
        "ribs": "SELECT COUNT(*) as subscriptions_with_rib FROM subscription WHERE rib_file_id IS NOT NULL;",
        "entities": "SELECT COUNT(DISTINCT legal_entity_id) as unique_entities FROM subscription WHERE legal_entity_id IS NOT NULL;",
        "payment_ribs": "SELECT COUNT(*) as payment_ribs FROM payment_method WHERE rib_file_id IS NOT NULL;"
    },
    "subscription": {
        "projects": "SELECT COUNT(*) as total_projects FROM project;",
        "documents": "SELECT COUNT(*) as gdc_documents FROM gdc_selected_document WHERE file_id IS NOT NULL;",
        "provided_files": "SELECT COUNT(*) as provided_files FROM provided_info WHERE data_type = 'FILE' AND value IS NOT NULL;",
        "companies": "SELECT COUNT(DISTINCT company_id) as unique_companies FROM project WHERE company_id IS NOT NULL;",
        "sirens": "SELECT COUNT(DISTINCT siren) as unique_sirens FROM project WHERE siren IS NOT NULL;",
        "products": "SELECT product_name, COUNT(*) as projects FROM project WHERE product_name IS NOT NULL GROUP BY product_name ORDER BY projects DESC LIMIT 10;",
        "file_types": "SELECT info_type_technical_name, COUNT(*) as count FROM provided_info WHERE data_type = 'FILE' AND value IS NOT NULL GROUP BY info_type_technical_name ORDER BY count DESC LIMIT 15;"
    },
    "product": {
        "products": "SELECT COUNT(*) as total_products FROM product;",
        "catalog": "SELECT slug, label FROM product ORDER BY label LIMIT 10;"
    }
}

def execute_query(database_id: int, query: str, format_output=True):
    """Exécuter une requête SQL"""
    if not MTBS_AVAILABLE:
        print("❌ Mode démo - Impossible d'exécuter la requête")
        return None
    
    try:
        result = _mtbs.send_sql(query=query, database=database_id, raw=False, cache_enabled=True)
        data = json.loads(result)
        
        if format_output and data:
            print(f"\n📊 Résultat ({len(data)} lignes):")
            print(tabulate(data, headers="keys", tablefmt="grid"))
        
        return data
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return None

def list_databases():
    """Lister les bases de données disponibles"""
    print("\n🗃️  Bases de données disponibles:")
    print("-" * 50)
    
    data = []
    for key, db in DATABASES.items():
        data.append([key, db["name"], db["id"]])
    
    print(tabulate(data, headers=["Alias", "Nom", "ID"], tablefmt="grid"))

def list_connections():
    """Lister les rapprochements découverts"""
    print("\n🔗 Rapprochements découverts:")
    print("-" * 70)
    
    data = []
    for conn in CONNECTIONS:
        data.append([
            conn["name"],
            f"{DATABASES[conn['from_db']]['name']} → {DATABASES[conn['to_db']]['name']}",
            conn["key"],
            conn["count"]
        ])
    
    print(tabulate(data, headers=["Nom", "Bases", "Clé de liaison", "Volume"], tablefmt="grid"))

def show_connection_details(connection_name):
    """Afficher les détails d'un rapprochement"""
    conn = next((c for c in CONNECTIONS if c["name"].lower() == connection_name.lower()), None)
    
    if not conn:
        print(f"❌ Rapprochement '{connection_name}' non trouvé")
        return
    
    print(f"\n🔗 Détails du rapprochement: {conn['name']}")
    print("-" * 60)
    print(f"Base source: {DATABASES[conn['from_db']]['name']} (ID: {DATABASES[conn['from_db']]['id']})")
    print(f"Base cible: {DATABASES[conn['to_db']]['name']} (ID: {DATABASES[conn['to_db']]['id']})")
    print(f"Clé de liaison: {conn['key']}")
    print(f"Volume estimé: {conn['count']} enregistrements")

def run_predefined_query(db_alias, query_name):
    """Exécuter une requête prédéfinie"""
    if db_alias not in DATABASES:
        print(f"❌ Base '{db_alias}' non trouvée")
        return
    
    if db_alias not in PREDEFINED_QUERIES:
        print(f"❌ Aucune requête prédéfinie pour '{db_alias}'")
        return
    
    if query_name not in PREDEFINED_QUERIES[db_alias]:
        print(f"❌ Requête '{query_name}' non trouvée pour '{db_alias}'")
        print(f"Requêtes disponibles: {', '.join(PREDEFINED_QUERIES[db_alias].keys())}")
        return
    
    query = PREDEFINED_QUERIES[db_alias][query_name]
    db_id = DATABASES[db_alias]["id"]
    
    print(f"\n🚀 Exécution sur {DATABASES[db_alias]['name']}:")
    print(f"📝 Requête: {query}")
    
    execute_query(db_id, query)

def run_custom_query(db_alias, query):
    """Exécuter une requête personnalisée"""
    if db_alias not in DATABASES:
        print(f"❌ Base '{db_alias}' non trouvée")
        return
    
    db_id = DATABASES[db_alias]["id"]
    
    print(f"\n🚀 Exécution sur {DATABASES[db_alias]['name']}:")
    print(f"📝 Requête: {query}")
    
    result = execute_query(db_id, query)
    
    # Option d'export
    if result and len(result) > 0:
        export = input("\n💾 Exporter en CSV ? (o/N): ")
        if export.lower() == 'o':
            filename = f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            import pandas as pd
            df = pd.DataFrame(result)
            df.to_csv(filename, index=False)
            print(f"✅ Résultat exporté dans {filename}")

def interactive_mode():
    """Mode interactif"""
    print("\n🖥️  Mode interactif MTBS Explorer")
    print("Tapez 'help' pour voir les commandes disponibles")
    print("Tapez 'exit' pour quitter")
    
    while True:
        try:
            command = input("\nmtbs> ").strip()
            
            if command == "exit":
                print("👋 Au revoir!")
                break
            elif command == "help":
                print_help()
            elif command == "dbs":
                list_databases()
            elif command == "connections":
                list_connections()
            elif command.startswith("query "):
                parts = command.split(" ", 3)
                if len(parts) >= 3:
                    db_alias = parts[1]
                    if len(parts) == 3:  # requête prédéfinie
                        query_name = parts[2]
                        run_predefined_query(db_alias, query_name)
                    else:  # requête personnalisée
                        query = " ".join(parts[2:])
                        run_custom_query(db_alias, query)
                else:
                    print("Usage: query <db_alias> <query_name_or_sql>")
            elif command.startswith("details "):
                conn_name = command[8:]
                show_connection_details(conn_name)
            else:
                print("❌ Commande non reconnue. Tapez 'help' pour l'aide.")
                
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except EOFError:
            print("\n👋 Au revoir!")
            break

def print_help():
    """Afficher l'aide"""
    print("\n📖 Commandes disponibles:")
    print("-" * 40)
    print("dbs                          - Lister les bases de données")
    print("connections                  - Lister les rapprochements")
    print("details <connection_name>    - Détails d'un rapprochement")
    print("query <db> <query_name>      - Exécuter requête prédéfinie")  
    print("query <db> <sql>             - Exécuter requête personnalisée")
    print("help                         - Afficher cette aide")
    print("exit                         - Quitter")
    
    print(f"\n📚 Requêtes prédéfinies par base:")
    for db_alias, queries in PREDEFINED_QUERIES.items():
        print(f"  {db_alias}: {', '.join(queries.keys())}")

def main():
    parser = argparse.ArgumentParser(
        description="MTBS Rapprochements CLI - Explorer les connexions entre bases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s --list-dbs                     # Lister les bases
  %(prog)s --list-connections             # Lister les rapprochements  
  %(prog)s --query uploads count          # Requête prédéfinie
  %(prog)s --query esg "SELECT COUNT(*)"  # Requête personnalisée
  %(prog)s --interactive                  # Mode interactif
        """
    )
    
    parser.add_argument("--list-dbs", action="store_true", help="Lister les bases de données")
    parser.add_argument("--list-connections", action="store_true", help="Lister les rapprochements")
    parser.add_argument("--details", help="Détails d'un rapprochement")
    parser.add_argument("--query", nargs=2, metavar=("DB", "QUERY"), help="Exécuter une requête")
    parser.add_argument("--interactive", action="store_true", help="Mode interactif")
    
    args = parser.parse_args()
    
    print("🔍 MTBS Rapprochements CLI")
    print("=" * 40)
    
    if args.list_dbs:
        list_databases()
    elif args.list_connections:
        list_connections()
    elif args.details:
        show_connection_details(args.details)
    elif args.query:
        db_alias, query_or_name = args.query
        if query_or_name in PREDEFINED_QUERIES.get(db_alias, {}):
            run_predefined_query(db_alias, query_or_name)
        else:
            run_custom_query(db_alias, query_or_name)
    elif args.interactive:
        interactive_mode()
    else:
        print("Utilisez --help pour voir les options disponibles")
        print("Ou --interactive pour le mode interactif")

if __name__ == "__main__":
    main()
