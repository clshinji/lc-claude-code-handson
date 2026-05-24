/**
 * Cloudflare Pages middleware: 全リクエストに HTTP Basic Auth をかける。
 *
 * 認証情報は Cloudflare Pages の環境変数 / Secret で渡す:
 *   - BASIC_AUTH_USER (デフォルト "handson")
 *   - BASIC_AUTH_PASS (必須)
 *
 * `wrangler pages secret put BASIC_AUTH_PASS --project-name <name>` で登録。
 */
interface Env {
  BASIC_AUTH_USER?: string;
  BASIC_AUTH_PASS?: string;
}

const REALM = 'lc-handson';

function unauthorized(): Response {
  return new Response('Authentication required.\n', {
    status: 401,
    headers: {
      'WWW-Authenticate': `Basic realm="${REALM}", charset="UTF-8"`,
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-store',
    },
  });
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

export const onRequest: PagesFunction<Env> = async ({ request, env, next }) => {
  const user = env.BASIC_AUTH_USER ?? 'handson';
  const pass = env.BASIC_AUTH_PASS ?? '';

  if (!pass) {
    return new Response(
      'Server misconfigured: BASIC_AUTH_PASS is not set.\n',
      { status: 500, headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
    );
  }

  const header = request.headers.get('Authorization') ?? '';
  if (!header.startsWith('Basic ')) return unauthorized();

  let decoded: string;
  try {
    decoded = atob(header.slice('Basic '.length));
  } catch {
    return unauthorized();
  }

  const idx = decoded.indexOf(':');
  if (idx < 0) return unauthorized();
  const givenUser = decoded.slice(0, idx);
  const givenPass = decoded.slice(idx + 1);

  if (!timingSafeEqual(givenUser, user) || !timingSafeEqual(givenPass, pass)) {
    return unauthorized();
  }

  return next();
};
