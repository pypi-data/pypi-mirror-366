#!/usr/bin/env python3
"""
Script d'enrichissement des données uploaded_file
Extraction des UUIDs depuis les différentes APIs MTBS et identification des propriétaires
"""

import json
import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileOwnership:
    """Structure pour stocker les informations de propriétaire d'un fichier"""
    file_uuid: str
    company_id: str = None
    siren: str = None
    legal_entity_id: str = None
    directory_id: str = None
    source_api: str = None
    source_table: str = None
    confidence: float = 1.0  # Niveau de confiance (0-1)

class MTBSEnrichmentAnalyzer:
    """Analyseur pour l'enrichissement des données uploaded_file"""
    
    def __init__(self):
        self.found_ownerships: List[FileOwnership] = []
        self.databases = {
            "subscription_api": 5,
            "customer_subscription_api": 30, 
            "uploads_api": 13,
            "customer_documents_api": 51,
            "ocr_api": 33,
            "checklist_api": 15,
            "decision_api": 40,
            "contract_api": 2,
            "compliance_api": 50,
            "risk_api": 17,
            "fraud_detection_api": 18,
            "workflow_api": 6,
            "messaging_api": 8,
            "secure_space": 44
        }
    
    def extract_uuids_from_json(self, json_value: str) -> List[str]:
        """Extrait les UUIDs d'une valeur JSON"""
        if not json_value or json_value == 'null':
            return []
        
        try:
            # Parsing JSON
            if json_value.startswith('[') and json_value.endswith(']'):
                uuids = json.loads(json_value)
                if isinstance(uuids, list):
                    return [uuid.strip('"') for uuid in uuids if self.is_valid_uuid(uuid.strip('"'))]
            
            # Test direct UUID
            if self.is_valid_uuid(json_value):
                return [json_value]
                
        except json.JSONDecodeError:
            # Recherche par regex en cas d'échec JSON
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            matches = re.findall(uuid_pattern, json_value, re.IGNORECASE)
            return matches
        
        return []
    
    def is_valid_uuid(self, uuid_str: str) -> bool:
        """Valide le format UUID"""
        if not uuid_str or len(uuid_str) != 36:
            return False
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, uuid_str, re.IGNORECASE))
    
    def analyze_subscription_api(self) -> List[FileOwnership]:
        """Analyse l'API Subscription pour extraire les UUIDs de provided_info"""
        print("🔍 Analyse Subscription API - provided_info...")
        
        # Cette fonction serait connectée à la base via le MCP server
        # Pour l'instant, on simule avec les données que nous avons trouvées
        
        sample_data = [
            {
                "value": '["00000c38-5835-4d9d-b211-54d4cae71bbd","96268241-1d79-4438-99f0-8bd2f1880548"]',
                "company_id": "2699614162",
                "siren": "832905327"
            },
            {
                "value": '["00001067-ec57-438c-82b5-aa8e40452977"]',
                "company_id": "9581332006", 
                "siren": "813673688"
            }
        ]
        
        ownerships = []
        for record in sample_data:
            uuids = self.extract_uuids_from_json(record["value"])
            for uuid in uuids:
                ownership = FileOwnership(
                    file_uuid=uuid,
                    company_id=record["company_id"],
                    siren=record["siren"],
                    source_api="subscription_api",
                    source_table="provided_info",
                    confidence=0.95
                )
                ownerships.append(ownership)
        
        return ownerships
    
    def analyze_customer_subscription_api(self) -> List[FileOwnership]:
        """Analyse l'API Customer Subscription pour les rib_file_id"""
        print("🔍 Analyse Customer Subscription API - payment_method...")
        
        # Simulation des données payment_method.rib_file_id
        # Basé sur notre analyse précédente
        return []
    
    def generate_enrichment_report(self) -> Dict:
        """Génère un rapport d'enrichissement complet"""
        total_found = len(self.found_ownerships)
        unique_files = len(set([o.file_uuid for o in self.found_ownerships]))
        unique_companies = len(set([o.company_id for o in self.found_ownerships if o.company_id]))
        
        sources = {}
        for ownership in self.found_ownerships:
            source = ownership.source_api
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        
        return {
            "total_ownerships_found": total_found,
            "unique_files": unique_files,
            "unique_companies": unique_companies,
            "sources_breakdown": sources,
            "analysis_date": datetime.now().isoformat()
        }
    
    def generate_update_script(self) -> str:
        """Génère le script SQL de mise à jour pour uploaded_file"""
        script_parts = [
            "-- Script de mise à jour uploaded_file",
            f"-- Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- Total d'UUIDs à enrichir: {len(self.found_ownerships)}",
            "",
            "BEGIN TRANSACTION;",
            ""
        ]
        
        for ownership in self.found_ownerships:
            if ownership.company_id:
                update_sql = f"""UPDATE uploaded_file 
SET legal_entity_id = '{ownership.company_id}' 
WHERE id = '{ownership.file_uuid}' 
  AND legal_entity_id IS NULL;"""
                script_parts.append(update_sql)
                script_parts.append("")
        
        script_parts.extend([
            "COMMIT;",
            "",
            f"-- Fin du script - {len(self.found_ownerships)} mises à jour potentielles"
        ])
        
        return "\n".join(script_parts)

def main():
    """Fonction principale d'analyse"""
    print("🚀 Démarrage de l'analyse d'enrichissement MTBS")
    print("=" * 60)
    
    analyzer = MTBSEnrichmentAnalyzer()
    
    # Phase 1: Subscription API
    subscription_ownerships = analyzer.analyze_subscription_api()
    analyzer.found_ownerships.extend(subscription_ownerships)
    
    # Phase 2: Customer Subscription API  
    customer_subscription_ownerships = analyzer.analyze_customer_subscription_api()
    analyzer.found_ownerships.extend(customer_subscription_ownerships)
    
    # Génération du rapport
    report = analyzer.generate_enrichment_report()
    print("\n📊 Rapport d'Enrichissement:")
    print(f"- UUIDs trouvés: {report['unique_files']}")
    print(f"- Entreprises concernées: {report['unique_companies']}")
    print(f"- Sources analysées: {list(report['sources_breakdown'].keys())}")
    
    # Génération du script de mise à jour
    update_script = analyzer.generate_update_script()
    
    return analyzer, report, update_script

if __name__ == "__main__":
    analyzer, report, script = main()
    print("\n✅ Analyse terminée avec succès!")
