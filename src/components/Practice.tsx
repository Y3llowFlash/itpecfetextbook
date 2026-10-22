import { useEffect, useRef, useState } from 'react';
import type { Concept, Explanation, Question } from '../lib/models';
import { guestStore, newId } from '../lib/progress';
import { useProgress } from '../lib/use-progress';
import { returnUrl, conceptReturnPosition } from '../lib/reading';
import { StorageNotice } from './GuestNotice';
import GuestNotice from './GuestNotice';
import VideoRecommendation from './VideoRecommendation';
import { useAccount } from './AccountControls';
import { DEFAULT_FILTERS, FILTER_KEY, filterQuestions, parseFilters, publishedYears, questionLabel } from '../lib/question-policy';
import type { QuestionFilters } from '../lib/question-policy';

export interface PracticeProps { concept: Concept; questions: Question[]; explanations: Explanation[]; availableYears?: number[] }
const paperLabel = questionLabel;

export default function Practice({ concept, questions: bank, explanations, availableYears }: PracticeProps) {
  const { progress } = useProgress();
  const account = useAccount();
  const restoringAccount = account.busy && !account.user;
  const [activeId, setActiveId] = useState(bank[0]?.id);
  const [filters, setFilters] = useState<QuestionFilters>(DEFAULT_FILTERS);
  const [feedbackId, setFeedbackId] = useState<string>();
  const questions = filterQuestions(bank, filters, new Set(progress.attempts.map(a => a.questionId)));
  // Keep submitted feedback visible even when Unanswered only removes this question.
  const question = bank.find(q => q.id === feedbackId) || questions.find(q => q.id === activeId) || questions[0];
  const index = questions.findIndex(q => q.id === question?.id);
  const years = availableYears || publishedYears(bank);
  const [selected, setSelected] = useState('');
  const [ready, setReady] = useState(false);
  const [imageFailed, setImageFailed] = useState(false);
  const [zoom, setZoom] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const hydrated = useRef(false);
  const explanationMap = new Map(explanations.map((entry) => [entry.questionId, entry]));
  const saved = question ? progress.practice[concept.id]?.answers[question.id] : undefined;
  const explanation = question ? explanationMap.get(question.id) : undefined;
  const correct = Boolean(saved && saved.selected === question?.correctAnswer);
  const answeredCount = questions.filter((q) => progress.practice[concept.id]?.answers[q.id]).length;
  // Hydration must initially match the static HTML; read sessionStorage only after mount.
  const readingReturn = returnUrl(ready ? conceptReturnPosition(progress.reading, concept.id, concept.sectionId) : progress.reading?.sectionId === concept.sectionId ? progress.reading : null, concept.sectionUrl);

  useEffect(() => {
    if (hydrated.current) return;
    hydrated.current = true;
    const current = guestStore.getSnapshot().progress.practice[concept.id]?.questionId;
    const requested = new URLSearchParams(location.search).get('question');
    if (bank.some(q => q.id === (requested || current))) setActiveId(requested || current);
    try { setFilters(parseFilters(JSON.parse(localStorage.getItem(FILTER_KEY) || 'null'))); } catch { /* Storage can be unavailable. Defaults remain usable. */ }
    setReady(true);
  }, [concept.id, bank]);

  useEffect(() => {
    if (!ready || feedbackId) return;
    const url = new URL(location.href);
    if (question) { setActiveId(question.id); url.searchParams.set('question', question.id); }
    else url.searchParams.delete('question');
    history.replaceState(null, '', url);
  }, [ready, question?.id, feedbackId]);

  useEffect(() => {
    setSelected(saved?.selected || '');
    setImageFailed(false);
  }, [question?.id, saved?.selected, progress.guestId]);

  useEffect(() => {
    if (zoom) dialog.current?.showModal();
    else if (dialog.current?.open) dialog.current.close();
  }, [zoom]);

  const changeFilters = (next: QuestionFilters) => {
    setFeedbackId(undefined); setFilters(next);
    try { localStorage.setItem(FILTER_KEY, JSON.stringify(next)); } catch { /* Filtering works without persistent storage. */ }
  };
  const controls = <fieldset className="practice-filters"><legend>Filter questions</legend>
    <label>From year<select value={filters.from ?? ''} onChange={e => changeFilters({ ...filters, from: e.target.value ? Number(e.target.value) : null })}><option value="">Any year</option>{years.map(year => <option key={year}>{year}</option>)}</select></label>
    <label>To year<select value={filters.to ?? ''} onChange={e => changeFilters({ ...filters, to: e.target.value ? Number(e.target.value) : null })}><option value="">Any year</option>{years.map(year => <option key={year}>{year}</option>)}</select></label>
    <button type="button" className="text-button" onClick={() => changeFilters({ ...filters, from: null, to: null })}>All years</button>
    <label>Question source<select value={filters.source} onChange={e => changeFilters({ ...filters, source: e.target.value as QuestionFilters['source'] })}><option value="all">All sources</option><option value="itpec-practice">ITPEC Practice only</option><option value="historical-pdf">Historical PDFs only</option></select></label>
    <label className="filter-checkbox"><input type="checkbox" checked={filters.unanswered} onChange={e => changeFilters({ ...filters, unanswered: e.target.checked })} />Unanswered only</label>
    {filters.from !== null && filters.to !== null && filters.from > filters.to && <p role="alert">From year must be no later than To year.</p>}
    <p aria-live="polite">{questions.length} of {bank.length} questions match.</p>
  </fieldset>;
  if (!question || !explanation) return <div className="practice-flow"><a href={readingReturn}>← Return to textbook</a>{bank.length > 0 && controls}<section className="empty-state"><h1>{bank.length ? 'No questions match these filters' : 'Practice is not available yet'}</h1><p>{bank.length ? 'Change the filters to see more questions. Your answers and bookmarks are saved.' : 'This concept doesn’t have a complete published question set.'}</p>{bank.length > 0 && <button type="button" className="button button-secondary" onClick={() => changeFilters(DEFAULT_FILTERS)}>Reset filters</button>}<a href={readingReturn}>Return to the lesson →</a></section></div>;

  const goTo = (next: number) => {
    if (next < 0 || next >= questions.length) return;
    setFeedbackId(undefined); setActiveId(questions[next].id);
    guestStore.setCurrentQuestion(concept.id, questions[next].id);
    const url = new URL(location.href); url.searchParams.set('question', questions[next].id); history.replaceState(null, '', url);
    heading.current?.focus({ preventScroll: true });
  };
  const submit = () => {
    if (!selected || saved || restoringAccount) return;
    setFeedbackId(question.id);
    guestStore.recordAttempt({ id: newId(), questionId: question.id, conceptId: concept.id, selected,
      correct: selected === question.correctAnswer, at: new Date().toISOString(), revision: explanation.revision });
  };

  return <div className="practice-flow">
    <a className="back-to-reading" href={readingReturn}>← Return to textbook</a>
    <header className="practice-heading"><p className="small-label">HARDWARE · CONCEPT PRACTICE</p><h1>{concept.title}</h1><p>{questions.length} related published questions. Take them one at a time.</p></header>
    {controls}
    <div className="practice-topline"><p>{index >= 0 ? <>Question <strong>{index + 1}</strong> of {questions.length}</> : <>Answer saved · {questions.length} unanswered remain</>}</p><span>{answeredCount}/{questions.length} answered</span></div>
    <nav className="question-navigation" aria-label="Question navigation">{questions.map((q, i) => {
      const answer = progress.practice[concept.id]?.answers[q.id];
      const state = answer ? (answer.selected === q.correctAnswer ? 'correct' : 'incorrect') : 'unanswered';
      return <button type="button" key={q.id} className={`question-number ${i === index ? 'current' : ''} ${state}`} aria-current={i === index ? 'step' : undefined}
        aria-label={`Question ${i + 1}, ${state}`} onClick={() => goTo(i)}>{i + 1}{answer && <span aria-hidden="true">{state === 'correct' ? '✓' : '×'}</span>}</button>;
    })}</nav>
    <div className="question-meta"><h2 ref={heading} tabIndex={-1}>{paperLabel(question)} · Q{question.number}</h2>
      <button className="bookmark-button" type="button" aria-pressed={progress.bookmarks.includes(question.id)} onClick={() => guestStore.toggleBookmark(question.id)}>{progress.bookmarks.includes(question.id) ? '◆ Bookmarked' : '◇ Bookmark'}</button></div>
    <figure className="exam-image-figure">
      {imageFailed ? <p role="status">The image could not load. Use the accessible question description below.</p> : <button className="exam-image-button" type="button" onClick={() => setZoom(true)} aria-label={`Enlarge original question ${question.id}`}>
        <img key={question.id} src={question.image.src} width={question.image.width} height={question.image.height} alt={`Original ${paperLabel(question)}, question ${question.number}. Accessible description follows.`} loading="eager" decoding="async" onError={() => setImageFailed(true)} />
      </button>}
      <figcaption>Original exam question · Select the image to enlarge</figcaption>
    </figure>
    <details className="question-transcript"><summary>Read the question as text</summary><p>{explanation.imageDescription}</p><p>The original image above preserves the complete exam wording and layout.</p></details>
    <form onSubmit={(event) => { event.preventDefault(); submit(); }}>
      <fieldset className="answer-options" disabled={!ready || restoringAccount || Boolean(saved)}><legend>Choose your answer</legend>
        {question.options.map((option) => <label key={option} className={`answer-option ${selected === option ? 'selected' : ''} ${saved && option === question.correctAnswer ? 'answer-correct' : ''} ${saved && option === saved.selected && !correct ? 'answer-incorrect' : ''}`}>
          <input type="radio" name={`answer-${question.id}`} aria-label={`Option ${option.toUpperCase()}: ${explanation.optionText[option] || option.toUpperCase()}`} value={option} checked={selected === option} onChange={() => setSelected(option)} />
          <span className="option-letter">{option.toUpperCase()}</span><span>{explanation.optionText[option] || `Option ${option.toUpperCase()}`}</span>
          {saved && option === question.correctAnswer && <span className="answer-state">✓ Correct answer</span>}
        </label>)}
      </fieldset>
      {!saved && <div className="submit-row"><button className="button button-primary" type="submit" disabled={!selected || !ready || restoringAccount}>Check answer</button><span className="quiet-note">{restoringAccount ? 'Restoring your account progress…' : selected ? 'Ready when you are.' : 'Choose an option to check your answer.'}</span></div>}
    </form>
    {saved && <section className={`answer-feedback ${correct ? 'is-correct' : 'is-incorrect'}`} aria-label="Answer feedback" aria-live="polite">
      <h3>{correct ? '✓ That’s correct.' : 'Let’s work through it.'}</h3>
      {!correct && <p>You chose {saved.selected.toUpperCase()}. The correct answer is <strong>{question.correctAnswer.toUpperCase()}</strong>.</p>}
      <p className="answer-summary">{explanation.summary}</p>
      <h4>Why this answer works</h4><ol>{explanation.steps.map((step) => <li key={step}>{step}</li>)}</ol>
      <p className="takeaway"><strong>Remember:</strong> {explanation.takeaway}</p>
      <button className="text-button" type="button" onClick={() => { guestStore.retryQuestion(concept.id, question.id); setSelected(''); }}>Try this question again</button>
    </section>}
    {saved && !correct && <VideoRecommendation videos={concept.videos} conceptId={concept.id} questionId={question.id} fallback={explanation.takeaway} readingUrl={`${concept.sectionUrl}${concept.anchor ? `#${concept.anchor}` : ''}`} />}
    <div className="practice-bottom"><button className="button button-secondary" type="button" disabled={index <= 0} onClick={() => goTo(index - 1)}>← Previous</button>
      <span>{index >= 0 ? `${index + 1} / ${questions.length}` : `${questions.length} remaining`}</span>
      {index < questions.length - 1 ? <button className="button button-primary" type="button" onClick={() => goTo(index + 1)}>Next →</button> : <a className="button button-primary" href={readingReturn}>Back to lesson →</a>}
    </div>
    <p className="source-note">Source: {question.source.questionPdf.split('/').pop()}, PDF page {question.source.pageStart}{question.source.pageEnd !== question.source.pageStart ? `–${question.source.pageEnd}` : ''}. ID: <code>{question.id}</code>. Explanation written for this textbook.</p>
    <StorageNotice /><GuestNotice />
    <dialog className="image-dialog" ref={dialog} onClose={() => setZoom(false)} onClick={(event) => { if (event.target === dialog.current) setZoom(false); }}>
      <div className="dialog-heading"><strong>Original question · Q{question.number}</strong><button type="button" className="button button-secondary" onClick={() => setZoom(false)} autoFocus>Close ×</button></div>
      <div className="zoom-scroll"><img src={question.image.src} width={question.image.width} height={question.image.height} alt={explanation.imageDescription} /></div>
      <p>Scroll horizontally to read the image at full size.</p>
    </dialog>
  </div>;
}
