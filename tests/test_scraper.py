"""
Test suite per il modulo scraper
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scraper import CamcomScraper
from utils import load_config


@pytest.fixture
def config():
    """Fixture per la configurazione di test."""
    return {
        "api": {
            "base_url": "https://opendata.marche.camcom.it",
            "timeout": 30,
            "max_retries": 3
        },
        "output": {
            "csv_directory": "tests/data/processed",
            "raw_directory": "tests/data/raw",
            "cache_directory": "tests/data/cache"
        },
        "extraction": {
            "default_start_year": 2020,
            "default_end_year": 2023
        }
    }


@pytest.fixture
def scraper(config):
    """Fixture per lo scraper."""
    return CamcomScraper(config=config, use_cache=False)


class TestCamcomScraper:
    """Test per la classe CamcomScraper."""
    
    def test_initialization(self, scraper):
        """Test inizializzazione scraper."""
        assert scraper is not None
        assert scraper.config is not None
        assert scraper.api_client is not None
        assert scraper.processor is not None
    
    def test_list_regions(self, scraper):
        """Test elenco regioni."""
        regions = scraper.list_regions()
        assert isinstance(regions, list)
        assert len(regions) > 0
        assert "Veneto" in regions
    
    def test_list_provinces(self, scraper):
        """Test elenco province."""
        provinces = scraper.list_provinces()
        assert isinstance(provinces, dict)
        assert "Veneto" in provinces
        assert "Venezia" in provinces["Veneto"]
    
    def test_get_province_code(self, scraper):
        """Test ottenimento codice provincia."""
        code = scraper._get_province_code("venezia")
        assert code == "VE"
        
        code = scraper._get_province_code("roma")
        assert code == "RM"
        
        code = scraper._get_province_code("nonexistent")
        assert code is None
    
    def test_cache_path_generation(self, scraper):
        """Test generazione path cache."""
        path = scraper._get_cache_path("venezia", 2020, 2023)
        assert isinstance(path, Path)
        assert "venezia" in str(path).lower()
        assert "2020" in str(path)
        assert "2023" in str(path)
    
    @pytest.mark.skipif(
        not Path("tests/data/sample_data.json").exists(),
        reason="Sample data not available"
    )
    def test_extract_data_with_sample(self, scraper):
        """Test estrazione dati con dati di esempio."""
        # Questo test richiede dati di esempio
        data = scraper.extract_data(
            provincia="venezia",
            anno_inizio=2020,
            anno_fine=2020
        )
        
        if data is not None:
            assert isinstance(data, pd.DataFrame)
            assert len(data) > 0
    
    def test_statistics_calculation(self, scraper):
        """Test calcolo statistiche."""
        # Crea un DataFrame di esempio
        sample_data = pd.DataFrame({
            'anno': [2020, 2021, 2022],
            'provincia': ['Venezia', 'Venezia', 'Venezia'],
            'num_imprese_attive': [1000, 1050, 1100],
            'settore_ateco': ['C', 'C', 'C']
        })
        
        stats = scraper.get_statistics(sample_data)
        
        assert 'totale_record' in stats
        assert stats['totale_record'] == 3
        assert 'totale_imprese' in stats
        assert stats['totale_imprese'] == 3150


class TestDataValidation:
    """Test per la validazione dei dati."""
    
    def test_year_range_validation(self):
        """Test validazione range anni."""
        from utils import validate_year_range
        
        assert validate_year_range(2020, 2023) == True
        assert validate_year_range(2023, 2020) == False
        assert validate_year_range(1990, 2023) == False
        assert validate_year_range(2020, 2030) == False
    
    def test_province_name_normalization(self):
        """Test normalizzazione nomi province."""
        from utils import get_province_name_normalized
        
        assert get_province_name_normalized("Venezia") == "venezia"
        assert get_province_name_normalized("VENEZIA") == "venezia"
        assert get_province_name_normalized("  Venezia  ") == "venezia"


@pytest.mark.integration
class TestIntegration:
    """Test di integrazione (richiedono connessione internet)."""
    
    @pytest.mark.slow
    def test_real_data_extraction(self, scraper):
        """Test estrazione dati reali (lento)."""
        data = scraper.extract_data(
            provincia="trieste",
            anno_inizio=2023,
            anno_fine=2023
        )
        
        if data is not None:
            assert isinstance(data, pd.DataFrame)
            assert len(data) > 0
            assert 'provincia' in data.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])