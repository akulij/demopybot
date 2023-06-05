from modules.dialogs import config

from .tools import get_faqs, get_info_faqs


reply_keyboards = {
        "main": [
            config.ihavequestion,
            config.wheretobuy,
            config.support,
            ]
        }

inline_keyboards = {
        "faq_main": get_faqs,
        "faq_info": get_info_faqs,
        "links": [
            {
                "type": "link",
                "title": "ЭкосГум",
                "link": "www.ecosgum.ru",
                },
            {
                "type": "link",
                "title": "Экос",
                "link": "www.pribavka-ecos.ru",
                },
            {
                "type": "link",
                "title": "Озон",
                "link": "https://www.ozon.ru/seller/pribavka-212052/products/?miniapp=seller_212052",
                },
            ]
        }
