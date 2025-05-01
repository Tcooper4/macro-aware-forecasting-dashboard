def ensemble_vote(predictions, confidences):
    vote_score = sum(1 if p == 1 else -1 for p in predictions)
    confidence_score = sum(confidences) / len(confidences)
    if vote_score > 0:
        return "BUY", confidence_score
    elif vote_score < 0:
        return "SELL", 1 - confidence_score
    else:
        return "HOLD", 0.5
