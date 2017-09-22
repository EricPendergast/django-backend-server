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
        "choices": [
            {
                "content": "Default. Handled by Eledata"
            },
            {
                "content": "Enter your value:",
                "default_value": "50,000"
            }
        ],
        "label": "income",
        "content": "What is your company's average monthly income?",
        "floating_label": "Income",
        "required_question_labels": ["repeat", "recommendedProduct", "churn", "growth", "revenue"]
    },
    {
        "choices": [
            {
                "content": "Default. Handled by EleData"
            },
            {
                "content": "My expected prediction window (in month) would be: ",
                "default_value": "3"
            }
        ],
        "label": "prediction_window",
        "content": "What is your expected prediction window among your predictive questions ?",
        "floating_label": "Prediction Window",
        "required_question_labels": ["repeat", "recommendedProduct", "churn", "growth", "revenue"]
    }
]
