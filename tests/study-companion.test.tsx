import {afterEach,beforeEach,it,expect} from 'vitest';
import {render,screen,cleanup,act} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {readFileSync} from 'node:fs';
import StudyCompanion from '../src/components/StudyCompanion';
import {studyContext} from '../src/lib/study-context';
import {contents} from '../src/lib/toc';
import type {Question} from '../src/lib/models';
import {guestStore} from '../src/lib/progress';
const bank=JSON.parse(readFileSync('public/data/questions.json','utf8')) as Question[];
const contexts=['3-5-1','3-3-4','4-1-3','1'].map(number=>studyContext(contents.find(n=>n.number===number)!,bank));
beforeEach(()=>{localStorage.clear();sessionStorage.clear();guestStore.refresh();delete document.documentElement.dataset.readingContext;});
afterEach(cleanup);
it('updates section, counts and mapped video as source context changes and omits unavailable controls',()=>{
 render(<StudyCompanion contexts={contexts} initialId={contexts[0].id}/>);
 expect(screen.getByRole('heading',{name:'3-5-1 High Speed Memory Access'})).toBeTruthy();expect(screen.getByRole('link',{name:/Cache memory/}).getAttribute('href')).toBe('/practice/cache-memory/');
 act(()=>{document.documentElement.dataset.readingContext=contexts[1].id;window.dispatchEvent(new CustomEvent('itpec:reading-context'));});
 expect(screen.getByRole('heading',{name:'3-3-4 Interrupt'})).toBeTruthy();expect(screen.queryByRole('link',{name:/Cache memory/})).toBeNull();expect(screen.queryByRole('heading',{name:'Free lessons'})).toBeNull();
 act(()=>{document.documentElement.dataset.readingContext=contexts[3].id;window.dispatchEvent(new CustomEvent('itpec:reading-context'));});
 expect(screen.queryByRole('region',{name:'Related questions'})).toBeNull();
});
it('persists legacy cache completion and routes bookmarked related questions to the correct concept',async()=>{
 const user=userEvent.setup();render(<StudyCompanion contexts={contexts} initialId={contexts[0].id}/>);
 await user.click(screen.getByRole('button',{name:'Mark 3-5-1 complete'}));expect(guestStore.getSnapshot().progress.completedSections).toContain('fe-v1-ch01-memory-cache');expect(guestStore.getSnapshot().progress.completedSections).not.toContain('fe-v1-ch01-s03');
 const id=contexts[2].links.find(l=>l.id==='defragmentation')!.questionIds[0];
 act(()=>{guestStore.toggleBookmark(id);document.documentElement.dataset.readingContext=contexts[2].id;window.dispatchEvent(new CustomEvent('itpec:reading-context'));});
 expect(screen.getByRole('link',{name:id}).getAttribute('href')).toBe(`/practice/defragmentation/?question=${id}`);
});
