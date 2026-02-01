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
import { readdir, mkdir, access, readFile } from "node:fs/promises";
import { join, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { createServer, type Server } from "node:http";
import { lookup } from "mime-types";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const DIST_DIR = join(__dirname, "..", "..", "docs");  // Astro outputs to ../docs
const OUTPUT_DIR = join(__dirname, "..", "..", "articles", "pdf");

// Start a simple static file server
async function startServer(port: number): Promise<{ server: Server; getStats: () => { ok: number; fail: number } }> {
  let okCount = 0;
  let failCount = 0;

  return new Promise((resolve) => {
    const server = createServer(async (req, res) => {
      const url = req.url || "/";
      // Remove /graphyard prefix if present
      const path = url.replace(/^\/graphyard/, "");
      const filePath = join(DIST_DIR, path);

      try {
        const content = await readFile(filePath);
        const mimeType = lookup(filePath) || "application/octet-stream";
        res.writeHead(200, { "Content-Type": mimeType });
        res.end(content);
        okCount++;
      } catch (err) {
        res.writeHead(404);
        res.end("Not found");
        failCount++;
        console.log(`    404: ${path}`);
      }
    });

    server.listen(port, () => resolve({
      server,
      getStats: () => ({ ok: okCount, fail: failCount }),
    }));
  });
}

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
  serverPort: number,
  config: PDFConfig = DEFAULT_CONFIG
): Promise<string> {
  const page: Page = await browser.newPage();

  // Load via HTTP server (supports /graphyard/ paths properly)
  const url = `http://localhost:${serverPort}/graphyard/articles/${articleSlug}/index.html`;
  console.log(`    Loading: ${url}`);
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

  // Disable lazy loading on all images so they load immediately
  await page.evaluate(() => {
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach((img) => {
      img.removeAttribute("loading");
      // Force reload by reassigning src
      const src = img.getAttribute("src");
      if (src) {
        img.setAttribute("src", "");
        img.setAttribute("src", src);
      }
    });
  });

  // Wait for network to settle after triggering image loads
  await page.waitForLoadState("networkidle", { timeout: 60000 });

  // Verify all images loaded
  const imageStatus = await page.evaluate(() => {
    const images = document.querySelectorAll("img");
    return {
      total: images.length,
      loaded: Array.from(images).filter((img) => img.complete && img.naturalWidth > 0).length,
    };
  });
  console.log(`    Images: ${imageStatus.loaded}/${imageStatus.total} loaded`);

  // Final wait for all images
  await page.evaluate(() => {
    const images = document.querySelectorAll("img");
    return Promise.all(
      Array.from(images).map((img) => {
        if (img.complete) return Promise.resolve();
        return new Promise((resolve) => {
          img.addEventListener("load", resolve);
          img.addEventListener("error", resolve);
          // Timeout after 10 seconds per image
          setTimeout(resolve, 10000);
        });
      })
    );
  });

  // Additional wait to ensure SVGs are fully rendered
  await page.waitForTimeout(2000);

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

  // Start local server to serve assets
  const PORT = 3847;
  const { server, getStats } = await startServer(PORT);
  console.log(`  Started local server on port ${PORT}`);

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
        const outputPath = await generatePDF(browser, article, PORT);
        console.log(`  ✓ Created: ${basename(outputPath)}\n`);
      } catch (error) {
        console.error(`  ✗ Failed: ${article}`);
        console.error(`    ${error instanceof Error ? error.message : error}\n`);
      }
    }

    const stats = getStats();
    console.log(`\nServer handled ${stats.ok} requests, ${stats.fail} failed`);
    console.log(`PDFs saved to: ${OUTPUT_DIR}`);
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
