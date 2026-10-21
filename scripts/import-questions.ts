import path from 'node:path';
import { importQuestions } from './question-importer';
const sourceIndex = process.argv.indexOf('--source');
const source = sourceIndex >= 0 ? process.argv[sourceIndex + 1] : process.env.ITPEC_SOURCE_DIR;
if (!source) throw new Error('Use npm run import:questions -- --source "D:\\ITPEC Old Questions"');
const manifest = await importQuestions(source, path.resolve('.'));
console.log(`Imported ${manifest.total} published questions. Excluded ${manifest.rejectedUnpublished} unpublished records and their images. Dataset ${manifest.datasetHash.slice(0, 12)}.`);
