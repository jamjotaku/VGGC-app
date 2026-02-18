import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
})

export default async function handler(req, res) {
  const { userId, type } = req.query;

  // --- 【AI機能】Difyへのリクエスト中継 ---
  if (req.method === 'POST' && type === 'dify') {
    try {
      const { image } = req.body;
      const response = await fetch('https://api.dify.ai/v1/chat-messages', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.DIFY_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          inputs: {},
          query: "この画像から「配置番号,サークル名,種類,商品名,価格」を抽出してください",
          response_mode: "blocking",
          user: "vggc-admin",
          files: [{ type: "image", transfer_method: "base64", data: image }]
        })
      });
      const result = await response.json();
      return res.status(200).json(result);
    } catch (e) {
      return res.status(500).json({ error: "Dify通信エラー" });
    }
  }

  // --- 【データ機能】Redis処理 ---
  const key = type === 'catalog' ? 'vggc_catalog' : `vggc_${userId}`;

  if (req.method === 'POST' && type === 'catalog') {
    if (req.headers['x-admin-password'] !== process.env.ADMIN_PASSWORD) {
      return res.status(403).json({ error: "認証エラー" });
    }
  }

  try {
    if (req.method === 'GET') {
      const data = await redis.get(key);
      return res.status(200).json(data || []);
    }
    if (req.method === 'POST') {
      await redis.set(key, req.body);
      return res.status(200).json({ success: true });
    }
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}