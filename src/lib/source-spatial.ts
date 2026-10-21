import {createRequire} from 'node:module';
import crops from '../content/hardware-spatial-crops.json';

// Build-time presentation: source input files and historical reading IDs stay immutable.
const {JSDOM}=createRequire(import.meta.url)('jsdom') as {JSDOM:new(html:string)=>{window:{document:Document;close():void}}};
const anchorAttributes=['id','data-source-block','data-source-kind','data-reading-block'];
export function repairSpatialContent(html:string){
 const regions=crops.regions.filter(r=>html.includes(`id="${r.sourceBlockIds[0]}"`));
 if(!regions.length)return html;
 const dom=new JSDOM(html),doc=dom.window.document;
 const wrapNative=(element:HTMLElement)=>{
  if(element.tagName==='SPAN')return element;
  const span=doc.createElement('span');
  for(const attr of anchorAttributes){const value=element.getAttribute(attr);if(value!==null){span.setAttribute(attr,value);element.removeAttribute(attr);}}
  span.innerHTML=element.innerHTML;element.replaceChildren(span);return span;
 };
 try{
  for(const region of regions){
   const members=region.sourceBlockIds.map(id=>doc.getElementById(id));
   if(members.some(el=>!el))throw new Error(`Incomplete spatial source region: ${region.id}`);
   const figure=doc.createElement('figure');
   figure.className='source-crop';figure.id=`${crops.releaseId}-crop-${region.id}`;
   figure.setAttribute('data-reading-block','');figure.dataset.spatialCrop=region.id;
   figure.dataset.sourcePdfPage=String(region.pdfPage);figure.dataset.sourcePrintedPage=String(region.printedPage);
   figure.style.setProperty('--crop-width',`${Math.round((region.bbox[2]-region.bbox[0])*1.4)}px`);
   const first=members[0]!;
   const insertion=first.parentElement?.tagName==='UL'?first.parentElement:first;
   insertion.before(figure);
   for(const member of members){
    const source=member!,anchor=doc.createElement('span');
    for(const attr of anchorAttributes){const value=source.getAttribute(attr);if(value!==null)anchor.setAttribute(attr,value);}
    anchor.className='source-crop-anchor';anchor.dataset.sourceCrop=region.id;anchor.setAttribute('aria-hidden','true');
    figure.append(anchor);const parent=source.parentElement;source.remove();
    if(parent?.tagName==='UL'&&!parent.children.length)parent.remove();
   }
   const scroll=doc.createElement('div');scroll.className='source-crop-scroll';scroll.tabIndex=0;
   scroll.setAttribute('role','region');scroll.setAttribute('aria-label',`${region.alt}. Scroll horizontally if needed.`);
   const link=doc.createElement('a');link.href='/'+region.asset.path;link.target='_blank';link.rel='noopener';
   link.setAttribute('aria-label',`Enlarge original: ${region.alt} (opens image in a new tab)`);
   const image=doc.createElement('img');image.src=link.href;image.alt=region.alt;
   image.width=region.asset.width;image.height=region.asset.height;image.loading='lazy';image.decoding='async';
   link.append(image);scroll.append(link);figure.append(scroll);
   const caption=doc.createElement('figcaption');caption.append(`p. ${region.printedPage} · `);
   const enlarge=link.cloneNode(false) as HTMLAnchorElement;enlarge.textContent='Enlarge';caption.append(enlarge);figure.append(caption);
  }
  const recoveries=regions.flatMap<(typeof crops.regions)[number]['recoveries'][number]>(r=>r.recoveries);
  const recoverySpan=(record:typeof recoveries[number])=>{
   const span=doc.createElement('span');span.id=`${crops.releaseId}-${record.id}`;
   span.setAttribute('data-reading-block','');span.dataset.sourceRecovery=record.id;span.innerHTML=record.html;return span;
  };
  for(const targetId of new Set(recoveries.map(r=>r.targetId).filter((id):id is string=>!!id))){
   const native=wrapNative(doc.getElementById(targetId)!);
   const records=recoveries.filter(r=>r.targetId===targetId).sort((a,b)=>a.bbox[1]-b.bbox[1]||a.range[0]-b.range[0]);
   for(const record of records.filter(r=>r.placement==='before'))native.before(recoverySpan(record),doc.createTextNode(' '));
   let after:Node=native;
   for(const record of records.filter(r=>r.placement==='after')){const span=recoverySpan(record);after.parentNode!.insertBefore(doc.createTextNode(' '),after.nextSibling);after.parentNode!.insertBefore(span,after.nextSibling!.nextSibling);after=span;}
  }
  for(const region of regions){
   const orphaned=region.recoveries.filter(r=>!r.targetId);if(!orphaned.length)continue;
   const paragraph=doc.createElement('p');paragraph.dataset.sourceRestoredProse=region.id;
   for(const record of orphaned){if(paragraph.childNodes.length)paragraph.append(' ');paragraph.append(recoverySpan(record));}
   doc.querySelector(`[data-spatial-crop="${region.id}"]`)!.after(paragraph);
  }
  for(const ids of crops.mergeNativeParagraphs){
   const found=ids.map(id=>doc.getElementById(id));if(!found[0])continue;
   if(found.some(el=>!el))throw new Error('Incomplete restored source paragraph');
   const paragraphs=[...new Set(found.map(el=>wrapNative(el!).closest('p')!))];
   const first=paragraphs[0];
   for(const paragraph of paragraphs.slice(1)){first.append(' ',...paragraph.childNodes);paragraph.remove();}
  }
  return doc.body.innerHTML;
 }finally{dom.window.close();}
}
