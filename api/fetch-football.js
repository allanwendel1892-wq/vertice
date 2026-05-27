export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET');

    const targetUrl = req.query.url || 'https://www.football-data.co.uk/mmz4281/2526/E0.csv';

    try {
        const response = await fetch(targetUrl, {
            method: 'GET',
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
        });

        if (!response.ok) {
            return res.status(response.status).send(`Erro na fonte original: ${response.statusText}`);
        }

        const csvData = await response.text();
        res.setHeader('Content-Type', 'text/csv; charset=utf-8');
        return res.status(200).send(csvData);
    } catch (error) {
        return res.status(500).send('Erro interno no proxy: ' + error.message);
    }
}
