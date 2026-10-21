import definitions from '../content/hardware-lessons.json' with { type: 'json' };
import editions from '../content/textbook-editions.json' with { type: 'json' };
export interface LessonHeading { id: string; title: string; level: number; pages: number[] }
export interface HardwareLesson {
  id: string; slug: string; title: string; description: string; number: string;
  editionId: string; pages: number[]; headings: LessonHeading[];
}
export const hardwareLessons = definitions as HardwareLesson[];
export const lessonPath = (lesson: HardwareLesson) => `/chapters/hardware/${lesson.slug}/`;
export const lessonForPath = (path: string) => hardwareLessons.find((lesson) => lessonPath(lesson) === path);
export const pageLabel = (pages: number[]) => pages.length === 1 || pages[0] === pages[1] ? `p. ${pages[0]}` : `pp. ${pages[0]}–${pages[1]}`;
export const editionLabel = `${editions[0].title} · ${editions[0].volume} · ${editions[0].edition}`;

/** Only authored Markdown is rendered; reference badges use verified metadata. */
export function annotateLesson(html: string, lesson: HardwareLesson, counts: Map<string, number>) {
  for (const heading of lesson.headings) {
    const pattern = new RegExp(`(<h${heading.level}\\b[^>]*\\bid="${heading.id}"[^>]*>[\\s\\S]*?<\\/h${heading.level}>)`);
    if (!pattern.test(html)) throw new Error(`Missing source heading: ${lesson.slug}/${heading.id}`);
    html = html.replace(pattern, `$1<p class="source-badge" data-source-ref="${heading.id}" title="${editionLabel}">Original textbook · ${pageLabel(heading.pages)}</p>`);
  }
  html = html.replace(/(<a\b[^>]*data-concept="([a-z0-9-]+)"[^>]*>)([\s\S]*?)(<\/a>)/g, (_, open, id, text, close) => {
    const count = counts.get(id);
    if (!count) throw new Error(`Unreviewed highlight: ${id}`);
    return `${open}${text}<span class="concept-count"> · ${count} ${count === 1 ? 'question' : 'questions'}</span>${close}`;
  });
  return html;
}
