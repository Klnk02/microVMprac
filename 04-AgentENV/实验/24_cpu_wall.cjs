// Local wall/CPU accounting demonstration. This is not a storage benchmark.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { performance } = require('node:perf_hooks');

const waitMs = 500;
const repetitions = 3;
let checksum = 0;

function compute() {
  let value = 0;
  for (let i = 0; i < 20000000; i++) {
    value = (value + (i ^ (i >>> 3))) | 0;
  }
  checksum ^= value;
}

function busyWait() {
  const deadline = performance.now() + waitMs;
  while (performance.now() < deadline) {
    // Deliberately consume CPU while waiting for a deadline.
  }
}

function sleepWait() {
  return new Promise(resolve => setTimeout(resolve, waitMs));
}

async function measure(name, operation, round) {
  const cpuStart = process.cpuUsage();
  const wallStart = performance.now();
  await operation();
  const wallMs = performance.now() - wallStart;
  const cpu = process.cpuUsage(cpuStart);
  return {
    name,
    round,
    wall_ms: wallMs,
    user_cpu_ms: cpu.user / 1000,
    system_cpu_ms: cpu.system / 1000,
    process_cpu_ms: (cpu.user + cpu.system) / 1000
  };
}

async function main() {
  compute(); // Warm up this function before retaining samples.
  const samples = [];
  const cases = [
    ['compute', compute],
    ['sleep', sleepWait],
    ['busy_poll', busyWait]
  ];
  for (let round = 1; round <= repetitions; round++) {
    for (const [name, operation] of cases) {
      samples.push(await measure(name, operation, round));
    }
  }
  const summary = cases.map(([name]) => {
    const selected = samples.filter(sample => sample.name === name);
    const average = key => selected.reduce((sum, sample) => sum + sample[key], 0) / selected.length;
    const wall = average('wall_ms');
    const cpu = average('process_cpu_ms');
    return {
      name,
      n: selected.length,
      mean_wall_ms: wall,
      mean_process_cpu_ms: cpu,
      cpu_per_wall_percent: 100 * cpu / wall
    };
  });
  const result = {
    measured_at: new Date().toISOString(),
    platform: process.platform,
    release: os.release(),
    runtime: process.version,
    logical_cpus: os.cpus().length,
    scope: 'One Node process, including its runtime threads; agent-run Windows demonstration, not Linux perf or microVM IO.',
    wait_ms: waitMs,
    checksum,
    samples,
    summary
  };
  const output = path.join(__dirname, '24_cpu_wall_result.json');
  if (process.argv.includes('--stdout')) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
  console.table(summary);
  console.log('Raw results: ' + output);
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
