// @vitest-environment node
import { it,expect } from 'vitest';
import { createHash } from 'node:crypto';
import { applyQuestionHighlights } from '../src/lib/question-highlights';
import type { Concept,Question } from '../src/lib/models';
const question={id:'same',is_published:true}as Question;
const concept={id:'reviewed',questionIds:['same']}as Concept;
it('counts unique approved questions and replaces both the visible and accessible legacy badge',()=>{
  const html='<p><a data-concept="reviewed">Source words<span class="concept-count" aria-label="9 published questions"> · 9 questions</span></a></p>';
  const rendered=applyQuestionHighlights(html,[concept],[question,question]);
  expect(rendered).toContain('1 published questions');expect(rendered).toContain(' · 1 question</span>');expect(rendered).not.toContain('9 questions');
});
it('adds only a hash-bound approved source passage and preserves its original inner markup',()=>{
  const inner='<span>Original source words</span>';
  const reviewed={...concept,sourceHighlight:{headingNumber:'3-1',passageId:'source-passage',fragmentSha256:createHash('sha256').update(inner).digest('hex')}};
  const html=`<p id="source-passage">${inner}</p>`;
  const result=applyQuestionHighlights(html,[reviewed],[question]);
  expect(result).toContain(`href="/practice/reviewed/">${inner}`);
  expect(()=>applyQuestionHighlights(html.replace('words','changed'),[reviewed],[question])).toThrow('passage changed');
  expect(()=>applyQuestionHighlights(html,[reviewed],[])).toThrow('passage changed');
});
