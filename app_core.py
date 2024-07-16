import random

from exceptions import RangeException
from basic_module import ensureInstanceOfType, findNum

def generateSingleGroupNumbers(rangeMin, rangeMax, total, ignoreNums,
                               chosenNums=None):
    if not isinstance(rangeMin, int):
        raise ValueError("数值错误：范围最小值不是整数。")
    elif not isinstance(rangeMax, int):
        raise ValueError("数值错误：范围最大值不是整数。")
    elif not isinstance(total, int):
        raise ValueError("数值错误：随机数个数不是整数。")
    elif not isinstance(ignoreNums, (list, tuple)):
        raise TypeError("The ignore nums list isn't a list or a tuple.")
    if rangeMin > rangeMax:
        raise RangeException("范围错误：范围最小值大于范围最大值。")
    elif total <= 0:
        raise RangeException("范围错误：随机数个数为非正整数。")
    elif total > rangeMax - rangeMin + 1:
        raise RangeException("范围错误：随机数个数大于范围。")
    if chosenNums is not None:
        chosenNums = ensureInstanceOfType(chosenNums, list, default=[])
    else:
        chosenNums = []
    resultList = []
    count = 0
    if ignoreNums:
        ignoreNumsLeftIndex = findNum(ignoreNums, rangeMin)
        if ignoreNumsLeftIndex is None:
            ignoreNumsLeftIndex = 0
        # Including right range.
        ignoreNumsRightIndex = findNum(ignoreNums, rangeMax)
        if ignoreNumsRightIndex is None:
            ignoreNumsRightIndex = -1
        ignoreNumsCount = ignoreNumsRightIndex - ignoreNumsLeftIndex + 1
    else:
        ignoreNumsCount = 0
    chosenNumsCount = len(chosenNums)
    rangeWidth = (rangeMax - rangeMin + 1)
    while count < total:
        num = random.randint(rangeMin, rangeMax)
        if num in resultList:
            continue
        if num in ignoreNums:
            if ignoreNumsCount >= rangeWidth - total:
                raise Exception
            while num in ignoreNums:
                num = random.randint(rangeMin, rangeMax)
        resultList.append(num)
        if num not in chosenNums:
            chosenNums.append(num)
        count += 1
        if chosenNumsCount >= rangeWidth:
            chosenNums.clear()
            chosenNumsCount = len(chosenNums)
    return resultList

def generateWithHigherLevelNumbers(rangeMin, rangeMax, total, ignoreNums,
                                   higherLevelNums=None, chosenNums=None):
    if not isinstance(rangeMin, int):
        raise ValueError("数值错误：范围最小值不是整数。")
    elif not isinstance(rangeMax, int):
        raise ValueError("数值错误：范围最大值不是整数。")
    elif not isinstance(total, int):
        raise ValueError("数值错误：随机数个数不是整数。")
    elif not isinstance(ignoreNums, (list, tuple)):
        raise TypeError("The ignore nums list isn't a list or a tuple.")
    if higherLevelNums is not None:
        higherLevelNums = ensureInstanceOfType(higherLevelNums, list, [])
    else:
        higherLevelNums = []
    ignoreNums = list(ignoreNums)
    higherLevelNums = list(filter(lambda num: num not in ignoreNums,
                                  sorted(higherLevelNums)))
    leftIndex = findNum(higherLevelNums, rangeMin)
    if leftIndex is None:
        leftIndex = 0
    rightIndex = findNum(higherLevelNums, rangeMax)
    if rightIndex is None:
        rightIndex = -1
    higherLevelNums = higherLevelNums[leftIndex: rightIndex + 1]
    ignoreNums.extend(higherLevelNums)
    resultList = []
    for count in range(random.randint(0, min(total, len(higherLevelNums)))):
        resultList.append(higherLevelNums.pop(random.randrange(
            len(higherLevelNums))))
    total -= len(resultList)
    if total > 0:
        resultList.extend(generateSingleGroupNumbers(
            rangeMin, rangeMax, total, ignoreNums, chosenNums))
    return resultList
