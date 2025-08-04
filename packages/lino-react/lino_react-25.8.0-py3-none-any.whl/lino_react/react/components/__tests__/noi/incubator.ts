import * as t from '../../types';
import * as constants from "../../constants";
import { setTimeout } from "timers/promises";

describe("noi/incubator.ts", () => {
    it.skip("placeholder", async () => {});

    let page;

    beforeAll(async () => {
        page = await globalThis.__BROWSER_GLOBAL__.newPage();
        // page.on("console", message => console.log(message.text()));
        await global.wait.runserverInit();
        await page.setDefaultNavigationTimeout(0);
    });

    beforeEach(async () => {
        await page.goto(global.SERVER_URL);
        await page.waitForNetworkIdle();
        await global.signIn(page);
    });

    afterAll(async () => {
        await page.close();
    });

    it("Eject button on CommentsByRFC body", async () => {
        await page.evaluate(() => {
            window.App.URLContext.history.pushPath({
                pathname: "/api/tickets/AllTickets/1"
            });
        });
        await page.waitForNetworkIdle();

        const getSlaveHtml = async () => {
            return await page.evaluate(() => {
                return window.App.URLContext.dataContext.refStore
                    .slaveLeaves["comments.CommentsByRFC"].state.value;
            });
        }

        let html = await getSlaveHtml();
        if (html === '<div class="htmlText"></div>') {
            await page.locator("button>span.pi-angle-double-left").click();
            await page.waitForNetworkIdle();

            html = await getSlaveHtml();
        }

        while (html === '<div class="htmlText"></div>') {
            await page.locator("button>span.pi-angle-right").click();
            await page.waitForNetworkIdle();

            html = await getSlaveHtml();
        }

        await page.waitForSelector("div.p-panel-header>span::-p-text(Comments)");
        const headerTitle = await page.$("div.p-panel-header>span::-p-text(Comments)");
        const header = await headerTitle.getProperty("parentElement");
        await headerTitle.dispose();
        const eject = await header.$("::-p-text(⏏)");
        await header.dispose();
        await eject.click();
        await eject.dispose();
        await page.waitForNetworkIdle();

        await page.locator("div.p-button>i.pi-table").click();
        await page.waitForNetworkIdle();

        await page.locator("::-p-text(⏏)").click();
        await page.waitForNetworkIdle();

        await setTimeout(3000);
    });
});
