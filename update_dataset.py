import pandas as pd
import cloudscraper
from io import StringIO
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================
CSV_PATH = 'campeonato-brasileiro-full.csv'
FBREF_URL = 'https://fbref.com/en/comps/24/schedule/Serie-A-Scores-and-Fixtures'

TEAM_MAPPING = {
    'Athletico Paranaense': 'Athletico PR',
    'Atlético Mineiro': 'Atletico MG',
    'Atlético Goianiense': 'Atletico GO',
    'Botafogo (RJ)': 'Botafogo RJ',
    'Corinthians': 'Corinthians',
    'Flamengo': 'Flamengo',
    'Fluminense': 'Fluminense',
    'Grêmio': 'Gremio',
    'Internacional': 'Internacional',
    'Palmeiras': 'Palmeiras',
    'Red Bull Bragantino': 'Bragantino',
    'São Paulo': 'Sao Paulo',
    'Vasco da Gama': 'Vasco',
    'Vitória': 'Vitoria',
    'Juventude': 'Juventude',
    'Criciúma': 'Criciuma',
    'Cuiabá': 'Cuiaba',
    'Fortaleza': 'Fortaleza',
    'Cruzeiro': 'Cruzeiro',
    'Bahia': 'Bahia'
}

def get_fbref_data():
    print("Iniciando extração evasiva do FBref...")
    
    # Cria o scraper mascarando a conexão como um navegador real
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    response = scraper.get(FBREF_URL)
    response.raise_for_status()
    
    tables = pd.read_html(StringIO(response.text))
    df_fbref = tables[0]
    
    df_played = df_fbref.dropna(subset=['Score']).copy()
    
    scores = df_played['Score'].astype(str).str.replace('–', '-').str.split('-', expand=True)
    df_played['FTHG'] = pd.to_numeric(scores[0], errors='coerce')
    df_played['FTAG'] = pd.to_numeric(scores[1], errors='coerce')
    
    df_clean = pd.DataFrame({
        'Date': pd.to_datetime(df_played['Date']).dt.strftime('%Y-%m-%d'),
        'HomeTeam': df_played['Home'].map(TEAM_MAPPING).fillna(df_played['Home']),
        'AwayTeam': df_played['Away'].map(TEAM_MAPPING).fillna(df_played['Away']),
        'FTHG': df_played['FTHG'],
        'FTAG': df_played['FTAG']
    })
    
    df_clean = df_clean.dropna(subset=['FTHG', 'FTAG'])
    return df_clean

def merge_and_save(new_data):
    print("Processando fusão com base histórica...")
    
    if os.path.exists(CSV_PATH):
        try:
            df_history = pd.read_csv(CSV_PATH)
        except Exception as e:
            print(f"Erro ao ler o CSV histórico: {e}")
            return
    else:
        print("CSV histórico não encontrado. Criando um novo.")
        df_history = pd.DataFrame(columns=['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])

    df_combined = pd.concat([df_history, new_data], ignore_index=True)
    df_final = df_combined.drop_duplicates(subset=['Date', 'HomeTeam'], keep='last')
    
    df_final.to_csv(CSV_PATH, index=False)
    print(f"Sucesso! Base atualizada. Total de partidas na base: {len(df_final)}")

if __name__ == "__main__":
    try:
        recent_matches = get_fbref_data()
        merge_and_save(recent_matches)
    except Exception as e:
        print(f"Erro na execução do script: {e}")
        exit(1)
