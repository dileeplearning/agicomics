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
    // oEmbed endpoint: /oembed?url=...
    if (url.pathname.endsWith('/oembed')) {
      const target = url.searchParams.get('url') || '';
      if (!target) return json({ error: 'missing url' }, cors, 400);
      try {
        const res = await fetch(target, { redirect: 'follow' });
        if (!res.ok) return json({ error: 'fetch_failed' }, cors, 502);
        const html = await res.text();
        const og = extractOG(html);
        // Build minimal oEmbed (photo type) using OG image as the content
        const provider_name = env.PROVIDER_NAME || 'AGI Comics';
        const provider_url = env.PROVIDER_URL || 'https://dileeplearning.github.io/agicomics/';
        const out = {
          version: '1.0',
          type: 'photo',
          provider_name,
          provider_url,
          title: og.title || 'AGI Comics',
          url: og.image || target,
        };
        if (og.width) out.width = og.width;
        if (og.height) out.height = og.height;
        if (og.url) out.author_url = og.url;
        return json(out, { ...cors, 'Content-Type': 'application/json; charset=utf-8' });
      } catch (e) {
        return json({ error: 'exception', message: String(e) }, cors, 500);
      }
    }

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

function extractOG(html) {
  const out = {};
  function m(re) { const r = html.match(re); return r ? r[1] : null; }
  out.title = m(/<meta[^>]+property=["']og:title["'][^>]+content=["']([^"']+)["'][^>]*>/i) || m(/<title>([^<]+)<\/title>/i);
  out.image = m(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["'][^>]*>/i);
  out.url = m(/<meta[^>]+property=["']og:url["'][^>]+content=["']([^"']+)["'][^>]*>/i);
  const w = m(/<meta[^>]+property=["']og:image:width["'][^>]+content=["'](\d+)["'][^>]*>/i);
  const h = m(/<meta[^>]+property=["']og:image:height["'][^>]+content=["'](\d+)["'][^>]*>/i);
  if (w) out.width = Number(w);
  if (h) out.height = Number(h);
  return out;
}

// Bind Workers KV in wrangler:
// [[kv_namespaces]]
// binding = "LIKES"
// id = "<your_kv_namespace_id>"
