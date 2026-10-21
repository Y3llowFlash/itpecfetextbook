import data from '../content/hardware-toc.json' with {type:'json'};
import {CACHE_LEGACY_ID} from './reading-routes';
export interface ContentsEntry{id:string;number:string;title:string;page:number;depth:number;sectionId:string;path:string;conceptIds:string[]}
export const contents=data.nodes as ContentsEntry[];
export const mainContents=contents.filter(node=>node.depth===1);
export const contentsUrl=(node:ContentsEntry)=>`${node.path}#${node.id}`;
export const descendants=(node:ContentsEntry)=>contents.filter(child=>child.number===node.number||child.number.startsWith(node.number+'-'));
export const completionId=(node:ContentsEntry)=>node.number==='3-5-1'?CACHE_LEGACY_ID:node.depth===1?node.sectionId:node.id;
export const contentsForPath=(path:string)=>contents.filter(node=>node.path===path);
export interface StudyContext extends ContentsEntry{
  completionId:string;
  questionIds:string[];
  links:Array<{id:string;title:string;count:number;questionIds:string[]}>;
  videos:Array<{id:string;title:string;url:string}>;
}
