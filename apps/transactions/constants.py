from django.utils.translation import gettext_lazy as _

NORMAL_USER_LIMITS = {
    "max_custom_category_count": 5,
    "max_wallets_count": 2,
}
PREMIUM_USER = {
    "transaction_count": 100,
    "transaction_streak": 30,
}
HOME_PAGE_STATS = {
    "num_recent_transactions": 5,
    "num_top_spending": 3,
    "max_floating_points": 3,
    "default_tab": "month",
}

DEFAULT_BANKS = [
    {
        "name": _("Vietcombank"),
        "code": "VCB",
    },
    {
        "name": _("MB Bank"),
        "code": "MB",
    },
    {
        "name": _("BIDV"),
        "code": "BIDV",
    },
    {
        "name": _("Agribank"),
        "code": "AGB",
    },
    {
        "name": _("Sacombank"),
        "code": "STB",
    },
    {
        "name": _("SCB"),
        "code": "SCB",
    },
    {
        "name": _("HSBC"),
        "code": "HSBC",
    },
    {
        "name": _("Vietinbank"),
        "code": "VTB",
    },
    {
        "name": _("HD Bank"),
        "code": "HDB",
    },
]
