"""
Script pour récupérer automatiquement tous les domaines .ch via AXFR
et créer le fichier domains_ch.txt
"""

import subprocess
import sys
import os
from datetime import datetime


def try_axfr_transfer(zone="ch", nameserver="zonedata.switch.ch"):
    """
    Tente un transfert de zone AXFR pour récupérer tous les domaines .ch
    
    Args:
        zone: Zone DNS à transférer (défaut: "ch")
        nameserver: Serveur DNS à interroger (défaut: "zonedata.switch.ch")
    
    Returns:
        list: Liste des domaines trouvés, ou None si échec
    """
    print(f"🔍 Tentative de transfert AXFR depuis {nameserver} pour la zone .{zone}")
    
    try:
        # Commande dig pour AXFR
        cmd = ["dig", f"@{nameserver}", zone, "AXFR", "+noall", "+answer"]
        
        print(f"   Commande: {' '.join(cmd)}")
        
        # Exécuter la commande
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        if result.returncode != 0:
            print(f"❌ Échec AXFR (code {result.returncode})")
            if result.stderr:
                print(f"   Erreur: {result.stderr[:200]}")
            return None
        
        # Parser la sortie pour extraire les domaines
        domains = set()
        lines = result.stdout.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            parts = line.split()
            if len(parts) >= 1:
                domain = parts[0].rstrip('.')
                # Ne garder que les domaines .ch (pas les sous-domaines)
                if domain.endswith(f'.{zone}') and domain.count('.') == 1:
                    # Extraire juste le nom de domaine
                    domain_name = domain.replace(f'.{zone}', '')
                    if domain_name and not domain_name.startswith('_'):
                        domains.add(f"{domain_name}.{zone}")
        
        if domains:
            print(f"✅ AXFR réussi: {len(domains)} domaines .{zone} trouvés")
            return sorted(list(domains))
        else:
            print(f"⚠️  AXFR retourné mais aucun domaine trouvé")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout: Le transfert AXFR a pris trop de temps")
        return None
    except FileNotFoundError:
        print(f"❌ Erreur: La commande 'dig' n'est pas installée")
        print(f"   Installez-la avec: sudo apt install dnsutils")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return None


def try_alternative_sources():
    """
    Tente des sources alternatives pour récupérer des domaines .ch
    
    Returns:
        list: Liste des domaines trouvés, ou None si échec
    """
    print("🔄 Tentative de sources alternatives...")
    
    # Liste de serveurs DNS alternatifs à essayer
    alternative_servers = [
        "ns1.nic.ch",
        "ns2.nic.ch", 
        "ns3.nic.ch",
        "a.nic.ch",
        "b.nic.ch",
        "c.nic.ch",
        "d.nic.ch",
        "e.nic.ch",
    ]
    
    for server in alternative_servers:
        print(f"   Essai avec {server}...")
        domains = try_axfr_transfer(zone="ch", nameserver=server)
        if domains:
            return domains
    
    print("❌ Toutes les sources alternatives ont échoué")
    return None


def save_domains_to_file(domains, filename="domains_ch.txt"):
    """
    Sauvegarde la liste de domaines dans un fichier
    
    Args:
        domains: Liste des domaines
        filename: Nom du fichier de sortie
    """
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    
    try:
        with open(filepath, 'w') as f:
            # Header avec info
            f.write(f"# Liste de domaines .ch\n")
            f.write(f"# Généré automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(domains)} domaines\n")
            f.write(f"#\n")
            f.write(f"# Un domaine par ligne\n")
            f.write(f"# Les lignes commençant par # sont ignorées\n")
            f.write(f"\n")
            
            # Domaines
            for domain in domains:
                f.write(f"{domain}\n")
        
        print(f"✅ Fichier créé: {filepath}")
        print(f"   {len(domains)} domaines sauvegardés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False


def check_existing_file(filename="domains_ch.txt"):
    """
    Vérifie si un fichier de domaines existe déjà
    
    Returns:
        tuple: (existe, nombre_de_domaines)
    """
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    
    if not os.path.exists(filepath):
        return False, 0
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            domains = [l.strip() for l in lines if l.strip() and not l.startswith('#')]
            return True, len(domains)
    except:
        return True, 0


def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("🌐 Récupération automatique des domaines .ch")
    print("=" * 80)
    print()
    
    # Vérifier si un fichier existe déjà
    exists, count = check_existing_file()
    if exists:
        print(f"ℹ️  Un fichier domains_ch.txt existe déjà ({count} domaines)")
        print(f"   Il sera remplacé si la récupération réussit")
        print()
    
    # Tentative 1: AXFR sur zonedata.switch.ch
    domains = try_axfr_transfer(zone="ch", nameserver="zonedata.switch.ch")
    
    # Tentative 2: Sources alternatives
    if not domains:
        print()
        domains = try_alternative_sources()
    
    # Si échec complet
    if not domains:
        print()
        print("=" * 80)
        print("❌ ÉCHEC: Impossible de récupérer les domaines .ch")
        print("=" * 80)
        print()
        
        if exists:
            print(f"ℹ️  Le fichier existant ({count} domaines) sera conservé")
            print(f"   Le scanner pourra utiliser cette liste")
            sys.exit(0)  # Exit 0 pour ne pas bloquer le pipeline
        else:
            print("⚠️  Aucun fichier domains_ch.txt disponible")
            print()
            print("Solutions:")
            print("  1. Installer dig: sudo apt install dnsutils")
            print("  2. Vérifier la connectivité réseau")
            print("  3. Créer manuellement domains_ch.txt")
            print("  4. Utiliser une liste de domaines d'une autre source")
            sys.exit(1)
    
    # Sauvegarder les domaines
    print()
    if save_domains_to_file(domains):
        print()
        print("=" * 80)
        print("✅ SUCCÈS: Domaines .ch récupérés et sauvegardés")
        print("=" * 80)
        print()
        print(f"📊 Statistiques:")
        print(f"   - Domaines trouvés: {len(domains)}")
        print(f"   - Fichier: domains_ch.txt")
        print()
        print("🚀 Prochaine étape:")
        print("   python -m backend.scan_ch_sites --limit 100")
        print()
        sys.exit(0)
    else:
        print()
        print("❌ Échec de la sauvegarde")
        sys.exit(1)


if __name__ == "__main__":
    main()
