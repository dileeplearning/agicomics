export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const slug = (url.searchParams.get('slug') || '').trim();
    const cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,OPTIONS',
      'Access-Control-Allow-Headers': 'content-type',
      'Cache-Control': 'no-store',
    };
    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (!slug) return json({ error: 'missing slug' }, cors, 400);
    const key = `slug:${slug}`;
    if (url.pathname.endsWith('/likes')) {
      const v = await env.LIKES.get(key);
      const count = Number(v || 0);
      return json({ slug, count }, cors);
    }
    if (url.pathname.endsWith('/hit')) {
      const v = await env.LIKES.get(key);
      let count = Number(v || 0) + 1;
      await env.LIKES.put(key, String(count));
      return json({ slug, count }, cors);
    }
    return new Response('Not Found', { status: 404, headers: cors });
  },
};

function json(data, headers = {}, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8', ...headers } });
}

// Bind Workers KV in wrangler:
// [[kv_namespaces]]
// binding = "LIKES"
// id = "<your_kv_namespace_id>"
