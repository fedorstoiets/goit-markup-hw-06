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
    const styles = await page.evaluate(() => {
      const css = (s) => getComputedStyle(document.querySelector(s));
      const px = (selector, prop) => css(selector).getPropertyValue(prop).trim();
      const logo = document.querySelector(".logo").getBoundingClientRect();
      const nav = document.querySelector(".primary-navigation").getBoundingClientRect();
      const foot = document.querySelector(".footer-container").getBoundingClientRect();
      return {
        containerMaxWidth: px(".container", "max-width"),
        titleMaxWidth: px(".hero-title", "max-width"),
        titleMarginBottom: px(".hero-title", "margin-bottom"),
        featuresFontSize: px(".features-subtitle", "font-size"),
        featuresWeight: px(".features-subtitle", "font-weight"),
        featuresBodyWeight: px(".features-text", "font-weight"),
        footerPaddingTop: px(".site-bottom", "padding-top"),
        footerPaddingBottom: px(".site-bottom", "padding-bottom"),
        footerInputWidth: document.querySelector(".footer-subscribe-input").getBoundingClientRect().width,
        footerLeftMargin: foot.left,
        footerRightMargin: window.innerWidth - foot.right,
        logoNavGap: nav.left - logo.right,
        addressGap: px(".address-list", "gap"),
        addressLetterSpacing: px(".address-link", "letter-spacing")
      };
    });
    console.log(JSON.stringify({width,styles}));
    const approx=(a,b,tol=1)=>Math.abs(Number.parseFloat(a)-b)<=tol;
    if ((width===320 && !(styles.containerMaxWidth==="320px" &&
         styles.titleMaxWidth==="216px" && approx(styles.titleMarginBottom,72) &&
         styles.featuresFontSize==="36px" && styles.featuresWeight==="700" &&
         approx(styles.footerPaddingTop,96))) ||
        (width===768 && !(approx(styles.logoNavGap,120) &&
         approx(styles.addressGap,12) && approx(styles.titleMarginBottom,36) &&
         styles.featuresFontSize==="36px" && styles.featuresWeight==="700" &&
         Math.abs(styles.footerLeftMargin-styles.footerRightMargin)<=1)) ||
        (width===1158 && !(approx(styles.titleMarginBottom,48) &&
         approx(styles.footerPaddingTop,100)))) {
      console.error("Formal computed CSS requirement failure", width, styles);
      failed=true;
    }

    if (width === 320) {
      await page.locator("[data-menu-open]").click();
      await page.waitForFunction(() => { const e = document.querySelector("[data-menu]"); return e.classList.contains("is-open") && getComputedStyle(e).visibility === "visible"; }, { timeout: 3000 });
      const shown = true;
      if (!shown) { console.error("Mobile menu is-open toggle failed"); failed=true; }
      await page.locator("[data-menu-close]").click();
      await page.waitForFunction(() => getComputedStyle(document.querySelector("[data-menu]")).visibility === "hidden", { timeout: 3000 });
      const hidden = true;
      if (!hidden) { console.error("Mobile menu hiding failed"); failed=true; }
    }
    await page.close();
  }
  await browser.close();
  if (failed) process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
