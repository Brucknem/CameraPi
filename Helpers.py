def bitfield(n, length):
    field = [1 if digit == '1' else 0 for digit in bin(n)[2:]]

    while len(field) < length:
        field.insert(0, 0)

    while len(field) > length:
        field.remove(0)

    return field