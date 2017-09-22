category = {
    "opportunity": "Opportunity",
    "risk": "Risk",
    "insight": "Insight"
}

status = {
    "initializing": "I",
    "pending": "P",
    "continuous": "C",
    "taken": "T",
    "abort": "A"
}

# TODO: Event Dictionary
# Constants saving TODOs for each event
'''
event_spec = {
    "H2O.leaving": {
        "event_category": category.get("risk"),
        "event_value": "vao",
        "event_desc": [
            "captured_user", "average_value_change_per_user", "expiry_date"
        ],
        "detailed_event_desc": [
            "average_transaction_value_per_user", "average_transaction_quantity_per_user", "most_popular_product"
        ],
        "analysis_desc": [
            "back_test_accuracy", "training_set_customer", "testing_set_customer", "training_set_transaction", "testing_set_transaction"
        ],
        "chart_type": "line",
        "chart": "H2O.leaving"
    }
}
'''
event = {
    "category": category,
    "status": status
}
