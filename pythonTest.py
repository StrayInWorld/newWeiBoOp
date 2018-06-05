def op_number(i, a):
    if i == 1:
        return a + 10
    else:
        return




last_start_index = 0
for i in range(6):
    last_start_index = op_number(i, last_start_index)
    print(last_start_index)
