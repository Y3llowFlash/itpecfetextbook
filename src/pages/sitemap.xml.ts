import type { APIRoute } from 'astro';
import { hardwareLessons, lessonPath } from '../lib/lessons';
import { concepts } from '../lib/catalog';
export const GET: APIRoute = ({ site }) => new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${['/', '/chapters/hardware/', ...hardwareLessons.map(lessonPath), ...concepts.map((concept) => `/practice/${concept.id}/`)].map((route) => `<url><loc>${new URL(route, site)}</loc></url>`).join('')}</urlset>`, { headers: { 'Content-Type': 'application/xml' } });
