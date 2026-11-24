const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const browser = await chromium.launch({ proxy });
  const ctx = await browser.newContext({ locale: 'ko-KR', viewport: { width: 1280, height: 1000 } });
  for (const id of process.argv.slice(2)) {
    const page = await ctx.newPage();
    const url = `https://www.airbnb.co.kr/rooms/${id}?check_in=2027-01-30&check_out=2027-02-03&adults=1&currency=KRW`;
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(9000);
      for (const sel of ['button[aria-label="닫기"]']) { const b = page.locator(sel).first(); if (await b.isVisible().catch(() => false)) await b.click().catch(() => {}); }
      const more = page.locator('[data-section-id="DESCRIPTION_DEFAULT"] button').first();
      if (await more.isVisible().catch(() => false)) { await more.click().catch(() => {}); await page.waitForTimeout(2500); }
      const text = await page.evaluate(() => document.body.innerText);
      fs.writeFileSync(`pw/${id}.txt`, text);
      await page.screenshot({ path: `pw/${id}.png` });
      console.log(id, 'ok', text.length);
    } catch (e) { console.log(id, 'ERR', e.message.slice(0, 120)); }
    await page.close();
  }
  await browser.close();
})();
