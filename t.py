def relativeSortArray(arr1, arr2):
    """
    :type arr1: List[int]
    :type arr2: List[int]
    :rtype: List[int]
    """
    for x in arr2:
        print(x)
        arr1.remove(x)

    # arr1 = [3,2,7,2,19], arr2 = [2,1,4,3,9,6]
    print(arr1, arr2)

    sorted_part = []
    new = []
    for i, number in enumerate(arr1):
        new.insert(i, number)
        print(new)
        if number in arr2:
            new.insert(i, number)
        else:
            new.remove(number)
            sorted_part.append(number)

    print(sorted_part)
    new += sorted(sorted_part)
    return new


relativeSortArray([2, 3, 1, 3, 2, 4, 6, 7, 9, 2, 19], [2, 1, 4, 3, 9, 6])
