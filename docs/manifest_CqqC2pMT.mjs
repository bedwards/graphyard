import '@astrojs/internal-helpers/path';
import '@astrojs/internal-helpers/remote';
import 'piccolore';
import 'html-escaper';
import 'clsx';
import { N as NOOP_MIDDLEWARE_HEADER, j as decodeKey } from './chunks/astro/server_BRFjjATV.mjs';
import 'es-module-lexer';

const NOOP_MIDDLEWARE_FN = async (_ctx, next) => {
  const response = await next();
  response.headers.set(NOOP_MIDDLEWARE_HEADER, "true");
  return response;
};

const codeToStatusMap = {
  // Implemented from IANA HTTP Status Code Registry
  // https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  PAYMENT_REQUIRED: 402,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  NOT_ACCEPTABLE: 406,
  PROXY_AUTHENTICATION_REQUIRED: 407,
  REQUEST_TIMEOUT: 408,
  CONFLICT: 409,
  GONE: 410,
  LENGTH_REQUIRED: 411,
  PRECONDITION_FAILED: 412,
  CONTENT_TOO_LARGE: 413,
  URI_TOO_LONG: 414,
  UNSUPPORTED_MEDIA_TYPE: 415,
  RANGE_NOT_SATISFIABLE: 416,
  EXPECTATION_FAILED: 417,
  MISDIRECTED_REQUEST: 421,
  UNPROCESSABLE_CONTENT: 422,
  LOCKED: 423,
  FAILED_DEPENDENCY: 424,
  TOO_EARLY: 425,
  UPGRADE_REQUIRED: 426,
  PRECONDITION_REQUIRED: 428,
  TOO_MANY_REQUESTS: 429,
  REQUEST_HEADER_FIELDS_TOO_LARGE: 431,
  UNAVAILABLE_FOR_LEGAL_REASONS: 451,
  INTERNAL_SERVER_ERROR: 500,
  NOT_IMPLEMENTED: 501,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
  HTTP_VERSION_NOT_SUPPORTED: 505,
  VARIANT_ALSO_NEGOTIATES: 506,
  INSUFFICIENT_STORAGE: 507,
  LOOP_DETECTED: 508,
  NETWORK_AUTHENTICATION_REQUIRED: 511
};
Object.entries(codeToStatusMap).reduce(
  // reverse the key-value pairs
  (acc, [key, value]) => ({ ...acc, [value]: key }),
  {}
);

function sanitizeParams(params) {
  return Object.fromEntries(
    Object.entries(params).map(([key, value]) => {
      if (typeof value === "string") {
        return [key, value.normalize().replace(/#/g, "%23").replace(/\?/g, "%3F")];
      }
      return [key, value];
    })
  );
}
function getParameter(part, params) {
  if (part.spread) {
    return params[part.content.slice(3)] || "";
  }
  if (part.dynamic) {
    if (!params[part.content]) {
      throw new TypeError(`Missing parameter: ${part.content}`);
    }
    return params[part.content];
  }
  return part.content.normalize().replace(/\?/g, "%3F").replace(/#/g, "%23").replace(/%5B/g, "[").replace(/%5D/g, "]");
}
function getSegment(segment, params) {
  const segmentPath = segment.map((part) => getParameter(part, params)).join("");
  return segmentPath ? "/" + segmentPath : "";
}
function getRouteGenerator(segments, addTrailingSlash) {
  return (params) => {
    const sanitizedParams = sanitizeParams(params);
    let trailing = "";
    if (addTrailingSlash === "always" && segments.length) {
      trailing = "/";
    }
    const path = segments.map((segment) => getSegment(segment, sanitizedParams)).join("") + trailing;
    return path || "/";
  };
}

function deserializeRouteData(rawRouteData) {
  return {
    route: rawRouteData.route,
    type: rawRouteData.type,
    pattern: new RegExp(rawRouteData.pattern),
    params: rawRouteData.params,
    component: rawRouteData.component,
    generate: getRouteGenerator(rawRouteData.segments, rawRouteData._meta.trailingSlash),
    pathname: rawRouteData.pathname || void 0,
    segments: rawRouteData.segments,
    prerender: rawRouteData.prerender,
    redirect: rawRouteData.redirect,
    redirectRoute: rawRouteData.redirectRoute ? deserializeRouteData(rawRouteData.redirectRoute) : void 0,
    fallbackRoutes: rawRouteData.fallbackRoutes.map((fallback) => {
      return deserializeRouteData(fallback);
    }),
    isIndex: rawRouteData.isIndex,
    origin: rawRouteData.origin
  };
}

function deserializeManifest(serializedManifest) {
  const routes = [];
  for (const serializedRoute of serializedManifest.routes) {
    routes.push({
      ...serializedRoute,
      routeData: deserializeRouteData(serializedRoute.routeData)
    });
    const route = serializedRoute;
    route.routeData = deserializeRouteData(serializedRoute.routeData);
  }
  const assets = new Set(serializedManifest.assets);
  const componentMetadata = new Map(serializedManifest.componentMetadata);
  const inlinedScripts = new Map(serializedManifest.inlinedScripts);
  const clientDirectives = new Map(serializedManifest.clientDirectives);
  const serverIslandNameMap = new Map(serializedManifest.serverIslandNameMap);
  const key = decodeKey(serializedManifest.key);
  return {
    // in case user middleware exists, this no-op middleware will be reassigned (see plugin-ssr.ts)
    middleware() {
      return { onRequest: NOOP_MIDDLEWARE_FN };
    },
    ...serializedManifest,
    assets,
    componentMetadata,
    inlinedScripts,
    clientDirectives,
    routes,
    serverIslandNameMap,
    key
  };
}

const manifest = deserializeManifest({"hrefRoot":"file:///Users/bedwards/graphyard/site/","cacheDir":"file:///Users/bedwards/graphyard/site/node_modules/.astro/","outDir":"file:///Users/bedwards/graphyard/docs/","srcDir":"file:///Users/bedwards/graphyard/site/src/","publicDir":"file:///Users/bedwards/graphyard/site/public/","buildClientDir":"file:///Users/bedwards/graphyard/docs/client/","buildServerDir":"file:///Users/bedwards/graphyard/docs/server/","adapterName":"","routes":[{"file":"file:///Users/bedwards/graphyard/docs/articles/baseball/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/baseball/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/baseball\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"baseball","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/baseball/altair.astro","pathname":"/articles/baseball/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/beyond-growth/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/beyond-growth/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/beyond-growth\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"beyond-growth","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/beyond-growth/altair.astro","pathname":"/articles/beyond-growth/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/blood-money/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/blood-money/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/blood-money\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"blood-money","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/blood-money/altair.astro","pathname":"/articles/blood-money/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/blood-money/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/blood-money","isIndex":true,"type":"page","pattern":"^\\/articles\\/blood-money\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"blood-money","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/blood-money/index.astro","pathname":"/articles/blood-money","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/cubs-2016/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/cubs-2016/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/cubs-2016\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"cubs-2016","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/cubs-2016/altair.astro","pathname":"/articles/cubs-2016/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/education/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/education/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/education\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"education","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/education/altair.astro","pathname":"/articles/education/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/gdp/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/gdp/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/gdp\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"gdp","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/gdp/altair.astro","pathname":"/articles/gdp/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/gdp/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/gdp","isIndex":true,"type":"page","pattern":"^\\/articles\\/gdp\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"gdp","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/gdp/index.astro","pathname":"/articles/gdp","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/learning-styles/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/learning-styles/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/learning-styles\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"learning-styles","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/learning-styles/altair.astro","pathname":"/articles/learning-styles/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/march-madness/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/march-madness/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/march-madness\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"march-madness","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/march-madness/altair.astro","pathname":"/articles/march-madness/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/articles/marx/altair/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/articles/marx/altair","isIndex":false,"type":"page","pattern":"^\\/articles\\/marx\\/altair\\/?$","segments":[[{"content":"articles","dynamic":false,"spread":false}],[{"content":"marx","dynamic":false,"spread":false}],[{"content":"altair","dynamic":false,"spread":false}]],"params":[],"component":"src/pages/articles/marx/altair.astro","pathname":"/articles/marx/altair","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}},{"file":"file:///Users/bedwards/graphyard/docs/index.html","links":[],"scripts":[],"styles":[],"routeData":{"route":"/","isIndex":true,"type":"page","pattern":"^\\/$","segments":[],"params":[],"component":"src/pages/index.astro","pathname":"/","prerender":true,"fallbackRoutes":[],"distURL":[],"origin":"project","_meta":{"trailingSlash":"ignore"}}}],"site":"https://bedwards.github.io","base":"/graphyard","trailingSlash":"ignore","compressHTML":true,"componentMetadata":[["/Users/bedwards/graphyard/site/src/pages/articles/baseball/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/beyond-growth/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/blood-money/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/blood-money/index.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/cubs-2016/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/education/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/gdp/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/learning-styles/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/march-madness/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/articles/marx/altair.astro",{"propagation":"none","containsHead":true}],["/Users/bedwards/graphyard/site/src/pages/index.astro",{"propagation":"none","containsHead":true}]],"renderers":[],"clientDirectives":[["idle","(()=>{var l=(n,t)=>{let i=async()=>{await(await n())()},e=typeof t.value==\"object\"?t.value:void 0,s={timeout:e==null?void 0:e.timeout};\"requestIdleCallback\"in window?window.requestIdleCallback(i,s):setTimeout(i,s.timeout||200)};(self.Astro||(self.Astro={})).idle=l;window.dispatchEvent(new Event(\"astro:idle\"));})();"],["load","(()=>{var e=async t=>{await(await t())()};(self.Astro||(self.Astro={})).load=e;window.dispatchEvent(new Event(\"astro:load\"));})();"],["media","(()=>{var n=(a,t)=>{let i=async()=>{await(await a())()};if(t.value){let e=matchMedia(t.value);e.matches?i():e.addEventListener(\"change\",i,{once:!0})}};(self.Astro||(self.Astro={})).media=n;window.dispatchEvent(new Event(\"astro:media\"));})();"],["only","(()=>{var e=async t=>{await(await t())()};(self.Astro||(self.Astro={})).only=e;window.dispatchEvent(new Event(\"astro:only\"));})();"],["visible","(()=>{var a=(s,i,o)=>{let r=async()=>{await(await s())()},t=typeof i.value==\"object\"?i.value:void 0,c={rootMargin:t==null?void 0:t.rootMargin},n=new IntersectionObserver(e=>{for(let l of e)if(l.isIntersecting){n.disconnect(),r();break}},c);for(let e of o.children)n.observe(e)};(self.Astro||(self.Astro={})).visible=a;window.dispatchEvent(new Event(\"astro:visible\"));})();"]],"entryModules":{"\u0000noop-middleware":"_noop-middleware.mjs","\u0000virtual:astro:actions/noop-entrypoint":"noop-entrypoint.mjs","\u0000@astro-page:src/pages/articles/baseball/altair@_@astro":"pages/articles/baseball/altair.astro.mjs","\u0000@astro-page:src/pages/articles/beyond-growth/altair@_@astro":"pages/articles/beyond-growth/altair.astro.mjs","\u0000@astro-page:src/pages/articles/blood-money/altair@_@astro":"pages/articles/blood-money/altair.astro.mjs","\u0000@astro-page:src/pages/articles/blood-money/index@_@astro":"pages/articles/blood-money.astro.mjs","\u0000@astro-page:src/pages/articles/cubs-2016/altair@_@astro":"pages/articles/cubs-2016/altair.astro.mjs","\u0000@astro-page:src/pages/articles/education/altair@_@astro":"pages/articles/education/altair.astro.mjs","\u0000@astro-page:src/pages/articles/gdp/altair@_@astro":"pages/articles/gdp/altair.astro.mjs","\u0000@astro-page:src/pages/articles/gdp/index@_@astro":"pages/articles/gdp.astro.mjs","\u0000@astro-page:src/pages/articles/learning-styles/altair@_@astro":"pages/articles/learning-styles/altair.astro.mjs","\u0000@astro-page:src/pages/articles/march-madness/altair@_@astro":"pages/articles/march-madness/altair.astro.mjs","\u0000@astro-page:src/pages/articles/marx/altair@_@astro":"pages/articles/marx/altair.astro.mjs","\u0000@astro-page:src/pages/index@_@astro":"pages/index.astro.mjs","\u0000@astro-renderers":"renderers.mjs","\u0000@astrojs-manifest":"manifest_CqqC2pMT.mjs","/Users/bedwards/graphyard/site/src/pages/articles/gdp/index.astro?astro&type=script&index=0&lang.ts":"_astro/index.astro_astro_type_script_index_0_lang.Bn23bm0R.js","astro:scripts/before-hydration.js":""},"inlinedScripts":[["/Users/bedwards/graphyard/site/src/pages/articles/gdp/index.astro?astro&type=script&index=0&lang.ts","window.location.href=\"/graphyard/articles/gdp/altair/\";"]],"assets":["/graphyard/file:///Users/bedwards/graphyard/docs/articles/baseball/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/beyond-growth/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/blood-money/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/blood-money/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/cubs-2016/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/education/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/gdp/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/gdp/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/learning-styles/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/march-madness/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/articles/marx/altair/index.html","/graphyard/file:///Users/bedwards/graphyard/docs/index.html"],"buildFormat":"directory","checkOrigin":false,"allowedDomains":[],"serverIslandNameMap":[],"key":"4ZwPMiW6qTZvdqoh8iwiLgOAPAChsNF8b1/2uHKc6+Q="});
if (manifest.sessionConfig) manifest.sessionConfig.driverModule = null;

export { manifest };
