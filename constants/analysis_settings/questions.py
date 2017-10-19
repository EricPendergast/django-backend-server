questions = [
    {
        "label": "revenue",
        "content": "revenue",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "icon": "editor/attachMoney",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.Clv"
    },
    {
        "label": "churn",
        "content": "churn",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "icon": "action/trendingDown",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.Leaving"
    },
    {
        "label": "growth",
        "content": "growth",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "icon": "action/trendingUp",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.Growing"
    },
    {
        "label": "repeat",
        "content": "repeat",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "icon": "av/repeat",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.Repeat"
    },
    {
        "label": "recommendedProduct",
        "content": "recommendedProduct",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "icon": "social/sentimentVerySatisfied",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "H2O.Recommendation"
    }
]
