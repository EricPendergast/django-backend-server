questions = [
    {
        "label": "revenue",
        "content": "What are the revenue contributed by my customers in the coming time?",
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
        "content": "Customers who are predicted to be not buying anymore in the coming time?",
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
        "content": "Customers who are predicted to be buying more in the coming time?",
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
        "content": "Customer who are predicted to be buying repeatedly in the coming time",
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
        "content": "What are the products that should be recommended to my customers?",
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
