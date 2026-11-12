from schema import InspectResult

CONFIDENCE_THRESHOLD = 0.7


def decide(result: InspectResult):
    scores = [
        result.dimensions.structure.score,
        result.dimensions.surface_wear.score,
        result.dimensions.water_damage.score,
    ]

    # 規則 1：任一項分數是 3 → reject
    if max(scores) == 3:
        return "reject"
    elif result.overall=="reject":
        return "reject"
    elif result.need_retake:
        return "review"
    elif max(scores)==2:
        return "review"
    elif result.confidence<CONFIDENCE_THRESHOLD:
        return "review"
    elif result.overall!="pass":
        return "review"
    else:
        return "pass"