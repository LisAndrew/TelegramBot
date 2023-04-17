from copy import deepcopy
from datetime import datetime
from itertools import groupby

from entities.TempRecord import TempRecord


def getRecordClassFields(record) -> TempRecord:
    mainStr = record['main']
    weather = record['weather'][0]

    return TempRecord(
        mainStr['temp'],
        mainStr['feels_like'],
        weather['description'],
        record['dt_txt']
    )


def labels(idx_and_item):
    index, item = idx_and_item

    if index > 1 and index % 8 == 0:
        return datetime.strptime(item.date, "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y")


class TempList:
    def __init__(self, list) -> None:
        self.dates = map(getRecordClassFields, list)

    def getFirstDate(self) -> TempRecord:
        return list(self.dates)[0]

    def groupByDate(self):
        return groupby(self.dates, lambda item: item.date)

    def plotData(self, inputDates):
        plot = dict()

        plot['labels'] = list(
            deepcopy(map(labels, enumerate(inputDates))))

        plot['x'] = list(
            deepcopy(map(lambda rec: rec.date, inputDates))
        )
        plot['y'] = list(
            deepcopy(map(lambda rec: rec.temp, inputDates)))

        return plot

    def getRangeDates(self, fromRange, toRange):
        def my_filter(item: TempRecord):
            itemDate = datetime.strptime(
                item.date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

            return datetime.strptime(fromRange, "%Y-%m-%d").date()
            # <= itemDate <= datetime.strptime(toRange, "%Y-%m-%d").date()

        return list(deepcopy(filter(my_filter, self.dates)))

    def omitTodayFromList(self):
        def my_filter(item: TempRecord):
            itemDate = datetime.strptime(
                item.date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            currentDate = datetime.now().strftime("%Y-%m-%d")

            return itemDate != currentDate

        return list(deepcopy(filter(my_filter, self.dates)))
