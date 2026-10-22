import path from 'node:path';
import { syncQuestions } from './question-sync';
const sourceIndex = process.argv.indexOf('--source');
const source = sourceIndex >= 0 ? process.argv[sourceIndex + 1] : process.env.ITPEC_SOURCE_DIR;
if (!source) throw new Error('Use npm run import:questions -- --source "D:\\ITPEC Old Questions"');
// Keep the legacy entry point, but never replace an approved historical catalog.
const report = await syncQuestions(source, path.resolve('.'), process.argv.includes('--dry-run'));
console.log(JSON.stringify(report,null,2));
if(report.conflicts.length)process.exitCode=2;
