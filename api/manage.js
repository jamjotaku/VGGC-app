import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
})

export default async function handler(req, res) {
  const { userId } = req.query;
  if (!userId) return res.status(400).json({ error: "No User ID" });

  const key = `vggc_${userId}`;

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