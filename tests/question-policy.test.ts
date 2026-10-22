// @vitest-environment node
import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import { DEFAULT_FILTERS, filterQuestions, matchOccurrence, parseFilters, publishedYears } from '../src/lib/question-policy';
import type { Question } from '../src/lib/models';
const bank = JSON.parse(fs.readFileSync('public/data/questions.json','utf8')) as Question[];
const a = { ...bank[0], id:'one', year:2020 }, b = { ...bank[1], id:'two', year:2026 }, sample = { ...bank[0], id:'sample', year:null };
const historical = { ...a, review:{ sources:[{kind:'itpec-practice'},{kind:'historical-pdf'}] } } as Question;
describe('reusable question filtering',()=>{
  it('includes both boundaries, excludes undated samples in a range and resets all years',()=>{
    expect(filterQuestions([a,b,sample],{...DEFAULT_FILTERS,from:2020,to:2026},new Set()).map(q=>q.id)).toEqual(['one','two']);
    expect(filterQuestions([a,b,sample],DEFAULT_FILTERS,new Set())).toHaveLength(3);
    expect(filterQuestions([a,b],{...DEFAULT_FILTERS,from:2026,to:2020},new Set())).toEqual([]);
  });
  it('tests source membership without duplicating canonical questions',()=>{
    expect(filterQuestions([historical,historical,b],{...DEFAULT_FILTERS,source:'historical-pdf'},new Set())).toEqual([historical]);
    expect(filterQuestions([historical,b],{...DEFAULT_FILTERS,source:'itpec-practice'},new Set())).toHaveLength(2);
  });
  it('combines year, source and unanswered without mutating any inputs',()=>{
    const answered=new Set(['one']); const before=JSON.stringify([historical,b]);
    expect(filterQuestions([historical,b],{from:2020,to:2026,source:'historical-pdf',unanswered:true},answered)).toEqual([]);
    expect(JSON.stringify([historical,b])).toBe(before); expect([...answered]).toEqual(['one']);
  });
  it('derives years only from real published records and validates stored settings',()=>{
    expect(publishedYears([a,b,sample,a])).toEqual([2020,2026]);
    expect(parseFilters({from:'2020',to:2500,source:'bad',unanswered:'true'})).toEqual(DEFAULT_FILTERS);
  });
});
const candidate={id:'canonical',examType:'FE-AM',year:2020,season:'S',number:1,contentSha256:'same',answer:'a'};
describe('reliable examination occurrence matches',()=>{
  it('keeps Practice ID and authoritative answer while recording a printed-key conflict',()=>{
    expect(matchOccurrence({...candidate,id:'pdf',answer:'b'},[candidate])).toEqual({status:'matched',canonicalId:'canonical',answer:'a',conflict:true});
  });
  it('does not merge repeated wording across years, incomplete metadata or ambiguous occurrences',()=>{
    expect(matchOccurrence({...candidate,year:2019},[candidate]).status).toBe('needs-review');
    expect(matchOccurrence({...candidate,examType:null},[candidate]).status).toBe('needs-review');
    expect(matchOccurrence(candidate,[candidate,{...candidate,id:'other'}]).status).toBe('needs-review');
    expect(matchOccurrence({...candidate,contentSha256:'different'},[candidate]).status).toBe('needs-review');
    expect(matchOccurrence({...candidate,year:2019,contentSha256:'different'},[candidate]).status).toBe('distinct');
  });
});
