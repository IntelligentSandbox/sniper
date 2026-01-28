def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)


print(calculate_average([1, 2, 3, 4, 5]))
