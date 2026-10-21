import proseRepairs from '../content/hardware-prose-repairs.json';

/** Restore reviewed source paragraphs while retaining every original word anchor. */
export function repairSourceParagraphs(html:string){
 for(const group of proseRepairs.paragraphs){
  const start=html.indexOf(`<p id="${group.firstId}"`);
  if(start<0)continue;
  const last=html.indexOf(`<p id="${group.lastId}"`,start);
  const end=last<0?-1:html.indexOf('</p>',last)+4;
  if(last<0||end<4)throw new Error(`Incomplete reviewed prose run: ${group.id}`);
  const source=html.slice(start,end);
  const fragments=[...source.matchAll(/<p\b([^>]*)>([\s\S]*?)<\/p>/g)];
  if(fragments.length!==group.fragmentCount||fragments.map(match=>match[0]).join('')!==source||fragments.some(match=>!match[1].includes('data-source-kind="paragraph"')))
   throw new Error(`Source prose structure changed: ${group.id}`);
  const paragraph=`<p data-source-paragraph="${group.id}">${fragments.map(match=>`<span${match[1]}>${match[2]}</span>`).join(' ')}</p>`;
  html=html.slice(0,start)+paragraph+html.slice(end);
 }
 return html;
}

/** Presentation only: source words, block IDs and asset paths stay exact. */
export function presentSourceHTML(html:string,chapterStart=false){
  html=repairSourceParagraphs(html);
  html=html.replace(/(<p class="source-badge"[^>]*>)Original textbook · /g,'$1')
    .replace(/aria-label="Original textbook · /g,'aria-label="')
    .replace(/(<figcaption>)Original textbook · /g,'$1');
  html=html.replace(/<(\/?)(h[234])\b/g,(_,close,tag:string)=>`<${close}h${Number(tag[1])-(chapterStart?0:1)}`);
  return html.replace(/(<h[1234]\b[^>]*data-source-kind="heading")/g,'$1 tabindex="-1"');
}
