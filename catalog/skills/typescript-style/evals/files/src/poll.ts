import { readFile } from 'node:fs/promises';
import { Client, JobStatus } from './client';
const terminal = ['SUCCEEDED', 'FAILED', 'CANCELLED'];
export type Poller = (jobId: string) => Promise<JobStatus>;
/**
 * Polls a job.
 * @param {Client} client the client
 * @param {number} deadline the deadline
 */
export function poller(client: Client, deadline: number): Poller {
  return async (jobId) => {
    let attempt = 0;
    while (Date.now() < deadline) {
      const status = (await client.describe(jobId, { region: JSON.parse(await readFile('config.json', 'utf8')).region })) as JobStatus;
      if (terminal.includes(status.state)) return status;
      else { attempt++; await new Promise((r) => setTimeout(r, Math.min(30000, 500 * 2 ** attempt))); }
    }
    throw new Error('timeout');
  };
}
export const stop = (client: Client, jobId: string) => { client.cancel(jobId); };
