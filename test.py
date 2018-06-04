def realOp(aa):
    return aa

def opNumber(startNum):
    print("执行第%d次" % (startNum + 1))
    return realOp(startNum)

lastStartIndex = 0
for i in range(100):
    lastStartIndex = opNumber(lastStartIndex)
