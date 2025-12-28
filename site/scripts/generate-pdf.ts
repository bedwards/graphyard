/**
 * PDF Generation Script
 *
 * Uses Playwright to render articles and export to PDF.
 * Designed for publication-quality output.
 *
 * Usage:
 *   npm run pdf                    # Generate all PDFs
 *   npm run pdf -- --article=gdp   # Generate specific article
 */

import { chromium, type Browser, type Page } from "playwright";
import { readdir, mkdir, access } from "node:fs/promises";
import { join, basename } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const DIST_DIR = join(__dirname, "..", "dist");
const OUTPUT_DIR = join(__dirname, "..", "dist", "pdf");

interface PDFConfig {
  format: "A4" | "Letter";
  margin: {
    top: string;
    right: string;
    bottom: string;
    left: string;
  };
  printBackground: boolean;
  displayHeaderFooter: boolean;
  headerTemplate: string;
  footerTemplate: string;
}

const DEFAULT_CONFIG: PDFConfig = {
  format: "A4",
  margin: {
    top: "1in",
    right: "0.75in",
    bottom: "1in",
    left: "0.75in",
  },
  printBackground: true,
  displayHeaderFooter: true,
  headerTemplate: `
    <div style="font-size: 9px; color: #666; width: 100%; text-align: center; font-family: 'Lexend', sans-serif;">
      <span class="title"></span>
    </div>
  `,
  footerTemplate: `
    <div style="font-size: 9px; color: #666; width: 100%; text-align: center; font-family: 'Lexend', sans-serif;">
      <span class="pageNumber"></span> / <span class="totalPages"></span>
    </div>
  `,
};

async function ensureDir(dir: string): Promise<void> {
  try {
    await access(dir);
  } catch {
    await mkdir(dir, { recursive: true });
  }
}

async function findArticles(): Promise<string[]> {
  const articlesDir = join(DIST_DIR, "articles");
  try {
    const entries = await readdir(articlesDir, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name);
  } catch {
    console.error("No articles directory found. Run 'npm run build' first.");
    return [];
  }
}

async function generatePDF(
  browser: Browser,
  articleSlug: string,
  config: PDFConfig = DEFAULT_CONFIG
): Promise<string> {
  const page: Page = await browser.newPage();

  // Load the built HTML file
  const articlePath = join(DIST_DIR, "articles", articleSlug, "index.html");
  await page.goto(`file://${articlePath}`, { waitUntil: "networkidle" });

  // Wait for fonts to load
  await page.evaluate(() => document.fonts.ready);

  // Wait for any lazy-loaded images
  await page.evaluate(() => {
    const images = document.querySelectorAll("img");
    return Promise.all(
      Array.from(images).map((img) => {
        if (img.complete) return Promise.resolve();
        return new Promise((resolve) => {
          img.addEventListener("load", resolve);
          img.addEventListener("error", resolve);
        });
      })
    );
  });

  // Generate PDF
  const outputPath = join(OUTPUT_DIR, `${articleSlug}.pdf`);
  await page.pdf({
    path: outputPath,
    format: config.format,
    margin: config.margin,
    printBackground: config.printBackground,
    displayHeaderFooter: config.displayHeaderFooter,
    headerTemplate: config.headerTemplate,
    footerTemplate: config.footerTemplate,
  });

  await page.close();
  return outputPath;
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const articleArg = args.find((arg) => arg.startsWith("--article="));
  const specificArticle = articleArg?.split("=")[1];

  console.log("PDF Generation");
  console.log("==============\n");

  await ensureDir(OUTPUT_DIR);

  const browser = await chromium.launch();

  try {
    let articles: string[];

    if (specificArticle) {
      articles = [specificArticle];
    } else {
      articles = await findArticles();
    }

    if (articles.length === 0) {
      console.log("No articles found to process.");
      return;
    }

    console.log(`Found ${articles.length} article(s) to process:\n`);

    for (const article of articles) {
      try {
        console.log(`  Generating: ${article}...`);
        const outputPath = await generatePDF(browser, article);
        console.log(`  ✓ Created: ${basename(outputPath)}\n`);
      } catch (error) {
        console.error(`  ✗ Failed: ${article}`);
        console.error(`    ${error instanceof Error ? error.message : error}\n`);
      }
    }

    console.log(`\nPDFs saved to: ${OUTPUT_DIR}`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
