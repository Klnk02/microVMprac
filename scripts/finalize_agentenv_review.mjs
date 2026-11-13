import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const workspace=path.resolve(repo,'..');
const work=path.join(workspace,'.review-build');
const runtime=process.env.CODEX_REVIEW_RUNTIME || 'C:/Users/a/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill=process.env.CODEX_REVIEW_PRESENTATION_SKILL || 'C:/Users/a/.codex/plugins/cache/openai-primary-runtime/presentations/26.1111.10930/skills/presentations';
process.env.RUNTIME_NODE_MODULES=runtime+'/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
await fs.mkdir(work+'/output',{recursive:true});
const candidatePath=work+'/candidate.pptx';
const digest=createHash('sha256').update(await fs.readFile(candidatePath)).digest('hex').slice(0,12);
const stamp=Date.now();
const owners=[2,6,8,12,22,23,30,31,34,38,44,51,52,56,57,62,65,66,68];
const result=await finalizePresentation({workspaceDir:workspace,candidatePath,
 finalPath:work+'/output/agentenv-review-'+digest+'-'+stamp+'.pptx',
 pythonExecutable:runtime+'/python/python.exe',
 integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...owners.flatMap(n=>['--require-native-table-slide',String(n)])],
 explicitTotalSlideCount:68,requiredNativeTableOwnerSlides:owners,
 fontPolicy:{basis:'design',families:['Microsoft YaHei']},verifyArtifactToolImport:true,
 receiptPath:work+'/validation-'+digest+'-'+stamp+'.json'
});
console.log(JSON.stringify({finalPath:result.finalPath,receiptPath:result.receiptPath,sha256:result.finalSha256}));
