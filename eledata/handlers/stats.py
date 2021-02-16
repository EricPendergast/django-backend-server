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
    :param pending_events: Queryset, list of ordered pending events
    :return: dictionary, Summary of pending events
    """
    # Initialize variables and count for all pending
    # TODO: Aggregate to group the event_id
    # pipeline = [
    #     {
    #         "$group": {
    #             "_id": {
    #                 "event_id": "$event_id",
    #             },
    #             "first": {"$first": "$$ROOT"},
    #         }
    #     }
    # ]
    pending_opportunity = 0
    pending_risk = 0
    pending_count = len(pending_events)
    pending_last_update = pending_events[0][u'updated_at'].strftime("%Y-%m-%d") if pending_events else "--"

    for event in pending_events:
        if event[u'event_type'] == CONSTANTS.EVENT.CATEGORY.get('OPPORTUNITY'):
            pending_opportunity += float(event[u'event_value'].items()[0])
        elif event[u'event_type'] == CONSTANTS.EVENT.CATEGORY.get('RISK'):
            pending_risk += float(event[u'event_value'].items()[0])

    return dict(pending_vao="{:,.2f}".format(pending_opportunity),
                pending_var="{:,.2f}".format(pending_risk),
                pending_insights=pending_count,
                last_updated=pending_last_update,
                )
