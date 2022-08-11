// ==UserScript==
// @name         Taobao Superbuy Interface
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Crawl taobao bought-items data
// @author       Hykilpikonna
// @match        https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=taobao.com
// @grant        none
// ==/UserScript==

(async function() {
    'use strict';

    const GBK = new TextDecoder('GBK')

    /**
     * Get taobao bought item links
     *
     * @returns {{id: string, date: string, store: {name: string, url: string}, items:
     *              {name: string, url: string, sel?: string[][], promises?: string[], price: string, origPrice?: string,
     *              qty: string}[]}[]}
     */
    async function getTaobaoLinks()
    {
        let orders = [...document.querySelectorAll('.bought-wrapper-mod__trade-order___2lrzV')]
        // orders = [orders[0]]

        return await Promise.all(orders.map(async o =>
        {
            const order = {}
            order.id = o.getAttribute('data-id')

            // Header info
            const elHeader = o.querySelector('.bought-wrapper-mod__head___2vnqo').querySelectorAll('td')
            order.date = elHeader[0].firstChild.textContent
            const elStore = elHeader[1].firstElementChild.querySelector('a')
            order.store = {name: elStore.innerHTML, url: elStore.getAttribute('href')}

            // Items info
            const elItems = [...o.querySelector('tbody:not(.bought-wrapper-mod__head___2vnqo)').children]
            order.items = elItems.map(i =>
            {
                const elChildren = i.children
                const item = {}

                // Item name block
                const elName = [...elChildren[0].firstChild.children[1].children]
                elName.forEach(c =>
                {
                    const reactid = c.getAttribute('data-reactid')

                    // Name & URL block
                    if (reactid.endsWith('.0'))
                    {
                        item.name = c.firstChild.textContent.trim()

                        // Filter link, remove tracking parameters
                        const url = new URL('https:' + c.firstElementChild.getAttribute('href'))
                        for (let key of url.searchParams.keys())
                            if (key !== 'id') url.searchParams.delete(key)

                        item.url = url.toString()
                    }

                    // Selection block
                    if (reactid.endsWith('.1'))
                        item.sel = [...c.children].map(it => [it.firstChild.innerHTML, it.lastChild.innerHTML])

                    // Promises block
                    if (reactid.endsWith('.2'))
                        item.promises = [...c.children].map(it => it.getAttribute('title'))
                })

                // Ignore insurance
                if (item.name === '保险服务') return null

                // Price block
                const elPrice = elChildren[1].firstChild
                item.price = elPrice.lastChild.textContent
                if (elPrice.children.length === 2)
                    item.origPrice = elPrice.firstChild.textContent

                // Quantity block
                item.qty = elChildren[2].textContent

                return item
            }).filter(i => i)

            // Total price
            const elI0 = elItems[0].children
            const elTotalPrice = elI0[4].firstChild
            order.priceTotal = elTotalPrice.firstChild.textContent
            order.priceDelivery = elTotalPrice.children[1].children[1].textContent

            // Status block
            const elStatus = elI0[5].firstChild
            order.status = elStatus.firstChild.textContent

            // Get delivery status
            const req = await fetch(`https://buyertrade.taobao.com/trade/json/transit_step.do?bizOrderId=${order.id}`)
            order.delivery = JSON.parse(GBK.decode(await req.arrayBuffer()))

            return order
        }));
    }

    /**
     * Add CSS https://stackoverflow.com/a/33176845/7346633
     */
    function GM_addStyle(css) {
        const style = document.getElementById("GM_addStyleBy8626") || (function() {
            const style = document.createElement('style');
            style.type = 'text/css';
            style.id = "GM_addStyleBy8626";
            document.head.appendChild(style);
            return style;
        })();
        const sheet = style.sheet;
        sheet.insertRule(css, (sheet.rules || sheet.cssRules || []).length);
    }

    /**
     * Download text string as file
     */
    function download(filename, text)
    {
        const element = document.createElement('a')
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text))
        element.setAttribute('download', filename)

        element.style.display = 'none'
        document.body.appendChild(element)
        element.click()
        document.body.removeChild(element)
    }

    /**
     * Add interactive buttons
     */
    function addBtn()
    {
        console.log('addBtn called')
        let div = document.createElement('div')
        div.innerHTML = `
            <div id="superbuy-inject">
                <button id="btn-fill-items">Superbuy 添加物品</button>
                <button id="btn-fill-delivery">Superbuy 同步运输</button>
                <button id="btn-json-download">下载 JSON</button>
            </div>
        `
        document.body.appendChild(div)

        GM_addStyle(`
        #superbuy-inject
        {
            position: absolute;
            left: 0;
            top: 100px;
            z-index: 1000;
            display: flex;
            flex-direction: column
        }
        `)

        document.getElementById('btn-fill-items').addEventListener('click', async () => {
            let data = await getTaobaoLinks()

        })

        document.getElementById('btn-json-download').addEventListener('click', async () =>
        {
            download('bought_items.json', JSON.stringify(await getTaobaoLinks(), null, 2))
        })
    }

    addBtn()
})();
