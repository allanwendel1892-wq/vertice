export default async function handler(req, res) {
    // Configura cabeçalhos de CORS para permitir que seu frontend acesse a rota com segurança
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    // Pega a URL do CSV enviada por parâmetro ou usa a padrão da Premier League
    const targetUrl = req.query.url || 'https://www.football-data.co.uk/mmz4281/2526/E0.csv';

    try {
        const response = await fetch(targetUrl, {
            method: 'GET',
            headers: {
                // Emula um navegador real para passar direto pelo bloqueio da Cloudflare
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
        });

        if (!response.ok) {
            return res.status(response.status).json({ 
                error: `A fonte original respondeu com erro ${response.status}: ${response.statusText}` 
            });
        }

        const csvData = await response.text();
        
        // Define o tipo de conteúdo como CSV e envia os dados limpos para o front
        res.setHeader('Content-Type', 'text/csv; charset=utf-8');
        return res.status(200).send(csvData);

    } catch (error) {
        return res.status(500).json({ error: 'Erro interno no proxy da Vercel: ' + error.message });
    }
}
