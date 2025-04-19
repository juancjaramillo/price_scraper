#!/usr/bin/env python3
# price_scraper.py

# 1) Fuerza el backend Agg **antes** de importar matplotlib.pyplot
import matplotlib
matplotlib.use('Agg')

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse
import re

def scrape_price(url, selector):
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    elem = soup.select_one(selector)
    if not elem:
        raise ValueError(f"No se encontró el elemento con selector '{selector}'")
    text = elem.get_text().strip()
    cleaned = re.sub(r'[^\d\.]', '', text)
    if not cleaned:
        raise ValueError(f"No se pudo extraer un número de '{text}'")
    return float(cleaned)

def append_price_to_csv(path, timestamp, price):
    existe = os.path.isfile(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(['timestamp', 'price'])
        writer.writerow([timestamp.isoformat(), price])

def plot_price_history(path):
    """
    Lee el CSV y guarda un gráfico de precio vs fecha en 'price_history.png'.
    Ya no usa plt.show(), solo plt.savefig().
    """
    df = pd.read_csv(path, parse_dates=['timestamp'])
    plt.figure(figsize=(10,5))
    plt.plot(df['timestamp'], df['price'], marker='o')
    plt.xlabel('Fecha')
    plt.ylabel('Precio')
    plt.title('Evolución del Precio')
    plt.grid(True)
    plt.gcf().autofmt_xdate()

    out_file = 'price_history.png'
    plt.savefig(out_file, dpi=150)
    print(f"📈 Gráfico guardado en ./{out_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Scrapea precio de un producto y guarda su evolución gráfica.")
    parser.add_argument('url', help='URL del producto')
    parser.add_argument('selector', help='Selector CSS del elemento precio')
    parser.add_argument('--csv', default='price_history.csv',
                        help='CSV de historial (default: price_history.csv)')
    args = parser.parse_args()

    ahora = datetime.now()
    try:
        precio = scrape_price(args.url, args.selector)
        print(f"[{ahora:%Y-%m-%d %H:%M:%S}] Precio: {precio}")
        append_price_to_csv(args.csv, ahora, precio)
        plot_price_history(args.csv)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
