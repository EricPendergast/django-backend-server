from project.settings import CONSTANTS


def get_entity_data_metrics(entities):
    if not entities:
        return

    response = []
    for entity in entities:
        if not entity or entity.state < 2:
            break

        response.append(dict(
            entity_type=entity.type,
            labels=entity.data_summary_chart[u'labels'],
            datasets=entity.data_summary_chart[u'datasets'],
            icon=CONSTANTS.ENTITY.ICON_LIST.get(entity.type.upper())
        ))
    return response
