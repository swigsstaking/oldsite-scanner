"""
Module pour récupérer automatiquement les domaines .ch depuis crt.sh (Certificate Transparency logs)
"""

import asyncio
import aiohttp
import aiofiles
import re
import json
import os
from datetime import datetime
from typing import Set, List
import socket


# Configuration
YEARS = list(range(2020, 2026))  # 2020 à 2025
OUTFILE = "domains_final.txt"
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, OUTFILE)
CRTSH_BASE_URL = "https://crt.sh/"


def clean_domain(raw_domain: str) -> str:
    """
    Nettoie un domaine extrait de crt.sh
    
    Args:
        raw_domain: Domaine brut (peut contenir *, protocoles, etc.)
    
    Returns:
        Domaine nettoyé ou None si invalide
    """
    if not raw_domain:
        return None
    
    # Enlever les espaces
    domain = raw_domain.strip().lower()
    
    # Enlever les wildcards
    domain = domain.replace('*.', '')
    domain = domain.replace('*', '')
    
    # Enlever les protocoles
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^ftp://', '', domain)
    
    # Enlever les chemins
    domain = domain.split('/')[0]
    
    # Enlever les ports
    domain = domain.split(':')[0]
    
    # Enlever les espaces et caractères spéciaux
    domain = domain.strip()
    
    # Vérifier que c'est bien un .ch
    if not domain.endswith('.ch'):
        return None
    
    # Vérifier qu'il n'y a pas de caractères bizarres
    if not re.match(r'^[a-z0-9.-]+\.ch$', domain):
        return None
    
    # Enlever les sous-domaines trop profonds (garder max 2 niveaux)
    parts = domain.split('.')
    if len(parts) > 3:  # ex: sub.sub.domain.ch -> trop profond
        return None
    
    return domain


async def fetch_crtsh_year(session: aiohttp.ClientSession, year: int) -> Set[str]:
    """
    Récupère les domaines .ch pour une année donnée depuis crt.sh
    
    Args:
        session: Session aiohttp
        year: Année à interroger
    
    Returns:
        Set de domaines trouvés
    """
    domains = set()
    
    # Requête pour l'année
    # Format: https://crt.sh/?q=%.ch&output=json&minNotBefore=2024-01-01&maxNotBefore=2024-12-31
    params = {
        'q': '%.ch',
        'output': 'json',
        'minNotBefore': f'{year}-01-01',
        'maxNotBefore': f'{year}-12-31'
    }
    
    print(f"🔍 Interrogation crt.sh pour l'année {year}...")
    
    try:
        async with session.get(CRTSH_BASE_URL, params=params, timeout=aiohttp.ClientTimeout(total=120)) as response:
            if response.status != 200:
                print(f"   ⚠️  Erreur HTTP {response.status} pour {year}")
                return domains
            
            text = await response.text()
            
            # Parser le JSON
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                print(f"   ⚠️  Erreur de parsing JSON pour {year}")
                return domains
            
            if not isinstance(data, list):
                print(f"   ⚠️  Format inattendu pour {year}")
                return domains
            
            # Extraire les domaines
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                
                # Le champ peut être 'name_value' ou 'common_name'
                raw_domains = entry.get('name_value', '') or entry.get('common_name', '')
                
                # Peut contenir plusieurs domaines séparés par \n
                for raw_domain in raw_domains.split('\n'):
                    cleaned = clean_domain(raw_domain)
                    if cleaned:
                        domains.add(cleaned)
            
            print(f"   ✅ {year}: {len(domains)} domaines trouvés")
            
    except asyncio.TimeoutError:
        print(f"   ⏱️  Timeout pour {year}")
    except Exception as e:
        print(f"   ❌ Erreur pour {year}: {e}")
    
    return domains


async def verify_domain_dns(domain: str) -> bool:
    """
    Vérifie qu'un domaine résout en DNS (optionnel, peut être lent)
    
    Args:
        domain: Domaine à vérifier
    
    Returns:
        True si le domaine résout
    """
    try:
        loop = asyncio.get_event_loop()
        await loop.getaddrinfo(domain, None)
        return True
    except:
        return False


async def fetch_all_domains(verify_dns: bool = False) -> Set[str]:
    """
    Récupère tous les domaines .ch depuis crt.sh
    
    Args:
        verify_dns: Si True, vérifie que les domaines résolvent (lent!)
    
    Returns:
        Set de tous les domaines trouvés
    """
    all_domains = set()
    
    # Créer une session HTTP
    timeout = aiohttp.ClientTimeout(total=120)
    connector = aiohttp.TCPConnector(limit=10)  # Max 10 connexions simultanées
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        # Lancer les requêtes pour toutes les années en parallèle
        tasks = [fetch_crtsh_year(session, year) for year in YEARS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combiner les résultats
        for result in results:
            if isinstance(result, set):
                all_domains.update(result)
            elif isinstance(result, Exception):
                print(f"   ⚠️  Une requête a échoué: {result}")
    
    print(f"\n📊 Total brut: {len(all_domains)} domaines uniques")
    
    # Vérification DNS optionnelle
    if verify_dns and all_domains:
        print(f"\n🔍 Vérification DNS de {len(all_domains)} domaines (peut prendre du temps)...")
        verified = set()
        
        # Vérifier par lots de 100
        domains_list = list(all_domains)
        batch_size = 100
        
        for i in range(0, len(domains_list), batch_size):
            batch = domains_list[i:i+batch_size]
            tasks = [verify_domain_dns(d) for d in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for domain, result in zip(batch, results):
                if result is True:
                    verified.add(domain)
            
            print(f"   Vérifié {min(i+batch_size, len(domains_list))}/{len(domains_list)} domaines...")
        
        print(f"   ✅ {len(verified)} domaines résolvent en DNS")
        all_domains = verified
    
    return all_domains


async def save_domains(domains: Set[str], filepath: str):
    """
    Sauvegarde les domaines dans un fichier
    
    Args:
        domains: Set de domaines
        filepath: Chemin du fichier de sortie
    """
    # Trier les domaines
    sorted_domains = sorted(list(domains))
    
    print(f"\n💾 Sauvegarde de {len(sorted_domains)} domaines dans {filepath}...")
    
    async with aiofiles.open(filepath, 'w') as f:
        # Header
        await f.write(f"# Liste de domaines .ch récupérés depuis crt.sh\n")
        await f.write(f"# Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        await f.write(f"# Total: {len(sorted_domains)} domaines\n")
        await f.write(f"# Années: {min(YEARS)}-{max(YEARS)}\n")
        await f.write(f"#\n")
        await f.write(f"# Un domaine par ligne\n")
        await f.write(f"\n")
        
        # Domaines
        for domain in sorted_domains:
            await f.write(f"{domain}\n")
    
    print(f"   ✅ Fichier créé: {filepath}")


async def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("🌐 Récupération des domaines .ch depuis crt.sh")
    print("=" * 80)
    print(f"\n📅 Années interrogées: {min(YEARS)} à {max(YEARS)}")
    print(f"📁 Fichier de sortie: {OUTPUT_PATH}")
    print()
    
    # Récupérer les domaines
    domains = await fetch_all_domains(verify_dns=False)  # DNS verification désactivée (trop lent)
    
    if not domains:
        print("\n❌ Aucun domaine trouvé!")
        return 1
    
    # Sauvegarder
    await save_domains(domains, OUTPUT_PATH)
    
    print("\n" + "=" * 80)
    print("✅ SUCCÈS")
    print("=" * 80)
    print(f"\n📊 Statistiques:")
    print(f"   - Domaines trouvés: {len(domains)}")
    print(f"   - Fichier: {OUTPUT_PATH}")
    print()
    print("🚀 Prochaine étape:")
    print(f"   python -m backend.scan_ch_sites --domains-file {OUTFILE} --limit 500")
    print()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
