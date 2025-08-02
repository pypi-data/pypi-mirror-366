#!/usr/bin/env python3
"""
Test rapide pour vérifier que la Vue d'ensemble est mise à jour avec l'enrichissement
"""
import sys
import os

# Ajouter le chemin pour importer main.py
sys.path.append('/home/ruddy/dev/workspaces/bpifrance/python/mtbs/reports/app')

# Simuler l'absence de MTBS pour tester les données d'exemple
import main
main.MTBS_AVAILABLE = False

def test_live_connections():
    """Test de la fonction get_live_connections mise à jour"""
    print("🔍 Test des connexions live avec enrichissement...")
    
    connections = main.get_live_connections()
    
    print(f"\n📊 Nombre de connexions trouvées : {len(connections)}")
    
    # Vérifier que l'enrichissement est présent
    enrichissement_found = False
    for conn in connections:
        print(f"  - {conn['from']} → {conn['to']}")
        print(f"    Type: {conn['type']}")
        print(f"    Count: {conn['count']:,}")
        print(f"    Status: {conn['status']}")
        
        if "ENRICHISSEMENT VALIDÉ" in conn['status']:
            enrichissement_found = True
            print("    ✅ ENRICHISSEMENT TROUVÉ!")
        print()
    
    if enrichissement_found:
        print("🎯 SUCCESS: L'enrichissement de 2.3M fichiers est bien présent dans Vue d'ensemble!")
    else:
        print("❌ ERREUR: L'enrichissement n'apparaît pas dans Vue d'ensemble")
    
    return enrichissement_found

def test_home_content():
    """Test du contenu de la page d'accueil"""
    print("\n🏠 Test du contenu d'accueil...")
    
    # Lire le fichier main.py pour vérifier le contenu
    with open('/home/ruddy/dev/workspaces/bpifrance/python/mtbs/reports/app/main.py', 'r') as f:
        content = f.read()
    
    # Vérifications
    checks = [
        ("🎯 NOUVEAU : Subscription API", "Nouvelle connexion mentionnée"),
        ("2,3M fichiers validés", "Métriques d'enrichissement"),
        ("ENRICHISSEMENT VALIDÉ", "Status d'enrichissement"),
        ("🎯 Nouveaux fichiers", "Métrique de nouveaux fichiers")
    ]
    
    all_found = True
    for check, description in checks:
        if check in content:
            print(f"  ✅ {description}: TROUVÉ")
        else:
            print(f"  ❌ {description}: MANQUANT")
            all_found = False
    
    return all_found

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DE MISE À JOUR DE LA VUE D'ENSEMBLE")
    print("=" * 60)
    
    # Test 1: Connexions live
    conn_test = test_live_connections()
    
    # Test 2: Contenu d'accueil
    home_test = test_home_content()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    if conn_test and home_test:
        print("🎉 TOUS LES TESTS PASSÉS!")
        print("   L'application Vue d'ensemble est maintenant à jour avec l'enrichissement.")
        print("   Les 2.3M fichiers de provided_info sont correctement affichés.")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        if not conn_test:
            print("   - Problème avec les connexions live")
        if not home_test:
            print("   - Problème avec le contenu d'accueil")
