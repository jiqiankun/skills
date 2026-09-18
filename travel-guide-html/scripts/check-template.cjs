/* 模板维护检查：使用现有 Playwright，测试本地打开、窄屏、导航和无脚本降级。 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const playwright = require('playwright');

(async () => {
  const source = fs.readFileSync(path.join(__dirname, '../assets/guide-template.html'), 'utf8');
  const filled = source.replace(/\{\{([^}]+)\}\}/g, (_, label) => `检查内容：${label}`);
  const day = filled.match(/  <section id="day-1"[\s\S]*?\n  <\/section>/)[0];
  const extraDays = [2, 3, 4, 5].map(n => day.replaceAll('day-1', `day-${n}`).replaceAll('Day 1', `Day ${n}`));
  const full = filled.replace(day, [day, ...extraDays].join('\n')).replace(
    '<a href="#day-1">Day 1</a>',
    [1, 2, 3, 4, 5].map(n => `<a href="#day-${n}">Day ${n}</a>`).join('\n')
  );
  const minimal = filled.replace(/  <section id="souvenirs"[\s\S]*?\n  <\/section>/, '')
    .replace('  <a href="#souvenirs">特产</a>', '');
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'travel-guide-check-'));
  const files = [path.join(folder, 'full.html'), path.join(folder, 'minimal.html')];
  files.forEach((file, i) => fs.writeFileSync(file, [full, minimal][i]));
  let browser;
  try {
    const engine = process.env.GUIDE_ENGINE || 'chromium';
    assert(playwright[engine], '未知浏览器引擎');
    browser = await playwright[engine].launch({ headless: true, ...(process.env.GUIDE_BROWSER ? { executablePath: process.env.GUIDE_BROWSER } : {}) });
    const errors = [];
    for (const javaScriptEnabled of [true, false]) {
      const context = await browser.newContext({ javaScriptEnabled });
      const page = await context.newPage();
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(pathToFileURL(files[0]).href);
      const ids = await page.locator('[id]').evaluateAll(nodes => nodes.map(node => node.id));
      assert.equal(new Set(ids).size, ids.length, '存在重复 ID');
      assert.equal(await page.locator('a[href^="#"]').evaluateAll(nodes => nodes.every(node => document.getElementById(node.hash.slice(1)))), true, '存在无效锚点');

      for (const width of [360, 390, 430, 760, 1280]) {
        await page.setViewportSize({ width, height: 900 });
        await page.locator('.nav a[href="#day-1"]').click();
        await page.waitForURL('**#day-1');
        await page.locator('#day-1').waitFor({ state: 'visible' });
        await page.locator('#day-1 details').evaluateAll(nodes => nodes.forEach(node => { node.open = true; }));
        await page.locator('#day-1 h3').first().evaluate(node => { node.textContent = '超长景点名称与地址'.repeat(15); });
        await page.locator('#day-1 .detail-body').first().evaluate(node => { node.append('https://example.invalid/' + 'longaddress'.repeat(35)); });
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, `${width}px 正文横向溢出`);
        if (width < 640) assert.equal(await page.locator('#day-1 .detail-body.grid').first().evaluate(node => getComputedStyle(node).gridTemplateColumns.split(' ').length), 1, '窄屏生成了多余网格列');
        for (const control of await page.locator('#day-1 summary').all()) {
          assert((await control.boundingBox()).height >= 44, '展开入口高度不足');
        }
      }

      await page.setViewportSize({ width: 390, height: 900 });
      const summary = page.locator('#day-1 details summary').first();
      await page.locator('#day-1 details').first().evaluate(node => { node.open = false; });
      await summary.focus();
      await page.keyboard.press('Enter');
      assert.equal(await page.locator('#day-1 details').first().getAttribute('open'), '', '键盘不能展开');
      await page.keyboard.press('Space');
      assert.equal(await page.locator('#day-1 details').first().getAttribute('open'), null, '键盘不能收起');
      await summary.click();
      await page.locator('.nav a[href="#prep"]').click();
      await page.waitForURL('**#prep');
      await page.locator('#prep').waitFor({ state: 'visible' });
      await page.goBack();
      await page.waitForURL('**#day-1');
      await page.locator('#day-1').waitFor({ state: 'visible' });
      assert.equal(await page.locator('#day-1 details').first().getAttribute('open'), '', '切页丢失展开状态');
      if (javaScriptEnabled) {
        assert.equal(await page.locator('[data-page]:visible').count(), 1, '增强后未正确切页');
        assert.equal(await page.evaluate(() => document.activeElement.id), 'day-1-title', '焦点未进入新页面标题');
        const heading = await page.locator('#day-1-title').boundingBox();
        const nav = await page.locator('.nav').boundingBox();
        assert(heading.y >= nav.y + nav.height - 1, '吸顶导航遮挡标题');
        await page.goto(pathToFileURL(files[0]).href + '#day-5');
        assert.equal(await page.locator('#day-5').isVisible(), true, '无法直接进入某日');
        await page.goto(pathToFileURL(files[0]).href + '#sources');
        assert.equal(await page.locator('#overview').isVisible(), true, '页内锚点未显示所属页面');
        await page.goto(pathToFileURL(files[0]).href + '#%E0%A4%A');
        assert.equal(await page.locator('#overview').isVisible(), true, '异常锚点未回退总览');
      } else {
        assert.equal(await page.locator('[data-page]:visible').count(), 8, '无脚本时正文缺失');
      }
      await page.goto(pathToFileURL(files[1]).href + '#prep');
      assert.equal(await page.locator('#prep').isVisible(), true, '移除可选页后导航失败');
      await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, '文字放大后横向溢出');
      await page.locator('.nav a[href="#day-1"]').click();
      await page.locator('#day-1 details').evaluateAll(nodes => nodes.forEach(node => { node.open = true; }));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, '放大的时间轴横向溢出');
      await context.close();
    }
    // 主动让导航增强出错，验证已经隐藏的正文也能恢复。
    const fallback = await browser.newContext();
    const fallbackPage = await fallback.newPage();
    await fallbackPage.addInitScript(() => {
      Element.prototype.scrollIntoView = () => { throw new Error('模拟导航增强失败'); };
    });
    await fallbackPage.goto(pathToFileURL(files[0]).href);
    await fallbackPage.locator('.nav a[href="#day-1"]').click();
    await fallbackPage.waitForURL('**#day-1');
    await fallbackPage.locator('#day-1').waitFor({ state: 'visible' });
    assert.equal(await fallbackPage.locator('[data-page]:visible').count(), 8, '增强失败后未恢复完整正文');
    await fallback.close();
    assert.deepEqual(errors, [], '浏览器脚本异常');
    console.log('通过：本地打开、五档宽度、长内容、键盘折叠、切页返回、锚点、可选页、文字放大与脚本失败降级。');
  } finally {
    if (browser) await browser.close();
    files.forEach(file => fs.unlinkSync(file));
    fs.rmdirSync(folder);
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
