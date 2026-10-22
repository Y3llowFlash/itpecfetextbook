/** Server-side overlays leave the released source files and native wording intact. */
import { createHash } from 'node:crypto';
import type { Concept, Question } from './models';
const sha=(text:string)=>createHash('sha256').update(text).digest('hex');
export function passageMatch(html:string, id:string) {
  if(!/^[a-zA-Z0-9_-]+$/.test(id))throw Error('Invalid passage ID');
  return new RegExp(`(<p\\b[^>]*\\bid="${id}"[^>]*>)([\\s\\S]*?)(<\\/p>)`).exec(html);
}
export function applyQuestionHighlights(html:string, concepts:Concept[], bank:Question[]) {
  for(const concept of concepts){
    const count=new Set(bank.filter(q=>q.is_published===true&&concept.questionIds.includes(q.id)).map(q=>q.id)).size;
    const overlay=concept.sourceHighlight;
    if(overlay){
      const match=passageMatch(html,overlay.passageId);
      if(!match)continue; // This source section does not own the passage.
      if(!count || sha(match[2])!==overlay.fragmentSha256 || /<a\b/.test(match[2]))throw Error(`Reviewed highlight passage changed: ${concept.id}`);
      html=html.replace(match[0],`${match[1]}<a class="concept-highlight" id="concept-${concept.id}" data-concept="${concept.id}" href="/practice/${concept.id}/">${match[2]}<span class="concept-count"> · ${count} questions</span></a>${match[3]}`);
    }
    html=html.replace(new RegExp(`(<a\\b[^>]*data-concept="${concept.id}"[^>]*>)([\\s\\S]*?)(<\\/a>)`,'g'),(_,open,body,close)=>`${open}${body.replace(/<span class="concept-count"[^>]*>[\s\S]*?<\/span>/g,`<span class="concept-count" aria-label="${count} published questions"> · ${count} ${count===1?'question':'questions'}</span>`)}${close}`);
  }
  return html;
}
