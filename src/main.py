#!/usr/bin/env python3
"""
Camera di Commercio Marche - Data Scraper
Entry point semplificato
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from scraper import CamcomScraper
from utils import setup_logging, load_config


def parse_arguments() -> argparse.Namespace:
    """Parse degli argomenti da linea di comando."""
    parser = argparse.ArgumentParser(
        description="Scraper per dati imprese Camera di Commercio Marche",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi d'uso:
  # Lista periodi disponibili
  %(prog)s --list-periods
  
  # Estrai dati per Venezia (tutti i periodi disponibili tra start e end)
  %(prog)s --provincia Venezia --start 2020-03 --end 2024-09
  
  # Con formato data completo
  %(prog)s --provincia Venezia --start 2023-09-30 --end 2024-09-30
        """
    )
    
    # Argomenti principali
    parser.add_argument(
        "--provincia",
        type=str,
        help="Provincia da estrarre (es: Venezia, Padova)"
    )
    
    parser.add_argument(
        "--regione",
        type=str,
        default="VENETO",
        help="Regione di appartenenza (default: VENETO)"
    )
    
    parser.add_argument(
        "--start",
        type=str,
        help="Periodo iniziale (es: 2020-03, 2020-09-30)"
    )
    
    parser.add_argument(
        "--end",
        type=str,
        help="Periodo finale (es: 2024-09, 2024-12-31)"
    )
    
    # Configurazione
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Percorso del file di configurazione"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Percorso del file CSV di output"
    )
    
    # Opzioni
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Mostra il browser (per debug)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Abilita output verboso"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostra statistiche sui dati estratti"
    )
    
    parser.add_argument(
        "--list-periods",
        action="store_true",
        help="Mostra i periodi disponibili e esci"
    )
    
    return parser.parse_args()


def main() -> int:
    """Funzione principale."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(level=log_level)
    
    # Carica configurazione
    try:
        config = load_config(args.config)
    except Exception as e:
        logger.error(f"Errore nel caricamento configurazione: {e}")
        return 1
    
    try:
        # Inizializza scraper
        logger.info("Inizializzazione scraper...")
        scraper = CamcomScraper(
            config=config,
            headless=not args.no_headless
        )
        
        # Lista periodi
        if args.list_periods:
            logger.info("Recupero periodi disponibili...")
            periods = scraper.get_available_periods(regione=args.regione)
            
            if periods:
                print("\n📅 Periodi disponibili:\n")
                for period in periods:
                    print(f"  - {period}")
                print(f"\nTotale: {len(periods)} periodi")
            else:
                print("❌ Nessun periodo trovato")
            
            return 0
        
        # Validazione argomenti
        if not args.provincia:
            logger.error("Devi specificare --provincia")
            return 1
        
        if not args.start or not args.end:
            logger.error("Devi specificare --start e --end")
            return 1
        
        # Estrazione dati
        logger.info(f"Avvio estrazione per {args.provincia}...")
        
        data = scraper.scrape_data(
            provincia=args.provincia,
            periodo_start=args.start,
            periodo_end=args.end,
            regione=args.regione
        )
        
        if data is None or len(data) == 0:
            logger.warning("Nessun dato estratto")
            return 1
        
        logger.info(f"Estratte {len(data)} righe di dati")
        
        # Determina percorso output
        if args.output:
            output_path = Path(args.output)
        else:
            output_dir = Path(config["output"]["csv_directory"])
            filename = f"{args.provincia.lower()}_{args.start}_{args.end}.csv"
            output_path = output_dir / filename
        
        # Salva dati
        logger.info(f"Salvataggio dati in: {output_path}")
        scraper.save_to_csv(data, output_path)
        
        # Mostra statistiche
        if args.stats:
            print("\n📊 Statistiche dei dati estratti:\n")
            stats = scraper.get_statistics(data)
            for key, value in stats.items():
                if value is not None:
                    print(f"  {key}: {value}")
        
        logger.info("✅ Estrazione completata con successo!")
        print(f"\n✅ Dati salvati in: {output_path}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Operazione interrotta dall'utente")
        return 130
    
    except Exception as e:
        logger.error(f"❌ Errore durante l'esecuzione: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())