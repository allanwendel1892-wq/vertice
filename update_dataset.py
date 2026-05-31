import pandas as pd
import requests
from io import StringIO
import os

# ==========================================
# CONFIGURAÇÕES
# ==========================================
CSV_PATH = 'campeonato-brasileiro-full.csv'
# URL do FBref com o calendário e resultados da Série A 2026
FBREF_URL = 'https://fbref.com/en/comps/24/schedule/Serie-A-Scores-and-Fixtures'

# Dicionário para padronizar os nomes do FBref com a sua base histórica
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
    # Adicione os times que subiram da Série B em 2025/2026 conforme necessário
}

def get_fbref_data():
    """Faz o scraping da tabela de jogos do FBref."""
    print("Iniciando extração do FBref...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(FBREF_URL, headers=headers)
    response.raise_for_status()
    
    # Extrai todas as tabelas da página
    tables = pd.read_html(StringIO(response.text))
    df_fbref = tables[0] # A primeira tabela é o calendário de jogos
    
    # Filtra apenas jogos que já acontecerScore (Score não é nulo)
    df_played = df_fbref.dropna(subset=['Score']).copy()
    
    # O FBref usa um en-dash '–' ou hyphen '-' para separar o placar.
    # Precisamos dividir a coluna 'Score' (ex: '2–1') em FTHG e FTAG
    scores = df_played['Score'].astype(str).str.replace('–', '-').str.split('-', expand=True)
    df_played['FTHG'] = pd.to_numeric(scores[0], errors='coerce')
    df_played['FTAG'] = pd.to_numeric(scores[1], errors='coerce')
    
    # Seleciona e renomeia as colunas para o seu schema
    df_clean = pd.DataFrame({
        'Date': pd.to_datetime(df_played['Date']).dt.strftime('%Y-%m-%d'),
        'HomeTeam': df_played['Home'].map(TEAM_MAPPING).fillna(df_played['Home']),
        'AwayTeam': df_played['Away'].map(TEAM_MAPPING).fillna(df_played['Away']),
        'FTHG': df_played['FTHG'],
        'FTAG': df_played['FTAG']
    })
    
    # Remove qualquer jogo onde não foi possível converter o placar
    df_clean = df_clean.dropna(subset=['FTHG', 'FTAG'])
    
    return df_clean

def merge_and_save(new_data):
    """Funde os dados novos com o CSV histórico sem criar duplicatas."""
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

    # Combina os dois DataFrames
    df_combined = pd.concat([df_history, new_data], ignore_index=True)
    
    # O Pulo do Gato (Idempotência):
    # Removemos duplicatas checando se já existe uma partida na mesma Data com o mesmo Mandante.
    # Mantemos o último registro (keep='last'), garantindo que atualizações de placar (se houver) prevaleçam.
    df_final = df_combined.drop_duplicates(subset=['Date', 'HomeTeam'], keep='last')
    
    # Salva de volta no arquivo
    df_final.to_csv(CSV_PATH, index=False)
    print(f"Sucesso! Base atualizada. Total de partidas na base: {len(df_final)}")

if __name__ == "__main__":
    try:
        recent_matches = get_fbref_data()
        merge_and_save(recent_matches)
    except Exception as e:
        print(f"Erro na execução do script: {e}")
        exit(1)
      
