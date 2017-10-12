from event import CATEGORY
STATUS = dict(
    INITIALIZING="I",
    PENDING="P",
    CONTINUOUS="C",
    UPDATING="UG",
    UPDATED="UD",
    FAILED="F",
)

# TODO: Event Dictionary
# Constants saving TODOs for each event


EVENT_SPEC = {
    "H2O.Clv": {
        "event_category": CATEGORY.get('INSIGHT'),
        "event_type": STATUS.get('PENDING'),
        "event_value": "vao",
        "event_desc": [
            "captured_user", "average_value_change_per_user", "expiry_date"
        ],
        "detailed_event_desc": [
            "average_transaction_value_per_user", "average_transaction_quantity_per_user", "most_popular_product"
        ],
        "analysis_desc": [
            "back_test_accuracy", "training_set_customer", "testing_set_customer", "training_set_transaction",
            "testing_set_transaction"
        ],
        "chart_type": "Line",
        "chart": "H2O.Clv"
    },

    "Monitoring.Reseller_Price_Range": {
        "event_category": CATEGORY.get('INSIGHT'),
        "event_type": STATUS.get('CONTINUOUS'),
        "event_value": "distinct_products",
        "event_desc": [
            "captured_user", "captured_competitor", "best_performing_competitor", "expiry_date"
        ],
        "detailed_event_desc": [
            "average_product_prize"
        ],
        "analysis_desc": [
            "data_processing_time", "captured_product_data"
        ],
        "chart_type": "MultiTables",
        "chart": "Monitoring.Reseller_Price_Range"
    }
}
