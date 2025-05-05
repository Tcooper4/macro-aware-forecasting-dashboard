def forecast_hmm(ticker, data, forecast_steps=5):
    import numpy as np
    from hmmlearn.hmm import GaussianHMM
    from utils.common import preprocess_for_model, generate_signal_from_return

    try:
        series = preprocess_for_model(data, ticker, column='Close')
        returns = series.pct_change().dropna().values.reshape(-1, 1)

        if len(returns) < 50:
            return 0.0, "HOLD", 0.0

        model = GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
        model.fit(returns)

        last_state = model.predict(returns)[-1]
        expected_return = model.means_.flatten()[last_state] * forecast_steps * 100
        signal = generate_signal_from_return(expected_return / 100)
        confidence = min(abs(expected_return) / 10, 1)

        print(f"[HMM] Expected return: {expected_return:.4f}, Confidence: {confidence:.2f}, Signal: {signal}")
        return expected_return / 100, signal, confidence

    except Exception as e:
        print(f"[HMM ERROR] {e}")
        return 0.0, "HOLD", 0.0
