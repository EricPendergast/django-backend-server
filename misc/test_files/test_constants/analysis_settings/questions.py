questions = [
    {
        "content": "Which customers will likely be leaving in the coming time?",
        "enabled": False,
        "label": "leaving",
        "orientation": "customer",
        "selected": False,
        "type": "predictive",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "H2O.question_01"
    },
    {
        "content": "Which products will be the most popular in the future?",
        "enabled": False,
        "label": "popularity",
        "orientation": "product",
        "selected": False,
        "type": "predictive",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.Question03Engine"
    },
    {
        "content": "What has caused the most customers to leave?",
        "enabled": False,
        "label": "cause of leave",
        "orientation": "hiddenInsight",
        "selected": False,
        "type": "descriptive",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "H2O.question_01"
    }
]
