def teslapython_1():
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
    if LRV == URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value to avoid division by zero")
   
    percentage = (X - LRV) / (URV - LRV) * 100

    print ((percentage + 25)/6.25)
    
#teslapython_1()

def teslapython_2():
    LRV = input("Enter the Lower Range Value (LRV): ")
    URV = input("Enter the Upper Range Value (URV): ")
    Y = input("Enter the 4-20mA signal (Y): ")
    LRV = float(LRV)
    URV = float(URV)
    Y = float(Y)
    if LRV >= URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value")
    if Y < 4 or Y > 20:
        raise ValueError("Measured value must be within the range defined by 4 and 20")
    if URV - LRV == 0:
        raise ValueError("Upper Range Value must be greater than Lower Range Value to avoid division by zero")
    if Y == 4:
        return 0.0
    if Y == 20:
        return 100.0
    if LRV == URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value to avoid division by zero")

    percentage = (Y*6.25)-25

    PV = (percentage * (URV - LRV) / 100) + LRV

    print(PV)

#teslapython_2()

def teslapython_3():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import sys
    print(sys.path)

    img = mpimg.imread('teslapython/pic1.png')
    imgplot = plt.imshow(img)
    plt.show()

def teslapython():
    while True:
        print("Welcome to the TeslaPython Conversion!")
        print("1. Process variable to 4-20mA conversion")
        print("2. 4-20mA to process variable conversion")
        print("3. Difference between PNP and NPN sensors")
        print("4. Exit")

        choice = input("Enter your choice (1, 2, 3, or 4): ")

        if choice == '1':
            teslapython_1()
        elif choice == '2':
            teslapython_2()
        elif choice == '3':
            teslapython_3()
        elif choice == '4':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    teslapython()