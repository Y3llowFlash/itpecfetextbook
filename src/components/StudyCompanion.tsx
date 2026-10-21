import {useEffect,useState} from 'react';
import {useProgress} from '../lib/use-progress';
import {guestStore} from '../lib/progress';
import {returnUrl} from '../lib/reading';
import type {StudyContext} from '../lib/toc';
import {StorageNotice} from './GuestNotice';

export default function StudyCompanion({contexts,initialId}:{contexts:StudyContext[];initialId:string}){
 const [contextId,setContextId]=useState(initialId);
 const {progress}=useProgress();
 useEffect(()=>{
  const update=()=>{const id=document.documentElement.dataset.readingContext;if(contexts.some(node=>node.id===id))setContextId(id!);};
  update();window.addEventListener('itpec:reading-context',update);return()=>window.removeEventListener('itpec:reading-context',update);
 },[contexts]);
 const current=contexts.find(context=>context.id===contextId)||contexts[0];
 if(!current)return null;
 const completed=progress.completedSections.includes(current.completionId);
 const bookmarked=current.questionIds.filter(id=>progress.bookmarks.includes(id));
 return <div className="companion-content" data-study-context={current.id}>
   <p className="companion-label">Current section</p>
   <h2><span className="context-number">{current.number}</span> {current.title}</h2>
   <p className="source-badge">p. {current.page}</p>
   <section className="context-progress" aria-label="Section progress"><h3>Progress</h3>
     <p className="completion-status">{completed?'Completed':'In progress'}</p>
     <button type="button" className="text-button" aria-label={`Mark ${current.number} ${completed?'incomplete':'complete'}`} aria-pressed={completed} onClick={()=>guestStore.setCompleted(current.completionId,!completed)}>{completed?'Mark incomplete':'Mark complete'}</button>
     {progress.reading&&<a className="text-link" href={returnUrl(progress.reading)}>Continue reading</a>}
   </section>
   {current.links.length>0&&<section className="context-questions" aria-label="Related questions"><h3>Related questions <span className="context-count">{current.questionIds.length}</span></h3>
     {current.links.map(link=><a className="companion-practice" key={link.id} href={`/practice/${link.id}/`}><span>{link.title}</span><span>{link.count}</span></a>)}
   </section>}
   {bookmarked.length>0&&<section aria-label="Bookmarked related questions"><h3>Bookmarks <span className="context-count">{bookmarked.length}</span></h3>
    {bookmarked.map(id=><a className="text-link" key={id} href={`/practice/${current.links.find(link=>link.questionIds.includes(id))!.id}/?question=${id}`}>{id}</a>)}
   </section>}
   {current.videos.length>0&&<section aria-label="Related free lessons"><h3>Free lessons</h3>{current.videos.map(video=><a className="text-link" key={video.id} href={video.url} target="_blank" rel="noopener noreferrer">{video.title} ↗</a>)}</section>}
   <a className="text-link" href="/progress/">Progress and bookmarks</a>
   <StorageNotice/>
 </div>;
}
