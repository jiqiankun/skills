/* 模板与攻略检查：使用现有 Playwright，测试本地打开、窄屏、导航、跳过链接、打印和无脚本降级。 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const playwright = require('playwright');

function buildTemplateSamples() {
  const source = fs.readFileSync(path.join(__dirname, '../assets/guide-template.html'), 'utf8');
  const filled = source.replace(/\{\{([^}]+)\}\}/g, (_, label) => `检查内容：${label}`);
  const dayBlock = filled.match(/  <section id="day-1"[\s\S]*?\n  <\/section>/)[0];
  const days = [1, 2, 3, 4, 5].map(n => {
    const prev = n === 1 ? '<a href="#overview">← 返回总览</a>' : `<a href="#day-${n - 1}">← 返回 Day ${n - 1}</a>`;
    const next = n === 5 ? '<a class="next" href="#souvenirs">特产 →</a>' : `<a class="next" href="#day-${n + 1}">下一天：Day ${n + 1} →</a>`;
    return dayBlock
      .replaceAll('day-1', `day-${n}`)
      .replaceAll('Day 1', `Day ${n}`)
      .replace(/<nav class="pager"[\s\S]*?<\/nav>/, `<nav class="pager" aria-label="页面切换">\n      ${prev}\n      ${next}\n    </nav>`);
  });
  const indexItem = filled.match(/        <li>\s*<a class="day-link" href="#day-1"[\s\S]*?<\/li>/)[0];
  const full = filled
    .replace(dayBlock, days.join('\n'))
    .replace('<a href="#day-1">Day 1</a>', [1, 2, 3, 4, 5].map(n => `<a href="#day-${n}">Day ${n}</a>`).join('\n  '))
    .replace(indexItem, [1, 2, 3, 4, 5].map(n => indexItem.replaceAll('day-1', `day-${n}`).replaceAll('Day 1', `Day ${n}`)).join('\n'))
    .replace('<a href="#day-1">← 返回 Day 1</a>', '<a href="#day-5">← 返回 Day 5</a>');
  const minimal = filled
    .replace(/  <section id="souvenirs"[\s\S]*?\n  <\/section>/, '')
    .replace('  <a href="#souvenirs">特产</a>', '')
    .replace('<a class="next" href="#souvenirs">特产 →</a>', '<a class="next" href="#prep">准备清单 →</a>');
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'travel-guide-check-'));
  const files = [path.join(folder, 'full.html'), path.join(folder, 'minimal.html')];
  files.forEach((file, i) => fs.writeFileSync(file, [full, minimal][i]));
  return { folder, primary: files[0], minimal: files[1] };
}

async function checkStaticInvariants(page, rawHtml) {
  assert.equal(/\{\{[^}]+\}\}/.test(rawHtml), false, '存在未替换的模板占位符');
  const ids = await page.locator('[id]').evaluateAll(nodes => nodes.map(node => node.id));
  assert.equal(new Set(ids).size, ids.length, '存在重复 ID');
  const badAnchors = await page.locator('a[href^="#"]').evaluateAll(nodes =>
    nodes.filter(node => {
      const id = decodeURIComponent(node.getAttribute('href').slice(1));
      return !id || !document.getElementById(id);
    }).map(node => node.getAttribute('href'))
  );
  assert.deepEqual(badAnchors, [], `存在无效锚点：${badAnchors.join(', ')}`);
  const unsafeLinks = await page.locator('a[href]').evaluateAll(nodes =>
    nodes.map(node => node.getAttribute('href').trim()).filter(href => !/^(#|https?:\/\/)/i.test(href))
  );
  assert.deepEqual(unsafeLinks, [], `存在不安全链接协议：${unsafeLinks.join(', ')}`);
  const inlineHandlers = await page.evaluate(() =>
    [...document.querySelectorAll('*')].some(el => [...el.attributes].some(attr => /^on/i.test(attr.name)))
  );
  assert.equal(inlineHandlers, false, '存在内联事件属性');
  const missingAlt = await page.locator('img').evaluateAll(nodes =>
    nodes.filter(img => !img.getAttribute('alt') || !img.getAttribute('alt').trim()).length
  );
  assert.equal(missingAlt, 0, '存在缺少替代文字的图片');
}

(async () => {
  const targetArg = process.argv[2];
  const isCustomFile = Boolean(targetArg);
  const sample = isCustomFile
    ? { folder: null, primary: path.resolve(targetArg), minimal: null }
    : buildTemplateSamples();
  const primaryHtml = fs.readFileSync(sample.primary, 'utf8');
  let browser;
  try {
    const engine = process.env.GUIDE_ENGINE || 'chromium';
    assert(playwright[engine], '未知浏览器引擎');
    browser = await playwright[engine].launch({
      headless: true,
      ...(process.env.GUIDE_BROWSER ? { executablePath: process.env.GUIDE_BROWSER } : {})
    });
    const errors = [];
    for (const javaScriptEnabled of [true, false]) {
      const context = await browser.newContext({ javaScriptEnabled });
      const page = await context.newPage();
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(pathToFileURL(sample.primary).href);
      await checkStaticInvariants(page, primaryHtml);

      const pageIds = await page.locator('[data-page]').evaluateAll(nodes => nodes.map(node => node.id));
      assert(pageIds.length >= 2, '缺少页面区块 [data-page]');
      const dayId = pageIds.find(id => id.startsWith('day-')) || pageIds[1];
      const otherId = pageIds.find(id => id !== pageIds[0] && id !== dayId) || pageIds[0];

      for (const width of [360, 390, 430, 760, 1280]) {
        await page.setViewportSize({ width, height: 900 });
        await page.locator(`.nav a[href="#${dayId}"]`).click();
        await page.waitForURL(`**#${dayId}`);
        await page.locator(`#${dayId}`).waitFor({ state: 'visible' });
        await page.locator(`#${dayId} details`).evaluateAll(nodes => nodes.forEach(node => { node.open = true; }));
        if (!isCustomFile) {
          await page.locator(`#${dayId} h3`).first().evaluate(node => { node.textContent = '超长景点名称与地址'.repeat(15); });
          await page.locator(`#${dayId} .detail-body`).first().evaluate(node => { node.append('https://example.invalid/' + 'longaddress'.repeat(35)); });
        }
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, `${width}px 正文横向溢出`);
        const detailGridCount = await page.locator(`#${dayId} .detail-body.grid`).count();
        if (width < 640 && detailGridCount > 0) {
          assert.equal(await page.locator(`#${dayId} .detail-body.grid`).first().evaluate(node => getComputedStyle(node).gridTemplateColumns.split(' ').length), 1, '窄屏生成了多余网格列');
        }
        for (const control of await page.locator(`#${dayId} summary`).all()) {
          assert((await control.boundingBox()).height >= 44, '展开入口高度不足');
        }
      }

      await page.setViewportSize({ width: 390, height: 900 });
      const detailsCount = await page.locator(`#${dayId} details`).count();
      if (detailsCount > 0) {
        const firstDetails = page.locator(`#${dayId} details`).first();
        const summary = firstDetails.locator('summary');
        await firstDetails.evaluate(node => { node.open = false; });
        await summary.focus();
        await page.keyboard.press('Enter');
        assert.equal(await firstDetails.getAttribute('open'), '', '键盘不能展开');
        await page.keyboard.press('Space');
        assert.equal(await firstDetails.getAttribute('open'), null, '键盘不能收起');
        await summary.click();
      }
      await page.locator(`.nav a[href="#${otherId}"]`).click();
      await page.waitForURL(`**#${otherId}`);
      await page.locator(`#${otherId}`).waitFor({ state: 'visible' });
      await page.goBack();
      await page.waitForURL(`**#${dayId}`);
      await page.locator(`#${dayId}`).waitFor({ state: 'visible' });
      if (detailsCount > 0) {
        assert.equal(await page.locator(`#${dayId} details`).first().getAttribute('open'), '', '切页丢失展开状态');
      }

      if (javaScriptEnabled) {
        assert.equal(await page.locator('[data-page]:visible').count(), 1, '增强后未正确切页');
        const expectedTitleId = await page.locator(`#${dayId}`).getAttribute('aria-labelledby');
        assert.equal(await page.evaluate(() => document.activeElement.id), expectedTitleId, '焦点未进入新页面标题');
        const heading = await page.locator(`#${expectedTitleId}`).boundingBox();
        const nav = await page.locator('.nav').boundingBox();
        assert(heading.y >= nav.y + nav.height - 1, '吸顶导航遮挡标题');

        // 验证跳过导航（#main）在日程页不会误跳回总览。
        await page.locator('.skip-link').focus();
        await page.keyboard.press('Enter');
        await page.waitForURL('**#main');
        assert.equal(await page.locator(`#${dayId}`).isVisible(), true, '跳过导航把当前日程页重置回了总览');

        // 验证总览每日入口跳转（存在时）。
        await page.locator(`.nav a[href="#${pageIds[0]}"]`).click();
        await page.waitForURL(`**#${pageIds[0]}`);
        const dayLink = page.locator(`#${pageIds[0]} .day-link`).first();
        if (await dayLink.count()) {
          const href = await dayLink.getAttribute('href');
          await dayLink.click();
          await page.waitForURL(`**${href}`);
          assert.equal(await page.locator(href).isVisible(), true, '总览每日入口未能切换页面');
        }

        // 验证打印媒体下全部页面均可见。
        await page.emulateMedia({ media: 'print' });
        assert.equal(await page.locator('[data-page]:visible').count(), pageIds.length, '打印模式下未展示全部页面');
        await page.emulateMedia({ media: 'screen' });

        // 验证直达末页、页内锚点与异常锚点回退。
        const lastId = pageIds[pageIds.length - 1];
        await page.goto(`${pathToFileURL(sample.primary).href}#${lastId}`);
        assert.equal(await page.locator(`#${lastId}`).isVisible(), true, '无法直接进入目标页');
        if (await page.locator('#sources').count()) {
          await page.goto(`${pathToFileURL(sample.primary).href}#sources`);
          assert.equal(await page.locator(`#${pageIds[0]}`).isVisible(), true, '页内锚点未显示所属页面');
        }
        await page.goto(`${pathToFileURL(sample.primary).href}#%E0%A4%A`);
        assert.equal(await page.locator(`#${pageIds[0]}`).isVisible(), true, '异常锚点未回退总览');
      } else {
        assert.equal(await page.locator('[data-page]:visible').count(), pageIds.length, '无脚本时正文缺失');
      }

      if (sample.minimal) {
        const minimalHtml = fs.readFileSync(sample.minimal, 'utf8');
        await page.goto(`${pathToFileURL(sample.minimal).href}#prep`);
        await checkStaticInvariants(page, minimalHtml);
        assert.equal(await page.locator('#prep').isVisible(), true, '移除可选页后导航失败');
      }

      await page.goto(pathToFileURL(sample.primary).href);
      await page.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, '文字放大后横向溢出');
      await page.locator(`.nav a[href="#${dayId}"]`).click();
      await page.locator(`#${dayId} details`).evaluateAll(nodes => nodes.forEach(node => { node.open = true; }));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, '放大的时间轴横向溢出');
      await context.close();
    }

    // 主动让导航增强出错，验证已经隐藏的正文也能恢复。
    const fallback = await browser.newContext();
    const fallbackPage = await fallback.newPage();
    await fallbackPage.addInitScript(() => {
      Element.prototype.scrollIntoView = () => { throw new Error('模拟导航增强失败'); };
    });
    await fallbackPage.goto(pathToFileURL(sample.primary).href);
    const totalPages = await fallbackPage.locator('[data-page]').count();
    const fallbackTarget = await fallbackPage.locator('.nav a').nth(1).getAttribute('href');
    await fallbackPage.locator(`.nav a[href="${fallbackTarget}"]`).click();
    await fallbackPage.waitForURL(`**${fallbackTarget}`);
    await fallbackPage.locator(fallbackTarget).waitFor({ state: 'visible' });
    assert.equal(await fallbackPage.locator('[data-page]:visible').count(), totalPages, '增强失败后未恢复完整正文');
    await fallback.close();

    assert.deepEqual(errors, [], `浏览器脚本异常：${errors.join('; ')}`);
    console.log(`通过（${isCustomFile ? path.basename(sample.primary) : '模板样本'}）：本地打开、静态安全与占位符、五档宽度、长内容、键盘折叠、切页返回、跳过导航、总览入口、打印全页、锚点、文字放大与脚本失败降级。`);
  } finally {
    if (browser) await browser.close();
    if (sample.folder) fs.rmSync(sample.folder, { recursive: true, force: true });
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
