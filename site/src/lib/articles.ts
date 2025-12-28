/**
 * Article Types and Registry
 *
 * Defines the article structure with:
 * - Domain categorization (economics, technology, etc.)
 * - Category tags (Latest Research, Pushing the Boundaries)
 * - Reverse chronological ordering within domains
 */

export type ArticleCategory = "latest-research" | "pushing-boundaries";

export interface Article {
  slug: string;
  domain: string;
  title: string;
  description: string;
  readingTime: string;
  publishDate: string;
  category: ArticleCategory;
  tags?: string[];
}

export interface Domain {
  id: string;
  name: string;
  description: string;
}

// Domain definitions
export const domains: Domain[] = [
  {
    id: "economics",
    name: "Economics",
    description: "Data-driven explorations of economic concepts and indicators",
  },
  {
    id: "technology",
    name: "Technology",
    description: "Deep dives into technological trends and innovations",
  },
  {
    id: "climate",
    name: "Climate",
    description: "Analysis of climate data and environmental trends",
  },
];

// Category display info
export const categoryInfo: Record<ArticleCategory, { label: string; color: string; description: string }> = {
  "latest-research": {
    label: "Latest Research",
    color: "#2563eb",
    description: "Analysis based on current academic research and data",
  },
  "pushing-boundaries": {
    label: "Pushing the Boundaries",
    color: "#7c3aed",
    description: "Creative synthesis of research, projecting future possibilities",
  },
};

// Article registry - add new articles here
export const articles: Article[] = [
  {
    slug: "gdp/altair",
    domain: "economics",
    title: "GDP: Understanding the Economy's Measuring Stick",
    description:
      "A first-principles exploration of Gross Domestic Product—what it measures, how it's calculated, why it matters, and where it falls short.",
    readingTime: "47 min",
    publishDate: "2025-01-15",
    category: "latest-research",
    tags: ["gdp", "macroeconomics", "measurement"],
  },
];

/**
 * Get articles by domain, sorted reverse chronologically
 */
export function getArticlesByDomain(domainId: string): Article[] {
  return articles
    .filter((article) => article.domain === domainId)
    .sort((a, b) => new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime());
}

/**
 * Get all articles sorted reverse chronologically
 */
export function getAllArticles(): Article[] {
  return [...articles].sort(
    (a, b) => new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime()
  );
}

/**
 * Get articles by category
 */
export function getArticlesByCategory(category: ArticleCategory): Article[] {
  return articles
    .filter((article) => article.category === category)
    .sort((a, b) => new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime());
}

/**
 * Calculate reading time from word count
 * Uses 200 words per minute for dense technical content
 */
export function calculateReadingTime(wordCount: number): string {
  const minutes = Math.ceil(wordCount / 200);
  return `${minutes} min`;
}

/**
 * Validate that an article achieves target reading time
 * A true 1-hour read should have ~12,000 words minimum
 */
export function validateReadingTime(
  wordCount: number,
  targetMinutes: number
): { valid: boolean; actualMinutes: number; message: string } {
  const actualMinutes = Math.ceil(wordCount / 200);
  const tolerance = 5; // Allow 5 minutes variance

  if (Math.abs(actualMinutes - targetMinutes) <= tolerance) {
    return {
      valid: true,
      actualMinutes,
      message: `Reading time validated: ${actualMinutes} min`,
    };
  }

  return {
    valid: false,
    actualMinutes,
    message: `Expected ${targetMinutes} min but got ${actualMinutes} min (${wordCount} words). ` +
      `For ${targetMinutes} min, need ~${targetMinutes * 200} words.`,
  };
}
