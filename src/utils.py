"""
Utility functions per il progetto
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def setup_logging(level: int = logging.INFO, log_file: str = None) -> logging.Logger:
    """
    Configura il sistema di logging.
    
    Args:
        level: Livello di logging
        log_file: Percorso del file di log (opzionale)
        
    Returns:
        Logger configurato
    """
    # Formato del log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurazione base
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format
    )
    
    # Aggiungi handler per file se specificato
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(log_format, datefmt=date_format)
        )
        
        logging.getLogger().addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configurato")
    
    return logger


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Carica la configurazione da file YAML.
    
    Args:
        config_path: Percorso del file di configurazione
        
    Returns:
        Dizionario con la configurazione
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"File di configurazione non trovato: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Validazione configurazione base
    required_keys = ['api', 'output', 'extraction']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Chiave mancante nella configurazione: {key}")
    
    return config


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Carica un file JSON.
    
    Args:
        file_path: Percorso del file
        
    Returns:
        Dati JSON come dizionario
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, file_path: Path):
    """
    Salva dati in formato JSON.
    
    Args:
        data: Dati da salvare
        file_path: Percorso del file
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def format_timestamp(dt: datetime = None) -> str:
    """
    Formatta un timestamp in modo leggibile.
    
    Args:
        dt: Datetime da formattare (default: now)
        
    Returns:
        Stringa formattata
    """
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def create_directory_structure():
    """Crea la struttura delle directory del progetto."""
    directories = [
        'data/raw',
        'data/processed',
        'data/cache',
        'logs',
        'config'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def validate_year_range(start_year: int, end_year: int) -> bool:
    """
    Valida un range di anni.
    
    Args:
        start_year: Anno iniziale
        end_year: Anno finale
        
    Returns:
        True se valido, False altrimenti
    """
    current_year = datetime.now().year
    
    if start_year > end_year:
        return False
    
    if start_year < 2000 or end_year > current_year + 1:
        return False
    
    return True


def format_number(num: int) -> str:
    """
    Formatta un numero con separatori delle migliaia.
    
    Args:
        num: Numero da formattare
        
    Returns:
        Stringa formattata
    """
    return f"{num:,}".replace(',', '.')


def calculate_file_size(file_path: Path) -> str:
    """
    Calcola la dimensione di un file in formato leggibile.
    
    Args:
        file_path: Percorso del file
        
    Returns:
        Dimensione formattata (es: "2.5 MB")
    """
    if not file_path.exists():
        return "0 B"
    
    size_bytes = file_path.stat().st_size
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"


def get_province_name_normalized(province: str) -> str:
    """
    Normalizza il nome di una provincia.
    
    Args:
        province: Nome provincia
        
    Returns:
        Nome normalizzato (lowercase, senza spazi)
    """
    return province.lower().strip().replace(' ', '-')


class ProgressBar:
    """Barra di progresso semplice per operazioni lunghe."""
    
    def __init__(self, total: int, prefix: str = 'Progress'):
        """
        Inizializza la barra di progresso.
        
        Args:
            total: Numero totale di elementi
            prefix: Prefisso da mostrare
        """
        self.total = total
        self.prefix = prefix
        self.current = 0
        self.start_time = datetime.now()
    
    def update(self, step: int = 1):
        """
        Aggiorna la barra di progresso.
        
        Args:
            step: Incremento (default: 1)
        """
        self.current += step
        percentage = (self.current / self.total) * 100
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        if self.current > 0:
            eta = elapsed * (self.total - self.current) / self.current
            eta_str = f"ETA: {int(eta)}s"
        else:
            eta_str = "ETA: N/A"
        
        bar_length = 30
        filled = int(bar_length * self.current / self.total)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f'\r{self.prefix}: |{bar}| {percentage:.1f}% ({self.current}/{self.total}) {eta_str}', end='')
        
        if self.current >= self.total:
            print()  # Newline alla fine
    
    def finish(self):
        """Completa la barra di progresso."""
        self.current = self.total
        self.update(0)