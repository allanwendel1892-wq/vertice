export default async function handler(req, res) {
  // 1. Habilita liberação de CORS para o seu frontend ler os dados da matriz
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const targetUrl = req.query.url;

  if (!targetUrl) {
    return res.status(400).json({ error: "Parâmetro URL da base de dados ausente." });
  }

  try {
    const fetchResponse = await fetch(targetUrl, {
      headers: {
        // 2. Falsificação estrita de User-Agent para evitar o bloqueio em nuvem
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/csv,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
      }
    });

    if (!fetchResponse.ok) {
      return res.status(fetchResponse.status).send(`Erro no Provedor Alvo: ${fetchResponse.statusText}`);
    }

    const csvData = await fetchResponse.text();
    
    // 3. Devolve os dados brutos pro seu HTML injetar no Algoritmo Poisson
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.status(200).send(csvData);
    
  } catch (error) {
    res.status(500).json({ error: "Falha catastrófica no motor proxy: " + error.message });
  }
}
