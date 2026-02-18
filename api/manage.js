import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
})

export default async function handler(req, res) {
  const { userId, type } = req.query;
  const key = type === 'catalog' ? 'vggc_catalog' : `vggc_${userId}`;

  // 【重要】カタログの更新(POST)時のみパスワードをチェック
  if (req.method === 'POST' && type === 'catalog') {
    const password = req.headers['x-admin-password']; // ヘッダーからパスワード取得
    if (password !== process.env.ADMIN_PASSWORD) {
      return res.status(403).json({ error: "認証エラー：パスワードが違います" });
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