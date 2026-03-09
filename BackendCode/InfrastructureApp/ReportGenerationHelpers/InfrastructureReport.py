import io
import xlsxwriter
from .ReportFormats import reportFormatsDictionary

#THIS CLASS ISN'T BEING USED FOR NOW.
#class InfrastructureReport:
#    bufferObject = None
#    workbook = None
#    reportFormatObjectsDictionary = {}

#    def __init__(self) -> None:
#        self.bufferObject = io.BytesIO()
#        self.workbook = xlsxwriter.Workbook(self.bufferObject)
#        for formatName in reportFormatsDictionary.keys():
#            self.reportFormatObjectsDictionary[formatName] = self.workbook.add_format(reportFormatsDictionary[formatName])
            
#    def getDataFormatObjects(self, rowIndex):
#        rowFormatObjectNonWrapped = self.reportFormatObjectsDictionary[str(rowIndex%8)]
#        rowFormatObjectWrapped = self.reportFormatObjectsDictionary[str(rowIndex%8)+'Wrapped']
#        return (rowFormatObjectNonWrapped, rowFormatObjectWrapped)

#    def closeReport(self):
#        self.workbook.close()
#        self.bufferObject.seek(0)
#        return self.bufferObject




def createWorkbook():
    bufferObject = io.BytesIO()
    workbook = xlsxwriter.Workbook(bufferObject)
    reportFormatObjectsDictionary = {}
    for formatName in reportFormatsDictionary.keys():
        reportFormatObjectsDictionary[formatName] = workbook.add_format(reportFormatsDictionary[formatName])
    return (bufferObject, workbook, reportFormatObjectsDictionary)


def dataFormatObjects(reportFormatObjectsDictionary, rowIndex):
    rowFormatObjectNonWrapped = reportFormatObjectsDictionary[str(rowIndex%8)]
    rowFormatObjectWrapped = reportFormatObjectsDictionary[str(rowIndex%8)+'Wrapped']
    return (rowFormatObjectNonWrapped, rowFormatObjectWrapped)



def columnIndexGenerator(startingColumnAlphabet):
    """
    This generator function generates Excel column indices. 
    It takes a starting column alphabet as input and yields successive column indices. 
    It doesn't yield iteratively beyond the column index 'XFD'.
    """
    import string

    outerAlphabets = list(string.ascii_uppercase)
    outerAlphabets.insert(0, '')

    innerAlphabets = list(string.ascii_uppercase)

    firstRunTrueFalse = True
    for outermostAlphabet in outerAlphabets:
        for middleAlphabet in outerAlphabets:
            if (firstRunTrueFalse):
                indexOfInitialCharacter = innerAlphabets.index(startingColumnAlphabet)
            else:
                indexOfInitialCharacter = 0
            for innerAlphabet in innerAlphabets[indexOfInitialCharacter:]:
                columnIndex = "".join([outermostAlphabet, middleAlphabet, innerAlphabet])
                # Excel has at most 16,384 columns.
                # Implying, the highest column index can be 'XFD'
                if (columnIndex != 'XFE'):
                    yield columnIndex
                    firstRunTrueFalse = False
                else:
                    raise StopIteration()


def getColumnNumber(columnString):
    """
    Converts a column string to its corresponding column number in Excel.

    Parameters:
    - columnString (str): The column string to be converted.

    Returns:
    - columnIndex (int): The corresponding column number.

    Example:
    getColumnNumber('A') returns 1
    getColumnNumber('AA') returns 27
    getColumnNumber('AAA') returns 703
    """
    columnIndex = 0
    for character in columnString[:-1]:
        columnIndex += ((ord(character)-65)+1) * 26
    columnIndex += ord(columnString[-1]) - 65 + 1
    return (columnIndex - 1)


def getLastUpdateDateFromQuerySet(querySet):
    """
    Get the last update date from a given queryset.
    Parameters:
        - querySet (QuerySet): The queryset to retrieve the last update date from.
    Returns:
        - date (datetime.date or None): The last update date as a datetime.date object, or, 
        - `None` if the queryset is empty.

    Example:
    >>> getLastUpdateDateFromQuerySet(querySet)
    datetime.date(2021, 10, 15)
    """
    if (len(querySet) > 0):
        return querySet.order_by('-dbLastModifiedDateTime')[0].dbLastModifiedDateTime.date()
    else:
        return None


def getLastUpdateDateStringFromQuerySet(querySet):
    """
    Get the last update date as a formatted string from a given queryset.
    Parameters:
        - querySet (QuerySet): The queryset to retrieve the last update date from.
    Returns:
        - dateString (str or None): The last update date as a formatted string in the format 'YYYY-MM-DD', or
        - `None` if the queryset is empty.
    Example:
        >>> getLastUpdateDateStringFromQuerySet(querySet)
        'Last update date: 2021-10-15'
    """
    if (len(querySet) > 0):
        dateString = getLastUpdateDateFromQuerySet(querySet).strftime('%Y-%m-%d')
        return ("Last update date: " + dateString)
    else:
        return None


def getLastUpdateDateStringFromDateObject(dateObject):
    '''
    Returns the last update date as a formatted string from a given date object.
    Parameters:
        dateObject (datetime): The date object from which to extract the last update date.
    Returns:
        str: The last update date in the format 'YYYY-MM-DD'.
    Example:
        >>> date = datetime.datetime(2022, 1, 1)
        >>> getLastUpdateDateStringFromDateObject(date)
        'Last update date: 2022-01-01'
    '''
    if (dateObject != None):
        dateString = dateObject.strftime('%Y-%m-%d')
        return ("Last update date: " + dateString)
    else:
        return None