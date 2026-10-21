// Server-only: compute verified counts once at build time, never on scroll.
import {concepts,questionsForConcept} from './catalog';
import type {Question} from './models';
import {contents,descendants,completionId,type ContentsEntry,type StudyContext} from './toc';
export function studyContext(node:ContentsEntry,bank:Question[]):StudyContext{
  const ids=new Set(descendants(node).flatMap(child=>child.conceptIds));
  const related=concepts.filter(concept=>ids.has(concept.id));
  const questionIds=[...new Set(related.flatMap(concept=>questionsForConcept(concept,bank).map(q=>q.id)))];
  return {...node,completionId:completionId(node),questionIds,
    links:related.map(concept=>({id:concept.id,title:concept.title,count:questionsForConcept(concept,bank).length,questionIds:questionsForConcept(concept,bank).map(q=>q.id)})).filter(link=>link.count>0),
    videos:[...new Map(related.flatMap(concept=>concept.videos).map(video=>[video.url,{id:video.id,title:video.title,url:video.url}])).values()]};
}
export const studyContextsForSection=(sectionId:string,bank:Question[])=>contents.filter(node=>node.sectionId===sectionId).map(node=>studyContext(node,bank));
export const studyContextForConcept=(conceptId:string,bank:Question[])=>{
  const node=contents.find(node=>node.conceptIds.includes(conceptId));
  return node?studyContext(node,bank):undefined;
};
