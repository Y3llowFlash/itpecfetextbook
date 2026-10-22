import covers from '../content/book-covers.json' with {type:'json'};
export const FE_ENTRY='/chapters/hardware/';
export const landingBooks=covers.map(cover=>({
 ...cover,label:`${cover.level.toUpperCase()} Level`,
 subtitle:cover.level==='fe'?'IT Fundamentals':cover.level==='ip'?'IT Passport Examination':'Applied Information Technology Engineer',
 available:cover.level==='fe',status:cover.level==='fe'?'Available now':'Coming soon',image:cover.variants.at(-1)!,
 srcset:cover.variants.map(v=>`/${v.path} ${v.width}w`).join(', '),
}));
