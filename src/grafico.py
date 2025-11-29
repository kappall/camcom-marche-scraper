import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def periodo_year(p):
    """Estrae solo l'anno dal periodo"""
    return int(p[:4])

def plot_data(file_path: str):
    # Leggi il CSV
    df = pd.read_csv(file_path)

    # Ordina i dati per anno
    df['anno'] = df['periodo'].map(periodo_year)
    df = df.sort_values('anno')

    # Crea il grafico
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['anno'], df['num_imprese_attive'], marker='o', linestyle='-')

    # Etichette e titolo
    ax.set_title('Numero di imprese attive per provincia di Venezia')
    ax.set_xlabel('Anno')
    ax.set_ylabel('Numero imprese attive')

    # Intervallo Y ogni 1000
    min_val = df['num_imprese_attive'].min() // 1000 * 1000
    max_val = (df['num_imprese_attive'].max() // 1000 + 1) * 1000
    ax.set_ylim(min_val, max_val)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1000))

    # Mostra griglia e allinea X
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xticks(df['anno'])
    ax.set_xticklabels(df['anno'], rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera grafico da CSV")
    parser.add_argument('-f', '--file', required=True, help="Path del CSV di input")
    args = parser.parse_args()
    plot_data(args.file)
