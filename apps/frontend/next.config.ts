import type { NextConfig } from "next";

// Orígenes externos confiables para la Política de Seguridad de Contenido (CSP).
// Al agregar un servicio externo nuevo (Analytics, Sentry, etc.) también debes
// incluir su dominio aquí, de lo contrario el navegador bloqueará la petición.
const BACKEND_ORIGIN = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const SUPABASE_WILDCARD = "https://*.supabase.co";
const GOOGLE_FONTS_STYLES = "https://fonts.googleapis.com";
const GOOGLE_FONTS_STATIC = "https://fonts.gstatic.com";

/**
 * Construye el valor de la cabecera Content-Security-Policy como una sola línea.
 * Cada directiva define qué tipo de recurso puede cargarse y desde qué orígenes.
 */
function buildCsp(): string {
  const directives: string[] = [
    // Política base: solo nuestro propio dominio si no hay regla específica.
    "default-src 'self'",

    // Scripts: 'unsafe-eval' e 'unsafe-inline' son necesarios para Next.js
    // (HMR en desarrollo y la hidratación de React en producción con inline scripts).
    "script-src 'self' 'unsafe-eval' 'unsafe-inline'",

    // Estilos: admite estilos inline (requeridos por Tailwind y muchos componentes)
    // y las hojas de estilo de Google Fonts.
    `style-src 'self' 'unsafe-inline' ${GOOGLE_FONTS_STYLES}`,

    // Fuentes tipográficas: solo de nuestro host y de los servidores de Google Fonts.
    `font-src 'self' ${GOOGLE_FONTS_STATIC}`,

    // Imágenes: nuestro host + blobs/data URIs (avatares generados) + Supabase Storage.
    `img-src 'self' blob: data: ${SUPABASE_WILDCARD}`,

    // Peticiones de red (fetch/XHR/WebSocket):
    // - nuestro propio host (Next.js API routes)
    // - el backend FastAPI
    // - la REST API y Auth de Supabase
    `connect-src 'self' ${BACKEND_ORIGIN} ${SUPABASE_WILDCARD}`,

    // Medios (audio/video): solo nuestro propio host.
    "media-src 'self'",

    // Objetos embebidos (Flash, plugins): ninguno permitido.
    "object-src 'none'",

    // Evita que nuestro sitio sea embebido en un <iframe> de cualquier origen
    // (Clickjacking). Equivalente moderno de X-Frame-Options.
    "frame-ancestors 'none'",

    // En producción, fuerza HTTPS para recursos que se soliciten por HTTP.
    "upgrade-insecure-requests",
  ];

  return directives.join("; ");
}

const securityHeaders = [
  {
    // Política de Seguridad de Contenido: previene XSS, data injection y Clickjacking.
    key: "Content-Security-Policy",
    value: buildCsp(),
  },
  {
    // Prevención de XSS en navegadores antiguos (IE/Edge legacy): bloquea la
    // página completa si se detecta un ataque reflejado en la URL.
    key: "X-XSS-Protection",
    value: "1; mode=block",
  },
  {
    // Impide Clickjacking en navegadores que aún no soportan frame-ancestors.
    key: "X-Frame-Options",
    value: "DENY",
  },
  {
    // Evita que el navegador "adivine" el tipo de contenido (MIME Sniffing),
    // lo que podría permitir que un archivo de texto se ejecute como script.
    key: "X-Content-Type-Options",
    value: "nosniff",
  },
];

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        // Aplica las cabeceras de seguridad a todas las rutas de la aplicación.
        source: "/(.*)",
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;

