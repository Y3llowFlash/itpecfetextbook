import { syncQuestions } from './question-sync';
const args = process.argv.slice(2);
if (args.some((arg,i) => !['--dry-run','--source'].includes(arg) && args[i-1] !== '--source')) throw new Error('Usage: questions:sync [--dry-run] [--source <Practice repository>]');
const index = args.indexOf('--source');
if (index >= 0 && (!args[index+1] || args[index+1].startsWith('--'))) throw new Error('--source requires a path');
const result = await syncQuestions(index >= 0 ? args[index+1] : 'D:/ITPEC Old Questions', process.cwd(), args.includes('--dry-run'));
console.log(JSON.stringify(result, null, 2));
if (result.conflicts.length) process.exitCode = 2;
