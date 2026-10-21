import {contentsForPath} from './toc';

export function setupReaderNavigation(){
 const tools=document.querySelector<HTMLDetailsElement>('[data-study-tools]');
 const desktop=matchMedia('(min-width: 78rem)');
 const adapt=()=>{if(tools)tools.open=desktop.matches;};adapt();desktop.addEventListener('change',adapt);
 const reader=document.querySelector<HTMLElement>('[data-reader]');
 if(!reader)return()=>desktop.removeEventListener('change',adapt);
 const nodes=contentsForPath(reader.dataset.readerPath||location.pathname);
 const headings=nodes.map(node=>({node,element:document.getElementById(node.id)})).filter(item=>item.element);
 let active='',frame=0;
 const setActive=(id:string)=>{
  if(id===active)return;active=id;
  document.documentElement.dataset.readingContext=id;
  document.querySelectorAll<HTMLElement>('[data-toc-link]').forEach(link=>{
   if(link.dataset.tocLink===id){link.setAttribute('aria-current','location');let parent=link.parentElement;while(parent&&!parent.hasAttribute('data-mobile-contents')){if(parent instanceof HTMLDetailsElement)parent.open=true;parent=parent.parentElement;}}
   else link.removeAttribute('aria-current');
   link.toggleAttribute('data-active-section',link.dataset.tocSection===reader.dataset.sectionId);
  });
  window.dispatchEvent(new CustomEvent('itpec:reading-context',{detail:{id}}));
 };
 const update=()=>{frame=0;const selected=[...headings].reverse().find(item=>item.element!.getBoundingClientRect().top<=150)||headings[0];if(selected)setActive(selected.node.id);};
 const schedule=()=>{if(!frame)frame=requestAnimationFrame(update);};
 const click=(event:MouseEvent)=>{
  const target=event.target instanceof Element?event.target.closest<HTMLAnchorElement>('[data-toc-link]'):null;
  if(!target||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
  const id=target.dataset.tocLink!;
  document.querySelector<HTMLDetailsElement>('[data-mobile-contents]')?.removeAttribute('open');
  if(new URL(target.href).pathname===location.pathname)requestAnimationFrame(()=>document.getElementById(id)?.focus({preventScroll:true}));
 };
 const hash=()=>{const id=decodeURIComponent(location.hash.slice(1));if(nodes.some(node=>node.id===id))setActive(id);schedule();};
 window.addEventListener('scroll',schedule,{passive:true});window.addEventListener('resize',schedule);window.addEventListener('hashchange',hash);window.addEventListener('pageshow',schedule);document.addEventListener('click',click);
 hash();
 // A direct fragment can be positioned before the book fonts finish loading.
 // Re-align it once, without disturbing saved checkpoints or history restores.
 const initialHash=location.hash;
 const navigation=performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming|undefined;
 let interacted=false;
 const interact=()=>{interacted=true;};
 window.addEventListener('pointerdown',interact,{once:true});window.addEventListener('keydown',interact,{once:true});window.addEventListener('wheel',interact,{once:true,passive:true});
 void document.fonts.ready.then(()=>{
  if(initialHash&&location.hash===initialHash&&!interacted&&!new URLSearchParams(location.search).has('resume')&&navigation?.type!=='back_forward')document.getElementById(decodeURIComponent(initialHash.slice(1)))?.scrollIntoView({behavior:'instant',block:'start'});
  schedule();
 });
 if(location.hash==='#chapter-practice')location.replace('/practice/');
 return()=>{cancelAnimationFrame(frame);desktop.removeEventListener('change',adapt);window.removeEventListener('scroll',schedule);window.removeEventListener('resize',schedule);window.removeEventListener('hashchange',hash);window.removeEventListener('pageshow',schedule);window.removeEventListener('pointerdown',interact);window.removeEventListener('keydown',interact);window.removeEventListener('wheel',interact);document.removeEventListener('click',click);};
}
