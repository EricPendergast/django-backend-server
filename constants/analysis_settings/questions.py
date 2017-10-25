questions = [
    {
        "label": "question_01",
        "content": "question_01",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.question_01"
    },
    {
        "label": "question_02",
        "content": "question_02",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.Leaving"
    },
    {
        "label": "question_03",
        "content": "question_03",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.Growing"
    },
    {
        "label": "question_04",
        "content": "question_04",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "required_entities": [
            "transaction"
        ],
        "analysis_engine": "H2O.Repeat"
    },
    {
        "label": "question_05",
        "content": "question_05",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "predictive",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "H2O.Recommendation"
    },
    {
        "label": "question_07",
        "content": "question_07",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "descriptive",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "Question.question_07"
    },
    {
        "label": "question_08",
        "content": "question_08",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "descriptive",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "Question.question_08"
    },
    {
        "label": "question_09",
        "content": "question_09",
        "enabled": False,
        "selected": False,
        "orientation": "customer",
        "type": "descriptive",
        "required_entities": [
            "transaction",
            "customer"
        ],
        "analysis_engine": "Question.question_09"
    },
    # --- Under developing ---
    {"label": "question_10", "content": "question_10", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "customer", "analysis_engine": "Question.question_10"},
    {"label": "question_11", "content": "question_11", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "customer", "analysis_engine": "Question.question_11"},
    {"label": "question_12", "content": "question_12", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_12"},
    {"label": "question_13", "content": "question_13", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_13"},
    {"label": "question_14", "content": "question_14", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_14"},
    {"label": "question_15", "content": "question_15", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_15"},
    {"label": "question_16", "content": "question_16", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_16"},
    {"label": "question_17", "content": "question_17", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_17"},
    {"label": "question_18", "content": "question_18", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_18"},
    {"label": "question_19", "content": "question_19", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_19"},
    {"label": "question_20", "content": "question_20", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_20"},
    {"label": "question_21", "content": "question_21", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_21"},
    {"label": "question_22", "content": "question_22", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_22"},
    {"label": "question_23", "content": "question_23", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_23"},
    {"label": "question_24", "content": "question_24", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_24"},
    {"label": "question_25", "content": "question_25", "enabled": False, "selected": False,
     "required_entities": ["transaction", "customer", "campaign", "conversion"], "type": "descriptive",
     "orientation": "sales", "analysis_engine": "Question.question_25"},
    {"label": "question_26", "content": "question_26", "enabled": False, "selected": False, "required_entities": [],
     "type": "predictive", "orientation": "product", "analysis_engine": "Recommendation.question_26"},
    {"label": "question_27", "content": "question_27", "enabled": False, "selected": False, "required_entities": [],
     "type": "predictive", "orientation": "product", "analysis_engine": "Recommendation.question_27"},
    {"label": "question_28", "content": "question_28", "enabled": False, "selected": False, "required_entities": [],
     "type": "predictive", "orientation": "product", "analysis_engine": "Recommendation.question_28"},
    {"label": "question_31", "content": "question_31", "enabled": False, "selected": False, "required_entities": [],
     "type": "descriptive", "orientation": "product", "analysis_engine": "ContinuousMonitoring.question_31"},
    {"label": "question_32", "content": "question_32", "enabled": False, "selected": False, "required_entities": [],
     "type": "descriptive", "orientation": "product", "analysis_engine": "ContinuousMonitoring.question_32"},
    {"label": "question_34", "content": "question_34", "enabled": False, "selected": False, "required_entities": [],
     "type": "descriptive", "orientation": "product", "analysis_engine": "ContinuousMonitoring.question_34"},
    {"label": "question_35", "content": "question_35", "enabled": False, "selected": False, "required_entities": [],
     "type": "descriptive", "orientation": "pricing", "analysis_engine": "ContinuousMonitoring.question_35"},
    {"label": "question_36", "content": "question_36", "enabled": False, "selected": False, "required_entities": [],
     "type": "descriptive", "orientation": "pricing", "analysis_engine": "ContinuousMonitoring.question_36"},
    # --- Under developing ---
    {
        "label": "question_37",
        "content": "question_37",
        "enabled": True,
        "selected": False,
        "orientation": "pricing",
        "type": "descriptive",
        "required_entities": [],
        "analysis_engine": "ContinuousMonitoring.question_37"
    }
]
