import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fs from 'node:fs';
import Practice from '../src/components/Practice';
import definitions from '../src/content/concepts.json';
import explanations from '../src/content/explanations.json';
import { guestStore } from '../src/lib/progress';
import type { Concept, Question } from '../src/lib/models';

const concept = definitions[0] as Concept;
const bank = JSON.parse(fs.readFileSync('public/data/questions.json', 'utf8')) as Question[];
const questions = bank.filter((q) => concept.questionIds.includes(q.id));
const props = { concept, questions, explanations };
beforeEach(() => { cleanup(); localStorage.clear(); guestStore.refresh(); history.replaceState(null, '', '/practice/cache-memory/'); });
afterEach(cleanup);

describe('complete cache practice interaction', () => {
  it('remembers filters, safely handles empty results, and preserves progress', async () => {
    const user = userEvent.setup(); const view=render(<Practice {...props} />);
    await user.click(screen.getByRole('button',{name:'◇ Bookmark'}));
    await user.selectOptions(screen.getByRole('combobox',{name:'From year'}),'2025');
    expect(screen.getByRole('heading',{name:'2025 Spring · Subject A · Q10'})).toBeTruthy();
    await user.selectOptions(screen.getByRole('combobox',{name:'Question source'}),'historical-pdf');
    expect(screen.getByRole('heading',{name:'No questions match these filters'})).toBeTruthy();
    expect(guestStore.getSnapshot().progress.bookmarks).toHaveLength(1);
    view.unmount(); render(<Practice {...props}/>);
    expect(screen.getByRole('heading',{name:'No questions match these filters'})).toBeTruthy();
    await user.click(screen.getByRole('button',{name:'Reset filters'}));
    expect(screen.getAllByRole('button',{name:/Question \d+, unanswered/})).toHaveLength(11);
  });
  it('keeps feedback visible in unanswered mode, then navigates to the remaining questions',async()=>{
    const user=userEvent.setup(); render(<Practice {...props}/>);
    await user.click(screen.getByRole('checkbox',{name:'Unanswered only'}));
    await user.click(screen.getByRole('radio',{name:/Option B: 360 ns/}));
    await user.click(screen.getByRole('button',{name:'Check answer'}));
    expect(screen.getByText('✓ That’s correct.')).toBeTruthy();
    expect(screen.getByText('Answer saved · 10 unanswered remain')).toBeTruthy();
    await user.click(screen.getByRole('button',{name:'Next →'}));
    expect(screen.getByRole('heading',{name:'2025 Spring · Subject A · Q10'})).toBeTruthy();
    expect(guestStore.getSnapshot().progress.attempts).toHaveLength(1);
  });
  it('records only submitted answers and shows the checked explanation', async () => {
    const user = userEvent.setup(); render(<Practice {...props} />);
    expect(screen.getByText('11 related published questions. Take them one at a time.')).toBeTruthy();
    await user.click(screen.getByRole('radio', { name: /Option B: 360 ns/ }));
    expect(guestStore.getSnapshot().progress.attempts).toHaveLength(0);
    await user.click(screen.getByRole('button', { name: 'Check answer' }));
    expect(screen.getByText('✓ That’s correct.')).toBeTruthy();
    expect(screen.getByText(/1500 ns already includes checking the cache/)).toBeTruthy();
    expect(guestStore.getSnapshot().progress.attempts).toHaveLength(1);
    expect(screen.getByRole('radio', { name: /Option B: 360 ns/ }).matches(':disabled')).toBe(true);
  });
  it('supports incorrect feedback, free help, next/previous and numbered navigation', async () => {
    const user = userEvent.setup(); render(<Practice {...props} />);
    await user.click(screen.getByRole('radio', { name: /Option A: 315 ns/ }));
    await user.click(screen.getByRole('button', { name: 'Check answer' }));
    expect(screen.getByText('Let’s work through it.')).toBeTruthy();
    expect(screen.getByRole('link', { name: /HDD, RAM, register & cache/ }).getAttribute('href')).toBe('https://t.me/itpecmm/101');
    await user.click(screen.getByRole('button', { name: 'Next →' }));
    expect(screen.getByRole('heading', { name: '2025 Spring · Subject A · Q10' })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: '← Previous' }));
    expect(screen.getByText('Let’s work through it.')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Question 3, unanswered' }));
    expect(screen.getByRole('heading', { name: '2026 Spring · Subject A · Q10' })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Next →' }));
    expect(screen.getByRole('heading', { name: '2009 Autumn · Morning · Q28' })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Next →' }));
    expect(screen.getByRole('heading', { name: '2011 Autumn · Morning · Q11' })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Next →' }));
    expect(screen.getByRole('heading', { name: '2015 Autumn · Morning · Q11' })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Question 10, unanswered' }));
    expect(screen.getByRole('heading', { name: '2019 Spring · Morning · Q11' })).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Next →' }));
    expect(screen.getByRole('heading', { name: '2022 Spring · Morning · Q13' })).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Back to lesson →' })).toBeTruthy();
  });
  it('restores answer and bookmark state after remounting the practice screen', async () => {
    const user = userEvent.setup(); const view = render(<Practice {...props} />);
    await user.click(screen.getByRole('button', { name: '◇ Bookmark' }));
    await user.click(screen.getByRole('radio', { name: /Option B: 360 ns/ }));
    await user.click(screen.getByRole('button', { name: 'Check answer' }));
    view.unmount(); guestStore.refresh(); render(<Practice {...props} />);
    expect(screen.getByRole('button', { name: '◆ Bookmarked' }).getAttribute('aria-pressed')).toBe('true');
    await waitFor(() => expect(screen.getByText('✓ That’s correct.')).toBeTruthy());
    expect(guestStore.getSnapshot().progress.attempts).toHaveLength(1);
  });
  it('offers the text description when an image fails and safely handles an empty set', () => {
    const view = render(<Practice {...props} />);
    fireEvent.error(screen.getByRole('img', { name: /Original 2024 Autumn/ }));
    expect(screen.getByText(/image could not load/)).toBeTruthy();
    view.unmount(); render(<Practice {...props} questions={[]} />);
    expect(screen.getByRole('heading', { name: 'Practice is not available yet' })).toBeTruthy();
  });
});
