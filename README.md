# Camera di Commercio Marche - Data Scraper

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Scraper Python per l'estrazione automatica dei dati sulle imprese attive dal portale [Open Data Explorer](https://opendata.marche.camcom.it/) della Camera di Commercio delle Marche.

## Descrizione

Questo progetto permette di estrarre in modo automatizzato i dati statistici sulle imprese attive nelle province italiane. I dati vengono salvati in formato CSV per analisi successive.

## Funzionalità

- Estrazione dati da JSON-stat API
- Supporto per tutte le province e regioni italiane
- Range temporale personalizzabile (2009-2025)
- Filtri per settore economico (ATECO)
- Export in formato CSV
- Gestione errori e retry automatico
- Logging dettagliato delle operazioni
- Cache locale per ottimizzare le richieste
- Configurazione tramite file YAML

## Quick Start

### Prerequisiti

- Python 3.8 o superiore
- pip (package manager)

### Installazione

```bash
# Clona il repository
git clone https://github.com/kappall/camcom-marche-scraper.git
cd camcom-marche-scraper

# Crea un ambiente virtuale
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installa le dipendenze
pip install -r requirements.txt
```

### Utilizzo Base

```bash
# Estrai dati per la provincia di Venezia (2009-2025)
python src/main.py --provincia Venezia --start 2009-03-31 --end 2025-09-30

# Utilizza configurazione personalizzata
python src/main.py --config config/custom_config.yaml
```

## Struttura del Progetto

```
camcom-marche-scraper/
│
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point dell'applicazione
│   ├── grafico.py              # Per costruire un line chart
│   ├── scraper.py              # Logica principale di scraping
│   └── utils.py                # Funzioni di utilità
│
├── config/
│   ├── config.yaml             # Configurazione principale
│   └── provinces.json          # Mapping province/codici
│
├── data/
│   ├── processed/              # Dati elaborati
│   └── cache/                  # Cache delle richieste
│
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

## Output dei Dati

I dati vengono salvati in formato CSV con le seguenti colonne:

```csv
provincia,anno,trimestre,settore_ateco,forma_giuridica,num_imprese_attive,variazione_annuale
Venezia,2024,Q4,C,Società di capitali,15234,2.3
```

### Colonne disponibili:

- `provincia`: Nome della provincia
- `anno`: Anno di riferimento
- `trimestre`: Trimestre (Q1, Q2, Q3, Q4)
- `settore_ateco`: Codice settore economico (ATECO 2025)
- `forma_giuridica`: Tipologia societaria
- `num_imprese_attive`: Numero di imprese attive
- `variazione_annuale`: Variazione percentuale anno su anno

## Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per i dettagli.

---

Se questo progetto ti è stato utile, lascia una stella su GitHub!
