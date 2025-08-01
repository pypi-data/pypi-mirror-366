import inspect

# ===================== 📦 ML and Visualization Programs ===================== #

def program1():
    import numpy as np
    from scipy.stats import hmean

    # Values and weights
    values = np.array([4, 5, 8, 7])
    weights = np.array([2, 3, 1, 4])

    # Geometric Mean
    geo_mean = np.prod(values) ** (1 / len(values))

    # Harmonic Mean
    harm_mean = hmean(values)

    # Weighted Mean
    weighted_mean = np.average(values, weights=weights)

    # Display results
    print(f"Geometric Mean: {geo_mean:.2f}")
    print(f"Harmonic Mean: {harm_mean:.2f}")
    print(f"Weighted Mean: {weighted_mean:.2f}")




def program2():
    import numpy as np

    # Dataset
    data = np.array([5, 7, 8, 6, 9, 6, 7, 8, 5, 6])

    # Range
    data_range = max(data) - min(data)

    # Mean
    mean = np.mean(data)

    # Mean Deviation
    mean_deviation = np.mean(np.abs(data - mean))

    # Variance
    variance = np.var(data)

    # Standard Deviation
    std_dev = np.std(data)

    # Output results
    print(f"Range: {data_range}")
    print(f"Mean: {mean:.2f}")
    print(f"Mean Deviation: {mean_deviation:.2f}")
    print(f"Variance: {variance:.2f}")
    print(f"Standard Deviation: {std_dev:.2f}")



def program3():
    import numpy as np

    # Group data
    group1 = np.array([5, 6, 7, 5, 6])
    group2 = np.array([8, 9, 10, 9, 11])
    n1 = len(group1)
    n2 = len(group2)

    # Means
    mean1 = np.mean(group1)
    mean2 = np.mean(group2)

    # Variances
    var1 = np.var(group1)
    var2 = np.var(group2)

    # Combined Mean
    mean_combined = (n1 * mean1 + n2 * mean2) / (n1 + n2)

    # Combined Variance
    var_combined = ((n1 * (var1 + (mean1 - mean_combined) ** 2)) +
                    (n2 * (var2 + (mean2 - mean_combined) ** 2))) / (n1 + n2)

    # Combined Standard Deviation
    std_combined = np.sqrt(var_combined)

    # Output
    print(f"Mean1: {mean1:.2f}, Mean2: {mean2:.2f}")
    print(f"Combined Mean: {mean_combined:.2f}")
    print(f"Combined Variance: {var_combined:.2f}")
    print(f"Combined Std Dev: {std_combined:.2f}")



def program4():
    import numpy as np
    from scipy.stats import pearsonr, spearmanr

    # Sample data
    x = np.array([40, 50, 60, 70, 80])
    y = np.array([45, 60, 65, 80, 90])

    # Pearson Correlation
    pearson_corr, _ = pearsonr(x, y)

    # Spearman Correlation
    spearman_corr, _ = spearmanr(x, y)

    # Output
    print(f"Pearson Correlation: {pearson_corr:.2f}")
    print(f"Spearman Correlation: {spearman_corr:.2f}")



def program5():
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression

    # Data
    X = np.array([2, 3, 4, 5, 6]).reshape(-1, 1)
    Y = np.array([40, 50, 65, 70, 85])

    # Model
    model = LinearRegression()
    model.fit(X, Y)

    # Coefficients
    a = model.intercept_
    b = model.coef_[0]

    # Prediction for X = 7
    predicted = model.predict(np.array([[7]]))

    # Output
    print(f"Regression Equation: Y = {a:.2f} + {b:.2f}X")
    print(f"Predicted Y for X=7: {predicted[0]:.2f}")

    # Plot
    plt.scatter(X, Y, color='blue', label='Data Points')
    plt.plot(X, model.predict(X), color='red', label='Regression Line')
    plt.title("Linear Regression Line")
    plt.xlabel("Study Hours")
    plt.ylabel("Marks")
    plt.legend()
    plt.grid(True)
    plt.show()


# ===================== 🔍 Source Code Introspection Functions ===================== #

def print_program1(): print(inspect.getsource(program1))
def print_program2(): print(inspect.getsource(program2))
def print_program3(): print(inspect.getsource(program3))
def print_program4(): print(inspect.getsource(program4))
def print_program5(): print(inspect.getsource(program5))

