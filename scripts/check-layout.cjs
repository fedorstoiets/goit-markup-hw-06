const { chromium } = require("playwright");
const { pathToFileURL } = require("node:url");
const path = require("node:path");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const url = pathToFileURL(path.resolve("index.html")).href;
  const sizes = [320, 375, 428, 767, 768, 1024, 1158, 1440];
  let failed = false;
  for (const width of sizes) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
    await page.goto(url, { waitUntil: "domcontentloaded" });
    const result = await page.evaluate(() => {
      const doc = document.documentElement;
      const team = document.querySelector(".team-item");
      return {
        viewport: window.innerWidth,
        documentWidth: doc.scrollWidth,
        bodyWidth: document.body.scrollWidth,
        teamWidth: team?.getBoundingClientRect().width,
        offenders: [...document.querySelectorAll("body *")]
          .filter(el => {
            const r=el.getBoundingClientRect();
            const st=getComputedStyle(el);
            return st.position !== "fixed" && st.visibility !== "hidden" && r.width>0 && (r.right > window.innerWidth + 1 || r.left < -1);
          })
          .slice(0, 8).map(el => ({ tag:el.tagName, cls:el.className?.baseVal || el.className }))
      };
    });
    const bad=result.documentWidth > width + 1 || result.bodyWidth > width + 1 || Math.abs(result.teamWidth - 264) > 1;
    console.log(JSON.stringify({width, ...result, pass:!bad}));
    if (bad) failed=true;
    if (width === 320) {
      await page.locator("[data-menu-open]").click();
      const shown = await page.locator("[data-menu]").evaluate(e => e.classList.contains("is-open") && getComputedStyle(e).visibility === "visible");
      if (!shown) { console.error("Mobile menu is-open toggle failed"); failed=true; }
      await page.locator("[data-menu-close]").click();
      const hidden = await page.locator("[data-menu]").evaluate(e => getComputedStyle(e).visibility === "hidden");
      if (!hidden) { console.error("Mobile menu hiding failed"); failed=true; }
    }
    await page.close();
  }
  await browser.close();
  if (failed) process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
