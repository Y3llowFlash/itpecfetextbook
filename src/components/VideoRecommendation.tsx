import { useState } from 'react';
import type { VideoLesson } from '../lib/models';

export function safeYoutubeId(video: VideoLesson): string | null {
  if (video.platform !== 'youtube' || !/^[a-zA-Z0-9_-]{11}$/.test(video.youtubeId || '')) return null;
  try { const url = new URL(video.url); return ['youtube.com', 'www.youtube.com', 'youtu.be'].includes(url.hostname) && url.protocol === 'https:' ? video.youtubeId! : null; } catch { return null; }
}

export default function VideoRecommendation({ videos, conceptId, questionId, fallback }: { videos: VideoLesson[]; conceptId: string; questionId: string; fallback: string }) {
  const [play, setPlay] = useState<string | null>(null);
  const relevant = videos.filter((video) => video.questionIds.includes(questionId) || video.conceptIds.includes(conceptId));
  return <aside className="video-help" aria-label="Free learning help">
    <strong>Finding this question difficult?</strong>
    {relevant.length > 0 ? <><p>Why not watch a free explanation?</p>{relevant.map((video) => {
      const youtubeId = safeYoutubeId(video);
      return <div key={video.id}>{youtubeId ? <>
        {play === video.id ? <iframe className="video-embed" src={`https://www.youtube-nocookie.com/embed/${youtubeId}`} title={video.title} allow="encrypted-media; picture-in-picture" allowFullScreen loading="lazy" referrerPolicy="strict-origin-when-cross-origin" /> : <button className="button button-secondary" type="button" onClick={() => setPlay(video.id)}>Play free lesson</button>}
        <a href={video.url} target="_blank" rel="noopener noreferrer">{video.title} · YouTube ↗</a>
      </> : <a className="external-lesson" href={video.url} target="_blank" rel="noopener noreferrer">{video.title}<span>{video.platform === 'telegram' ? 'Free topic lesson · Telegram' : 'Free external lesson'} ↗</span></a>}
        <p className="quiet-note">{video.questionIds.includes(questionId) ? 'Linked to this question.' : 'A concept lesson to help you review the idea.'}</p>
      </div>;
    })}</> : <><p>{fallback}</p><a href="/chapters/hardware/memory-and-cache/#weighted-average">Read the worked example →</a></>}
    <details className="course-note"><summary>Looking for a guided course?</summary><p>The 1% paid ITPEC course is an optional next step. Free textbook learning and practice remain available to everyone.</p></details>
  </aside>;
}
