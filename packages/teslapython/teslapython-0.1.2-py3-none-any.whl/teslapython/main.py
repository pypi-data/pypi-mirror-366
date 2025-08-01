def teslapython():
    LRV = input("Enter the Lower Range Value (LRV): ")
    URV = input("Enter the Upper Range Value (URV): ")
    X = input("Enter the measured value (X): ")
    LRV = float(LRV)
    URV = float(URV)
    X = float(X)
    if LRV >= URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value")
    if X < LRV or X > URV:
        raise ValueError("Measured value must be within the range defined by LRV and URV")
    if URV - LRV == 0:
        raise ValueError("Upper Range Value must be greater than Lower Range Value to avoid division by zero")
    if X == LRV:
        return 0.0
    if X == URV:
        return 100.0
    if X < LRV or X > URV:
        raise ValueError("Measured value must be within the range defined by LRV and URV")
    # Calculate the percentage of the measured value within the range
    if X < LRV or X > URV:
        raise ValueError("Measured value must be within the range defined by LRV and URV")
    if LRV == URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value to avoid division by zero")
   
    percentage = (X - LRV) / (URV - LRV) * 100

    print ((percentage + 25)/6.25)
    
teslapython()