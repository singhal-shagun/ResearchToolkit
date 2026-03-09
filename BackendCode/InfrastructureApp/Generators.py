#import string

#def InfrastructureExcelColumnIndexGenerator(*, startingColumnAlphabet):
#    outerAlphabets = list(string.ascii_uppercase)
#    outerAlphabets.insert(0, '')

#    innerAlphabets = list(string.ascii_uppercase)

#    firstRunTrueFalse = True
#    for outermostAlphabet in outerAlphabets:
#        for middleAlphabet in outerAlphabets:
#            if (firstRunTrueFalse):
#                indexOfInitialCharacter = innerAlphabets.index(startingColumnAlphabet)
#            else:
#                indexOfInitialCharacter = 0
#            for innerAlphabet in innerAlphabets[indexOfInitialCharacter:]:
#                columnIndex = "".join([outermostAlphabet, middleAlphabet, innerAlphabet])
#                # Excel has at most 16,384 columns.
#                # Implying, the highest column index can be 'XFD'
#                if (columnIndex != 'XFE'):
#                    yield columnIndex
#                    firstRunTrueFalse = False
#                else:
#                    raise StopIteration()