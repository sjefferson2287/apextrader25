import numpy as np

def binomial_tree_option_price(S, K, T, r, sigma, N, option_type="call", american=False):
    """
    Computes the price of an option using the Binomial Tree Model.
    
    Parameters:
    S (float): Initial stock price
    K (float): Strike price
    T (float): Time to maturity (years)
    r (float): Risk-free interest rate (decimal)
    sigma (float): Volatility of the underlying asset (decimal)
    N (int): Number of time steps in the binomial model
    option_type (str): "call" for call option, "put" for put option
    american (bool): If True, computes price for an American option
    
    Returns:
    float: Option price
    """
    dt = T / N  # Time step size
    u = np.exp(sigma * np.sqrt(dt))  # Up factor
    d = 1 / u  # Down factor (ensures risk neutrality)
    p = (np.exp(r * dt) - d) / (u - d)  # Risk-neutral probability
    
    # Step 1: Compute the terminal node values (option payoffs at expiration)
    stock_prices = np.array([S * (u ** j) * (d ** (N - j)) for j in range(N + 1)])
    
    if option_type == "call":
        option_values = np.maximum(stock_prices - K, 0)  # Call option payoff
    else:
        option_values = np.maximum(K - stock_prices, 0)  # Put option payoff
    
    # Step 2: Backpropagate the values to determine the option price today
    for i in range(N - 1, -1, -1):
        option_values = np.exp(-r * dt) * (p * option_values[1:] + (1 - p) * option_values[:-1])
        
        # If American option, check for early exercise
        if american:
            stock_prices = np.array([S * (u ** j) * (d ** (i - j)) for j in range(i + 1)])
            if option_type == "call":
                option_values = np.maximum(option_values, np.maximum(stock_prices - K, 0))
            else:
                option_values = np.maximum(option_values, np.maximum(K - stock_prices, 0))
    
    return option_values[0]

# Example Usage
S = 100    # Stock price
K = 105    # Strike price
T = 1      # Time to expiration (1 year)
r = 0.05   # Risk-free rate (5%)
sigma = 0.2  # Volatility (20%)
N = 3      # Number of time steps

# Compute European call option price
call_price = binomial_tree_option_price(S, K, T, r, sigma, N, option_type="call", american=False)
print(f"European Call Option Price: {call_price:.4f}")

# Compute American call option price
american_call_price = binomial_tree_option_price(S, K, T, r, sigma, N, option_type="call", american=True)
print(f"American Call Option Price: {american_call_price:.4f}")

# Compute European put option price
put_price = binomial_tree_option_price(S, K, T, r, sigma, N, option_type="put", american=False)
print(f"European Put Option Price: {put_price:.4f}")

# Compute American put option price
american_put_price = binomial_tree_option_price(S, K, T, r, sigma, N, option_type="put", american=True)
print(f"American Put Option Price: {american_put_price:.4f}")

