import type {ReadingPosition} from './models';
export const CPU_PATH='/chapters/hardware/cpu-and-main-memory/';
export const CACHE_HEADING='fev1-201504-ch1-r1-pdf-075-b005-l00-text-0';
export const CACHE_LEGACY_ID='fe-v1-ch01-memory-cache';
export function canonicalReadingPosition(position:ReadingPosition):ReadingPosition{
  if(position.path!=='/chapters/hardware/memory-and-cache/'||position.sectionId!==CACHE_LEGACY_ID)return position;
  const source=/^fev1-201504-ch1-r1-pdf-0(?:75|76|77|78|79)-/.test(position.blockId);
  return {...position,sectionId:'fe-v1-ch01-s03',path:CPU_PATH,blockId:source?position.blockId:CACHE_HEADING,
    focusId:position.focusId==='concept-cache-memory'?position.focusId:undefined};
}
