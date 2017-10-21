from project.settings import CONSTANTS


def get_entity_data_metrics(entities):
    if not entities:
        return

    response = []
    for entity in entities:
        if not entity:
            break

        response.append(dict(
            entity_type=entity.type,
            labels=entity.data_summary_chart[u'labels'],
            datasets=entity.data_summary_chart[u'datasets'],
            icon=CONSTANTS.ENTITY.ICON_LIST.get(entity.type.upper())
        ))
    return response


def get_event_dashboard_summary(pending_events):
    """
    Get event dashboard summary from all pending events
    :param pending_events: Queryset, list of pending events
    :return: dictionary, Summary of pending events
    """
    for event in pending_events:
        # TODO: 1. identify different event cat, 2. sum for risk and opportunity, 3. count for all, 4. get last update time
        print(event[u'event_type'])
    return
