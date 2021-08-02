def prediction(stock, no_of_days):
    from datetime import date, timedelta
    import yfinance as yf
    import plotly.graph_objs as go

    from model import prediction
    from sklearn.model_selection import train_test_split, GridSearchCV
    from sklearn.svm import SVR

    # load the data
    df = yf.download(stock, period='500d')
    df.reset_index(inplace=True)
    df['Day'] = df.index

    days = list()
    for i in range(len(df.Day)):
        days.append([i])

    # Splitting the dataset(9:1)

    X = days
    Y = df[['Close']]

    x_train, x_test, y_train, y_test = train_test_split(X,Y,test_size=0.1,shuffle=False)

    gsc = GridSearchCV(
        estimator=SVR(kernel='rbf'),
        param_grid={
            'C': [0.001, 0.01, 0.1, 1, 100, 1000],
            'epsilon': [
                0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10,
                50, 100, 150, 1000
            ],
            'gamma': [0.0001, 0.001, 0.005, 0.1, 1, 3, 5, 8, 40, 100, 1000]
        },
        cv=5,
        scoring='neg_mean_absolute_error',
        verbose=0,
        n_jobs=-1)

    y_train = y_train.values.ravel()
    y_train
    grid_result = gsc.fit(x_train, y_train)
    best_params = grid_result.best_params_
    rbf_svr = SVR(kernel='rbf',C=best_params["C"],epsilon=best_params["epsilon"],gamma=best_params["gamma"],max_iter=-1)

    # Support Vector Regression Models

    # RBF model
    #rbf_svr = SVR(kernel='rbf', C=1000.0, gamma=4.0)

    rbf_svr.fit(x_train, y_train)

    predicted_prices = list()
    for i in range(1, no_of_days):
        predicted_prices.append([i + x_test[-1][0]])

    predicted_days = []
    current = date.today()
    for i in range(no_of_days):
        current += timedelta(days=1)
        predicted_days.append(current)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=predicted_days,y=rbf_svr.predict(predicted_prices),mode='lines+markers',name='data'))
    fig.update_layout(title="Forecasted Close Price for the next " + str(no_of_days - 1) + " days",xaxis_title="Date",yaxis_title="Close Price")

    return fig
