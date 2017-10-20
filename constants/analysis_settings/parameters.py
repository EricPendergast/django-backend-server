parameters = [
    {
        "choices": [
            {
                "content": "Default. Handled by Eledata"
            }
        ],
        "label": "clv",
        "content": "What is your expected variation of CLV?",
        "floating_label": "Variation",
        "required_question_labels": ["leaving"]
    },
    {
        # What is your accepted range of correct prediction
        "choices": [
            {
                "content": "defaultChoice"
            },
            {
                "content": "ratio",
                "default_value": "0.1"
            },
            {
                "content": "distribution"
            },
        ],
        "label": "allowance",
        "content": "allowance",
        "floating_label": "allowance",
        "required_question_labels": ["repeat", "recommendedProduct", "churn", "growth", "revenue"]
    },
    {
        # What is your expected prediction window among your predictive questions ?
        "choices": [
            {
                "content": "defaultChoice"
            },
            {
                "content": 'monthly'
            },
            {
                "content": 'quarterly'
            },
            {
                "content": 'yearly',
            },
            {
                "content": "expectedTimeWindow",
                "default_value": "3"
            }
        ],
        "label": "prediction_window",
        "content": "prediction_window",
        "floating_label": "prediction_window",
        "required_question_labels": ["repeat", "recommendedProduct", "churn", "growth", "revenue"]
    },
    {
        # What is your definition of Churners?
        "choices": [
            {
                "content": "defaultChoice"
            },
            {
                # Users with no sales for __ months
                "content": 'no_sale',
                "default_value": '3'
            }
        ],
        "label": "churner_definition",
        "content": "churner_definition",
        "floating_label": "churner_definition",
        "required_question_labels": ["question_07"]
    },
    {
        # What is your definition of Growthers?
        "choices": [
            {
                "content": "defaultChoice"
            },
            {
                # Users with 6 months of increase of purchase amount in
                "content": 'increase_purchase',
                "default_value": '5'
            }
        ],
        "label": "growthers_definition",
        "content": "growthers_definition",
        "floating_label": "growthers_definition",
        "required_question_labels": ["question_08"]
    },
    {
        # What is your definition of Repeaters?
        "choices": [
            {
                "content": "defaultChoice"
            },
            {
                # Users in the past year that purchased more than __ times
                "content": 'past_year_purchase',
                "default_value": '10'
            }
        ],
        "label": "repeaters_definition",
        "content": "repeaters_definition",
        "floating_label": "repeaters_definition",
        "required_question_labels": ["question_09"]
    }
]
