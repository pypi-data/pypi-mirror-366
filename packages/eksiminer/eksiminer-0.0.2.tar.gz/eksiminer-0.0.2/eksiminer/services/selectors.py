SELECTORS = {
    "website": "https://eksisozluk.com",
    "debe_website": "https://eksisozluk.com/debe",
    "gundem": {
        "container": "ul.topic-list.partial li a",
        "wait_for_class": "topic-list",
    },
    "search": {
        "input": "search-textbox",
        "button": "button[aria-label='getir']",
    },
    "entry": {
        "total_page":  "a.last",
        "container": "ul#entry-item-list > li",
        "content": "div.content",
        "author": "a.entry-author",
        "date": "a.entry-date.permalink",
    },
    "debe": {
        "wait_for_class": "ul.topic-list.partial",
        "container": "ul.topic-list.partial li a",
    },
    "author": {
        "wait_for_class": "topic-item",
        "load_more": "a.load-more-entries",
        "topic": "div.topic-item",
        "title": "h1#title",
        "content": "div.content",
        "date": "a.entry-date",
    },
    "entry_from_url": {
        "content": "div.content.content-expanded",
        "author": "a.entry-author",
        "date": "a.entry-date",
        "title": "h1#title",
    }
}
