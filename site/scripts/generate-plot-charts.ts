/**
 * Observable Plot Chart Generator
 *
 * Reads chart specifications from JSON and renders them using
 * Observable Plot, saving as SVG files.
 *
 * Usage:
 *   node --experimental-strip-types scripts/generate-plot-charts.ts
 */

import { readFileSync, writeFileSync, mkdirSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";

// Observable Plot requires a DOM environment
const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>");
global.document = dom.window.document;

import { renderChartToSVG, type ChartSpec } from "../src/lib/plot-renderer.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SPECS_DIR = join(__dirname, "..", "public", "assets", "charts", "specs");
const OUTPUT_DIR = join(__dirname, "..", "public", "assets", "charts", "plot");

async function main(): Promise<void> {
  console.log("\n  Observable Plot Chart Generator");
  console.log("  ================================\n");

  // Ensure output directory exists
  mkdirSync(OUTPUT_DIR, { recursive: true });

  // Read manifest
  const manifestPath = join(SPECS_DIR, "manifest.json");
  let manifest: Array<{ chartId: string; specFile: string }>;

  try {
    const manifestContent = readFileSync(manifestPath, "utf-8");
    manifest = JSON.parse(manifestContent);
  } catch (error) {
    console.error(`  [ERROR] Could not read manifest: ${manifestPath}`);
    console.error(`          Run the Python generator first to create specs.`);
    process.exit(1);
  }

  console.log(`  Found ${manifest.length} chart specifications\n`);

  let successCount = 0;

  for (const entry of manifest) {
    try {
      // Read spec
      const specPath = join(SPECS_DIR, entry.specFile);
      const specContent = readFileSync(specPath, "utf-8");
      const spec: ChartSpec = JSON.parse(specContent);

      console.log(`  Rendering: ${spec.chartId}`);

      // Render to SVG
      const svg = renderChartToSVG(spec);

      // Save
      const outputPath = join(OUTPUT_DIR, `${spec.chartId}.svg`);
      writeFileSync(outputPath, svg);
      console.log(`  [Plot] Saved: ${spec.chartId}.svg`);

      successCount++;
    } catch (error) {
      console.error(`  [ERROR] ${entry.chartId}: ${error}`);
    }
  }

  console.log(`\n  Observable Plot: ${successCount}/${manifest.length} charts generated`);
  console.log(`  Output: ${OUTPUT_DIR}\n`);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
