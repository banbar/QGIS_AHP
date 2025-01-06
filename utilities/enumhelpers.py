def enum_index_of(enum, enumClass):
    index = 0
    for member in enumClass:
        if enum == member:
            return index
        index += 1
    
    return -1
