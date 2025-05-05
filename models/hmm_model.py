def forecast_hmm(ticker, data, forecast_steps=5):
    import numpy as np
    from hmmlearn.hmm import GaussianHMM
    from utils.common import preprocess_for_model, generate_signal_from_return

    try:
        series = preprocess_for_model(data, ticker, column='Close')
        returns = series.pct_change().dropna().values.reshape(-1, 1)

        if len(returns) < 50:
            print(f"⚠️ Not enough data to fit HMM for {ticker}.")
            return 0.0, "HOLD", 0.0

        model = GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
        model.fit(returns)

        last_state = model.predict(returns)[-1]
        next_means = model.means_.flatten()
        expected_return = next_means[last_state] * forecast_steps
        signal = generate_signal_from_return(expected_return)
        confidence = abs(expected_return)

        print(f"✅ HMM signal for {ticker}: {signal} (Predicted return: {expected_return:.4f})")
        return expected_return, signal, confidence

    except Exception as e:
        print(f"❌ HMM failed for {ticker}: {e}")
        return 0.0, "HOLD", 0.0
