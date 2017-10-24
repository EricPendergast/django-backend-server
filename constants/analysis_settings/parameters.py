parameters = [
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
        "required_question_labels": ["question_01", "question_02", "question_03", "question_04", "question_05"]
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
        "required_question_labels": ["question_01", "question_02", "question_03", "question_04", "question_05"]
    },
    {
        # What is your definition of Churners?
        "choices": [
            {
                # Users with no sales for __ months
                "content": 'no_sale',
                "default_value": '3'
            }
        ],
        "label": "churner_definition",
        "content": "churner_definition",
        "floating_label": "churner_definition",
        "required_question_labels": ["question_02", "question_07"]
    },
    {
        # What is your definition of Growthers?
        "choices": [
            {
                # In the past 6 months, users with increase of purchase quantity of _ %
                "content": 'increase_purchase',
                "default_value": '5'
            }
        ],
        "label": "growthers_definition",
        "content": "growthers_definition",
        "floating_label": "growthers_definition",
        "required_question_labels": ["question_03", "question_08"]
    },
    {
        # What is your definition of Repeaters?
        "choices": [
            {
                # Users in the past year that purchased more than __ times
                "content": 'past_year_purchase',
                "default_value": '10'
            }
        ],
        "label": "repeaters_definition",
        "content": "repeaters_definition",
        "floating_label": "repeaters_definition",
        "required_question_labels": ["question_04", "question_09"]
    }
]
