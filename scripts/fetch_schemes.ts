import axios from 'axios';
import { createObjectCsvWriter } from 'csv-writer';
import fs from 'fs';
import path from 'path';
import 'dotenv/config';


// Replace with your actual endpoint
const ENDPOINT = `https://api.myscheme.gov.in/search/v4/schemes?lang=en`;
const DETAILS_ENDPOINT = `https://api.myscheme.gov.in/schemes/v5/public/schemes?lang=en&slug=`;

// Ensure the data directory exists at the project root
const rootDataDir = path.resolve(__dirname, '..', 'data');
const rootDetailsDir = path.resolve(rootDataDir, 'scheme-details');

function getHeaders() {
    return {
        'accept': 'application/json, text/plain, */*',
        'x-api-key': 'API_KEY',
        'origin': 'https://www.myscheme.gov.in'
    };
}

async function fetchScheme(from: number, size: number) {
    return await axios.get(`${ENDPOINT}&from=${from}&size=${size}`, {
        headers: getHeaders()
    });
}

async function fetchSchemeDetails(slug: string) {
    return await axios.get(`${DETAILS_ENDPOINT}${slug}`, {
        headers: getHeaders()
    });
}

async function scrapeData() {
    const allItems: any[] = [];
    let size = 100, from = 0;
    let total = 0;

    while (true) {
        console.log(`Fetching from ${from}`);

        try {
            const resp = await fetchScheme(from, size);
            const { data } = resp.data

            from += data?.hits?.page?.size;

            if (data?.hits?.items) {
                allItems.push(...data.hits.items);
            }

            if (data?.hits?.page?.pageNumber === data?.hits?.page.totalPages - 1) {
                break;
            }
        } catch (err) {
            console.error('Request failed:', err);
            break;
        }
    }

    if (!allItems.length) {
        return;
    }

    // Map to JSON-friendly structure (sanitized)
    const records = allItems.map(item => item);

    // Ensure the root data directory exists
    if (!fs.existsSync(rootDataDir)) {
        fs.mkdirSync(rootDataDir, { recursive: true });
    }
    const outPath = path.join(rootDataDir, 'schemes.json');
    fs.writeFileSync(outPath, JSON.stringify(records, null, 2), 'utf-8');
    console.log(`JSON file written: ${outPath}`);
}

function getSlugsFromSchemes(): string[] {
    const data = fs.readFileSync(path.join(rootDataDir, 'schemes.json'), 'utf-8');
    const schemes = JSON.parse(data);
    return schemes.map((item: any) => item.fields?.slug || '').filter((slug: string) => !!slug);
}

function chunkArray<T>(arr: T[], chunkSize: number): T[][] {
    const results: T[][] = [];
    for (let i = 0; i < arr.length; i += chunkSize) {
        results.push(arr.slice(i, i + chunkSize));
    }
    return results;
}

async function scrapeSchemeDetails() {
    const slugIds: string[] = getSlugsFromSchemes();
    const BATCH_SIZE = 100;
    const BATCH_DELAY_MS = 60 * 1000; // 1 minute

    // Ensure the root details directory exists
    if (!fs.existsSync(rootDetailsDir)) {
        fs.mkdirSync(rootDetailsDir, { recursive: true });
    }

    const batches = chunkArray(slugIds, BATCH_SIZE);

    for (let batchIdx = 0; batchIdx < batches.length; batchIdx++) {
        const schemeDetails: { [key: string]: object } = {};
        const batch = batches[batchIdx];
        console.log(`Processing batch ${batchIdx + 1} of ${batches.length}...`);

        let batchFailed = false;
        const results = await Promise.all(batch.map(async (slugId) => {
            try {
                const details = await fetchSchemeDetails(slugId);
                const { data } = details.data;
                console.log(`Fetched details for ${slugId}`);
                return { slugId, data };
            } catch (err) {
                console.error(`Failed to fetch details for ${slugId}:`, err);
                batchFailed = true;
                return null;
            }
        }));

        if (batchFailed) {
            console.error(`Batch ${batchIdx + 1} failed. Aborting further batches.`);
            break;
        }

        for (const result of results) {
            if (result) {
                schemeDetails[result.slugId] = result.data;
            }
        }

        // Save progress after each batch in the root details subfolder
        const outPath = path.join(rootDetailsDir, `schemes-details-${batchIdx}.json`);
        fs.writeFileSync(outPath, JSON.stringify(schemeDetails, null, 2), 'utf-8');
        console.log(`Batch ${batchIdx + 1} complete. JSON file updated.`);

        if (batchIdx < batches.length - 1) {
            console.log(`Waiting ${BATCH_DELAY_MS / 1000} seconds before next batch...`);
            await new Promise(res => setTimeout(res, BATCH_DELAY_MS));
        }
    }

    console.log('All batches complete. JSON file written: schemes-details.json');
}

// Entry point for CLI usage
const arg = process.argv[2];
if (arg === 'schemes') {
    scrapeData();
} else if (arg === 'details') {
    scrapeSchemeDetails();
} else {
    console.log('Usage: npx ts-node fetch_schemes.ts [schemes|details]');
    console.log('  schemes - Fetch all schemes and save to data/schemes.json');
    console.log('  details - Fetch details for all slugs and save to data/scheme-details/');
}