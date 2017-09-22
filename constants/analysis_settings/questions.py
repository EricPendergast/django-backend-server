questions = [
    {
        "content": "Which customers will likely be leaving in the coming time?",
        "enabled": False,
        "label": "leaving",
        "icon": "maps/directionsRun",
        "orientation": "customer",
        "selected": False,
        "type": "predictive",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "H2O.leaving"
    },
    {
        "content": "Which products will be the most popular in the future?",
        "enabled": False,
        "label": "popularity",
        "icon": "action/trendingUp",
        "orientation": "product",
        "selected": False,
        "type": "predictive",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.popularity"
    },
    {
        "content": "What has caused the most customers to leave?",
        "enabled": False,
        "label": "cause of leave",
        "icon": "maps/directionsRun",
        "orientation": "hiddenInsight",
        "selected": False,
        "type": "descriptive",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "EventStats.leaving"
    }
]
