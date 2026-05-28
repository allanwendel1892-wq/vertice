import re
import time
from collections import defaultdict
from seleniumbase import Driver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
import numpy as np

add_printer(1)

# Inicializa o Driver com UC ativo em modo visível dentro do xvfb
driver = Driver(uc=True, headless=False)

try:
    print("Iniciando acesso ao site da Betano...")
    driver.get("https://br.betano.com/sport/futebol/brasil/brasileirao-serie-a/10016/")
    
    # Aguarda 12 segundos para garantir a renderização completa e passar checagens iniciais
    time.sleep(12)
    
    # Valida se caiu na tela de bloqueio do Cloudflare
    conteudo_pagina = driver.page_source.lower()
    if "cloudflare" in conteudo_pagina or "just a moment" in conteudo_pagina:
        print("Erro: Bloqueado pela proteção anti-bot da Betano.")
        exit(1)

    print("Buscando estrutura de dados...")
    df = get_df(
        driver,
        By,
        WebDriverWait,
        EC,
        queryselector="section",
        with_methods=True,
    )
    
    if df.empty:
        print("Erro: Nenhum elemento de dados foi retornado.")
        exit(1)

    texto = df.loc[
        df.aa_className.str.contains("grid__column", regex=False, na=False)
    ].aa_innerText.iloc[0]
    
    df_dados = pd.DataFrame(texto.splitlines())
    df_dados = df_dados.loc[
        df_dados.loc[
            df_dados[0].str.contains(r"Brasileirão\s+-\s+Série\s+A", regex=True, na=False)
        ].index[-1]
        + 1 :
    ].reset_index(drop=True)
    
    df_dados[0] = df_dados[0].str.strip()
    allbets = np.array_split(df_dados, df_dados.loc[df_dados[0].str.contains(r"^\d\d/\d\d$")].index)
    d = defaultdict(list)
    for bet in allbets:
        d[len(bet)].append(bet)
        
    df_final = pd.concat(
        [q.reset_index(drop=True) for q in d[sorted(d)[-1]]], axis=1, ignore_index=True
    )

    try:
        df_final = df_final.loc[np.setdiff1d(df_final.index, df_final[df_final == 'SO'].dropna().index)].reset_index(drop=True)
    except Exception:
        pass 

    df_final = df_final.loc[
        np.setdiff1d(
            df_final.index,
            df_final.applymap(lambda x: re.match("resultado|total|ambas", str(x), flags=re.I))
            .dropna(how="all")
            .index,
        )
    ].reset_index(drop=True)[:7]
    
    df_final = df_final.T
    df_final.columns = ["data", "hora", "team1_nome", "team2_nome", "team1", "empate", "team2"]
    df_final = df_final.astype({"team1": "Float64", "empate": "Float64", "team2": "Float64"})

    # Gravação real do arquivo esperado pela Vercel
    df_final.to_csv('proximos_jogos_betano.csv', index=False)
    print("Sucesso: arquivo proximos_jogos_betano.csv gerado com dados estruturados!")

except Exception as erro:
    print(f"Falha crítica na execução do scraper: {erro}")
    exit(1)
finally:
    driver.quit()
