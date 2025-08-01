def logic_predict(seq):

    n = len(seq)
    # Sequences with less than 4 elements are difficult to predict reliably
    if n < 4:
        return "Unknown: Sequence too short"

    # Check for arithmetic progression
    is_arithmetic = True
    # Calculate the common difference
    diff = seq[1] - seq[0]
    for i in range(1, n - 1):
        # Check if the difference between consecutive terms is constant
        if seq[i+1] - seq[i] != diff:
            is_arithmetic = False
            break
    if is_arithmetic:
        # If it's an arithmetic sequence, the next number is the last term plus the common difference
        return seq[-1] + diff

    # Check for geometric progression
    is_geometric = True
    # Avoid division by zero when calculating the ratio
    if all(x != 0 for x in seq[:-1]):
        # Calculate the common ratio
        ratio = seq[1] / seq[0]
        for i in range(1, n - 1):
            # Use a small tolerance for floating point comparisons to account for potential precision issues
            if abs(seq[i+1] / seq[i] - ratio) > 1e-9:
                is_geometric = False
                break
        if is_geometric:
            # If it's a geometric sequence, the next number is the last term multiplied by the common ratio
            return seq[-1] * ratio
    else:
        is_geometric = False # If any term is zero, it cannot be a standard geometric progression


    # Check for quadratic sequence (assuming the sequence is long enough)
    if n >= 5:
        # Calculate the differences between consecutive terms (first differences)
        diff1 = [seq[i+1] - seq[i] for i in range(n-1)]
        # Calculate the differences between those differences (second differences)
        diff2 = [diff1[i+1] - diff1[i] for i in range(len(diff1)-1)]

        # Check if the second differences are constant (within a tolerance for floating point numbers)
        is_quadratic = True
        if len(diff2) > 0:
            const_diff2 = diff2[0]
            for i in range(1, len(diff2)):
                if abs(diff2[i] - const_diff2) > 1e-9:
                    is_quadratic = False
                    break
            if is_quadratic:
                # If it's a quadratic sequence, the next second difference is the same as the constant second difference.
                # The next first difference is the last first difference plus the constant second difference.
                # The next number in the sequence is the last term plus the next first difference.
                next_diff1 = diff1[-1] + const_diff2
                return seq[-1] + next_diff1
        else:
            is_quadratic = False # Not enough second differences to check for a constant value


    # Check for Fibonacci-like sequence
    is_fibonacci_like = True
    if n >= 3:
        for i in range(n - 2):
            # Check if each term is the sum of the two preceding terms
            if seq[i+2] != seq[i+1] + seq[i]:
                is_fibonacci_like = False
                break
        if is_fibonacci_like:
            # If it's a Fibonacci-like sequence, the next number is the sum of the last two terms
            return seq[-1] + seq[-2]


    # Check for repeating sequence
    if n >= 2:
        # Iterate through possible pattern lengths
        for pattern_len in range(1, n // 2 + 1):
            is_repeating = True
            # Extract the potential pattern
            pattern = seq[:pattern_len]
            # Check if the rest of the sequence repeats this pattern
            for i in range(pattern_len, n):
                if seq[i] != pattern[i % pattern_len]:
                    is_repeating = False
                    break
            if is_repeating:
                # If a repeating pattern is found, the next number is the next element in the pattern
                return pattern[n % pattern_len]

    # If none of the above patterns are found
    return "Unknown: No recognized pattern"
test_seq = [2, 3, 5, 8, 12, 17]
prediction = logic_predict(test_seq)
print(f"Sequence: {test_seq}, Predicted next number: {prediction}")
def symbol_predict_and_encode(seq, logic_predict_func):
    """
    Converts a symbolic sequence into a list of integers, predicts the next
    symbol using a provided logic_predict_func, and returns the predicted symbol.

    Args:
        seq (list): A list of symbols (e.g., ['A', 'B', 'A']).
        logic_predict_func (function): A function that takes an encoded sequence
                                      (list of integers) and returns the predicted
                                      next encoded value.

    Returns:
        str: The predicted next symbol, or "Unknown" if the prediction
             cannot be reversed to a symbol.
    """
    mapping = {}
    reverse = {}
    encoded = []
    current = 1
    for symbol in seq:
        if symbol not in mapping:
            mapping[symbol] = current
            reverse[current] = symbol
            current += 1
        encoded.append(mapping[symbol])

    next_encoded = logic_predict_func(encoded)

    if isinstance(next_encoded, (int, float)) and int(next_encoded) in reverse:
        return reverse[int(next_encoded)]
    else:
        return "Unknown"