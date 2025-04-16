// 生成JavaScript脚本，自动登录京东，抓取手机价格数据，每小时更新一次
const puppeteer = require('puppeteer');

async function monitor() {
    const browser = await puppeteer.launch({ headless: false }); // 设置为非无头模式以便调试
    const page = await browser.newPage();

    // 设置用户代理和请求头
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
    await page.setExtraHTTPHeaders({ 'Referer': 'https://www.baidu.com' });

    // 打开京东首页
    await page.goto('https://www.jd.com');

    // 自动登录逻辑（需补充账号密码）
    await page.click('.link-login'); // 点击登录按钮
    await page.waitForSelector('#loginname'); // 等待用户名输入框加载
    await page.type('#loginname', 'your_username'); // 替换为你的京东用户名
    await page.type('#nloginpwd', 'your_password'); // 替换为你的京东密码
    await page.click('.login-btn'); // 点击登录按钮
    await page.waitForNavigation(); // 等待页面跳转

    // 价格抓取逻辑
    await page.goto('https://search.jd.com/Search?keyword=手机'); // 搜索手机
    await page.waitForSelector('.gl-item'); // 等待商品列表加载

    const prices = await page.evaluate(() => {
        const items = document.querySelectorAll('.gl-item .p-price');
        return Array.from(items).map(item => item.innerText.trim());
    });

    console.log('抓取到的手机价格数据:', prices);

    await browser.close();
}

// 每小时执行一次
setInterval(monitor, 3600000);

// 立即执行一次以便测试
monitor().catch(console.error);

// Removed invalid JSON-like block to fix the syntax error.