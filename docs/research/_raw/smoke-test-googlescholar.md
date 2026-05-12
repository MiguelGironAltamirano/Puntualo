# Evaluación de viabilidad — Google Scholar

**Fecha:** 2026-05-11
**Smoke test:** NO ejecutado. La evaluación es de viabilidad únicamente, dado que el plan original lo marcaba como evaluación-no-prueba.

## Acceso programático

- **API pública:** No existe. Google no provee una API oficial para Google Scholar (a diferencia de Search/Books).
- **robots.txt** (`https://scholar.google.com/robots.txt`):
  ```
  User-agent: *
  Disallow: /search
  Disallow: /index.html
  Disallow: /scholar
  Disallow: /citations?
  Allow: /citations?user=
  Disallow: /citations?*cstart=    # bloquea paginación
  Disallow: /citations?user=*@     # bloquea búsqueda por email
  ```
  - **Búsqueda por nombre prohibida** (`/scholar` y `/search` disallow).
  - **Perfil individual por ID** permitido (`/citations?user={id}`).
  - **Paginación bloqueada** (`*cstart=` disallow) — previene scraping masivo.

- **ToS:** prohíbe expresamente acceso automatizado a sus servicios. Fuente: condiciones generales Google + comportamiento documentado (Google bloquea con captcha tras pocas requests automatizadas).

## Implicación para Puntualo

No se puede:
- Buscar a un profesor por nombre desde Puntualo (action bloqueada).
- Hacer crawl masivo de perfiles UNMSM (paginación bloqueada).

Sí se puede (opcional):
- Fetch a un perfil específico si el profesor ya compartió su Scholar URL (en formato `https://scholar.google.com/citations?user={ID}`).
- Cuando Puntualo permita al profesor pegar su Scholar URL manualmente, almacenarla y desplegarla como link público en la ficha — sin scraping automatizado.

## Alternativas que entregan datos equivalentes

| Necesidad | Alternativa que sí cumple ToS |
|---|---|
| Publicaciones del profesor | OpenAlex API (gratis, sin cuota) |
| Citas y h-index | Semantic Scholar (libre) o OpenAlex |
| Áreas de investigación | OpenAlex `x_concepts` + ORCID `keywords` |
| Foto/perfil público | ORCID + UNMSM CV (PDF) |

Conclusión: **no perdemos cobertura significativa** descartando Google Scholar. OpenAlex+ORCID cubren los datos académicos importantes con APIs legales.

## Rol en pipeline

**Descartar para acceso automatizado.** Permitido únicamente como link manual:
- En la UI de Puntualo, opcionalmente, dejar un campo "Google Scholar URL" donde el propio profesor (o un admin) pegue el link. Almacenar como `external_links.google_scholar` sin scraping.
- NUNCA hacer requests programáticas a `scholar.google.com` desde el backend.

## Smoke test

No ejecutado. Por las razones documentadas, ningún resultado obtenido sería utilizable en pipeline automatizado.
