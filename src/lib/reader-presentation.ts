/** Presentation only: generated badges and heading tags; source words/IDs stay exact. */
export function presentSourceHTML(html:string,chapterStart=false){
  html=html.replace(/(<p class="source-badge"[^>]*>)Original textbook · /g,'$1')
    .replace(/aria-label="Original textbook · /g,'aria-label="')
    .replace(/(<figcaption>)Original textbook · /g,'$1');
  html=html.replace(/<(\/?)(h[234])\b/g,(_,close,tag:string)=>`<${close}h${Number(tag[1])-(chapterStart?0:1)}`);
  return html.replace(/(<h[1234]\b[^>]*data-source-kind="heading")/g,'$1 tabindex="-1"');
}
