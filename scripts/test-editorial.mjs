import { spawnSync } from 'node:child_process';
for(const [command,args] of [
  [process.execPath,['--test','tests/editorial-server.test.mjs']],
  ['python',['-m','unittest','discover','-s','tests','-p','test_editorial_converter.py']],
  [process.execPath,['node_modules/@playwright/test/cli.js','test','--config','playwright.editorial.config.ts']],
]){
  const result=spawnSync(command,args,{stdio:'inherit',env:{...process.env,DEBUG:''}});
  if(result.status!==0)process.exit(result.status||1);
}
