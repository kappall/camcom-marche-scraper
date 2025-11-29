"""
Camera di Commercio Marche - Scraper Core
Scraping diretto dalla tabella pivot HTML
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException


logger = logging.getLogger(__name__)


class CamcomScraper:
    """Scraper per la tabella pivot della Camera di Commercio Marche."""
    
    BASE_URL = "https://opendata.marche.camcom.it/pivot-table.htm"
    
    def __init__(self, config: Dict[str, Any], headless: bool = True):
        """
        Inizializza lo scraper.
        
        Args:
            config: Dizionario di configurazione
            headless: Se True, esegue Chrome in modalità headless
        """
        self.config = config
        self.headless = headless
        self.driver = None
        
        logger.info("Scraper inizializzato")
    
    def _init_driver(self):
        """Inizializza il driver Selenium."""
        if self.driver is not None:
            return
        
        logger.info("Inizializzazione driver Chrome...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        logger.info("Driver Chrome pronto")
    
    def _close_driver(self):
        """Chiude il driver Selenium."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Driver Chrome chiuso")
    
    def get_available_periods(self, regione: str = "VENETO") -> List[str]:
        """
        Ottiene i periodi disponibili dal select con id 'pivot-time'.
        
        Args:
            regione: Regione da filtrare
            
        Returns:
            Lista di periodi disponibili (es: ['2025-09-30', '2025-03', ...])
        """
        self._init_driver()
        
        try:
            # Costruisci URL
            url = f"{self.BASE_URL}?indic=Art&r1=2&r2=3&r3=4&c1=1&f1=0&f1v={regione.upper()}"
            
            logger.info(f"Caricamento pagina: {url}")
            self.driver.get(url)
            
            # Attendi caricamento select dei periodi
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.ID, "pivot-time")))
            
            time.sleep(1)  # Attendi rendering completo
            
            # Trova il select con id "pivot-time"
            select_element = self.driver.find_element(By.ID, "pivot-time")
            
            # Estrai tutte le opzioni
            options = select_element.find_elements(By.TAG_NAME, "option")
            
            periods = []
            for option in options:
                value = option.get_attribute("value")
                if value:
                    periods.append(value)
            
            logger.info(f"Trovati {len(periods)} periodi nel select")
            return sorted(periods, reverse=True)  # Dal più recente al più vecchio
            
        except Exception as e:
            logger.error(f"Errore nel recupero periodi: {e}")
            return []

    def _extract_value_for_province(self, provincia: str) -> Optional[int]:
      """
      Estrae il valore dalla tabella pivot per una provincia specifica.
      
      Cerca la colonna con header contenente il nome della provincia (match case-insensitive).
      Poi prende la cella corrispondente nell'ultima riga della tabella (tipicamente la riga dei totali).

      Args:
          provincia: Nome della provincia da cercare.

      Returns:
          Valore numerico oppure None se non trovato.
      """
      try:
          # Trova la tabella pivot
          table = self.driver.find_element(By.CLASS_NAME, "pvtTable")

          # Header: tutte le colonne che rappresentano province
          col_labels = table.find_elements(By.CLASS_NAME, "pvtColLabel")

          provincia_upper = provincia.upper()
          col_index = None

          # Identifica indice della colonna
          for idx, col_label in enumerate(col_labels):
              if provincia_upper in col_label.text.upper():
                  col_index = idx
                  break

          if col_index is None:
              logger.warning(f"Provincia '{provincia}' non trovata nelle colonne della tabella pivot.")
              return None

          # Tutte le righe della tabella
          rows = table.find_elements(By.TAG_NAME, "tr")
          if not rows:
              logger.warning("Nessuna riga trovata nella tabella pivot.")
              return None

          # Ultima riga (di solito la riga dei totali)
          last_row = rows[-1]
          cells = last_row.find_elements(By.TAG_NAME, "td")

          if col_index >= len(cells):
              logger.warning(f"Colonna {col_index} non presente nell'ultima riga.")
              return None

          # Valore testuale della cella
          value_text = cells[col_index].text.strip()

          # Normalize: rimuovi separatori
          cleaned = value_text.replace('.', '').replace(',', '').replace(' ', '')

          if cleaned.isdigit():
              return int(cleaned)

          logger.warning(f"Valore non numerico per provincia '{provincia}': '{value_text}'")
          return None

      except NoSuchElementException:
          logger.error("Elemento tabella pivot non trovato.")
          return None
      except Exception as e:
          logger.error(f"Errore nell'estrazione del valore: {e}")
          return None
    
    
    def scrape_data(
        self,
        provincia: str,
        periodo_start: str,
        periodo_end: str,
        regione: str = "VENETO"
    ) -> Optional[pd.DataFrame]:
        """
        Scrape i dati dalla tabella pivot.
        Usa i periodi esatti disponibili nel select #pivot-time.
        
        Args:
            provincia: Nome provincia (es: "Venezia")
            periodo_start: Periodo iniziale (es: "2020-03")
            periodo_end: Periodo finale (es: "2024-09")
            regione: Regione di appartenenza
            
        Returns:
            DataFrame con i dati estratti
        """
        self._init_driver()
        
        try:
            # Costruisci URL base
            url = f"{self.BASE_URL}?indic=Art&r1=2&r2=3&r3=4&c1=1&f1=0&f1v={regione.upper()}"
            
            logger.info(f"Caricamento pagina iniziale: {url}")
            self.driver.get(url)
            
            # Attendi caricamento
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.presence_of_element_located((By.ID, "pivot-time")))
            time.sleep(1)
            
            # Ottieni tutti i periodi disponibili
            all_periods = self.get_available_periods(regione)
            
            if not all_periods:
                logger.error("Nessun periodo disponibile")
                return None
            
            # Filtra i periodi tra start e end
            periodi = [p for p in all_periods if periodo_start <= p <= periodo_end]

            if not periodi:
                logger.warning(f"Nessun periodo trovato tra {periodo_start} e {periodo_end}")
                logger.info(f"Periodi disponibili: {all_periods[:5]}... (primi 5)")
                return None

            # Mantieni un solo periodo per anno (il primo perché all_periods è già in ordine decrescente)
            periodi_unici = {}
            for p in periodi:
                anno = p[:4]
                if anno not in periodi_unici:
                    periodi_unici[anno] = p

            # Lista finale, ordinata per anno decrescente
            periodi_finali = sorted(periodi_unici.values(), reverse=True)

            logger.info(f"Periodi selezionati (uno per anno): {periodi_finali}")

            
            all_data = []
            
            for i, periodo in enumerate(periodi_finali, 1):
                logger.info(f"[{i}/{len(periodi_finali)}] Elaborazione periodo: {periodo}")
                
                try:
                    # Seleziona il periodo nel dropdown
                    select_element = self.driver.find_element(By.ID, "pivot-time")
                    
                    # Trova l'opzione con il valore del periodo
                    option = select_element.find_element(By.CSS_SELECTOR, f"option[value='{periodo}']")
                    option.click()
                    
                    # Attendi che la tabella si aggiorni
                    time.sleep(2)  # Importante: attendi il refresh della tabella
                    
                    # Estrai il valore per la provincia
                    valore = self._extract_value_for_province(provincia)
                    
                    if valore is not None:
                        all_data.append({
                            'provincia': provincia,
                            'periodo': periodo,
                            'num_imprese_attive': valore,
                            'data_estrazione': datetime.now().isoformat()
                        })
                        logger.info(f"  ✓ {provincia} - {periodo}: {valore:,} imprese")
                    else:
                        logger.warning(f"  ✗ Valore non trovato per {provincia} - {periodo}")
                    
                except Exception as e:
                    logger.error(f"Errore nell'elaborazione periodo {periodo}: {e}")
                    continue
            
            if not all_data:
                logger.warning("Nessun dato estratto")
                return None
            
            # Crea DataFrame
            df = pd.DataFrame(all_data)
            logger.info(f"Estrazione completata: {len(df)} record")
            
            return df
            
        except Exception as e:
            logger.error(f"Errore nello scraping: {e}", exc_info=True)
            return None
        
        finally:
            self._close_driver()
    
    def __del__(self):
        """Cleanup quando l'oggetto viene distrutto."""
        self._close_driver()
        """
        Estrae il valore dalla tabella pvtTable per una provincia specifica.
        Trova la colonna con classe pvtColLabel che contiene il nome della provincia (uppercase),
        poi prende il valore dall'ultima riga di quella colonna.
        
        Args:
            provincia: Nome provincia (es: "Venezia")
            periodo: Periodo da cercare
            
        Returns:
            Valore numerico del totale o None
        """
        try:
            # Trova la tabella con classe pvtTable
            table = self.driver.find_element(By.CLASS_NAME, "pvtTable")
            
            # Trova tutte le colonne con classe pvtColLabel
            col_labels = table.find_elements(By.CLASS_NAME, "pvtColLabel")
            
            provincia_upper = provincia.upper()
            col_index = None
            
            # Cerca l'indice della colonna che contiene il nome della provincia
            for idx, col_label in enumerate(col_labels):
                if provincia_upper in col_label.text.upper():
                    col_index = idx
                    logger.debug(f"Trovata provincia '{provincia}' nella colonna {idx}")
                    break
            
            if col_index is None:
                logger.warning(f"Provincia '{provincia}' non trovata nelle colonne")
                return None
            
            # Trova tutte le righe della tabella
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            if not rows:
                logger.warning("Nessuna riga trovata nella tabella")
                return None
            
            # Prendi l'ultima riga (che contiene i totali)
            last_row = rows[-1]
            cells = last_row.find_elements(By.TAG_NAME, "td")
            
            if not cells or col_index >= len(cells):
                logger.warning(f"Colonna {col_index} non trovata nell'ultima riga")
                return None
            
            # Estrai il valore dalla cella corrispondente
            value_text = cells[col_index].text.strip()
            
            # Pulisci il valore: rimuovi separatori di migliaia
            value_clean = value_text.replace('.', '').replace(',', '').replace(' ', '')
            
            if value_clean.isdigit():
                value = int(value_clean)
                logger.debug(f"Valore estratto: {value}")
                return value
            else:
                logger.warning(f"Valore non numerico: '{value_text}'")
                return None
            
        except NoSuchElementException as e:
            logger.error(f"Elemento non trovato: {e}")
            return None
        except Exception as e:
            logger.error(f"Errore nell'estrazione valore: {e}")
            return None
    
    def save_to_csv(self, data: pd.DataFrame, output_path: Path):
        """
        Salva i dati in formato CSV.
        
        Args:
            data: DataFrame da salvare
            output_path: Percorso del file di output
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            data.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"CSV salvato: {output_path}")
            
        except Exception as e:
            logger.error(f"Errore nel salvataggio CSV: {e}", exc_info=True)
            raise
    
    def get_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcola statistiche sui dati estratti.
        
        Args:
            data: DataFrame con i dati
            
        Returns:
            Dizionario con le statistiche
        """
        stats = {
            'totale_record': len(data),
            'periodi_coperti': None,
            'province_presenti': None,
            'totale_imprese': None,
            'media_imprese': None
        }
        
        if 'periodo' in data.columns:
            periods = data['periodo'].unique()
            if len(periods) > 0:
                stats['periodi_coperti'] = f"{min(periods)} - {max(periods)}"
        
        if 'provincia' in data.columns:
            stats['province_presenti'] = data['provincia'].nunique()
        
        if 'num_imprese_attive' in data.columns:
            stats['totale_imprese'] = int(data['num_imprese_attive'].sum())
            stats['media_imprese'] = int(data['num_imprese_attive'].mean())
            stats['min_imprese'] = int(data['num_imprese_attive'].min())
            stats['max_imprese'] = int(data['num_imprese_attive'].max())
        
        return stats
    
    def __del__(self):
        """Cleanup quando l'oggetto viene distrutto."""
        self._close_driver()