const puppeteer = require("puppeteer");
const { axe, toHaveNoViolations } = require("jest-axe");

expect.extend(toHaveNoViolations);

describe("Accessibility Tests", () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch({ args: ["--no-sandbox"] });
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  it("should have no accessibility violations", async () => {
    await page.goto("http://localhost:3000"); // Container-URL
    await page.waitForSelector("body");

    const html = await page.content();
    const results = await axe(html);

    expect(results).toHaveNoViolations();
  });
});
