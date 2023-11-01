from modules.dialogs import config

from .tools import (
        get_bots_ikbd,
        )


reply_keyboards = {
        "main": [
            config.bots,
            config.tarifs,
            config.boost,
            config.info,
            config.account,
            config.support,
            ]
        }

inline_keyboards = {
        "botscfg": get_bots_ikbd,
        "telegraph_links": [
            {
                "type": "link",
                "title": "Ссылка 1",
                "link": "google.com",
                },
            {
                "type": "link",
                "title": "Ссылка 2",
                "link": "yandex.ru",
                },
            ]
        }
