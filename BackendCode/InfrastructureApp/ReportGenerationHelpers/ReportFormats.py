#FORMAT NAMES
h1 = 'h1'
h2 = 'h2'
h3 = 'h3'
textWrapFormatForMultilineString = 'textWrapFormatForMultilineString'
textHorizontalCenterAlignFormat = 'textHorizontalCenterAlignFormat'
serialNumber = 'serialNumber'
data0 = '0'
data0Wrapped = '0Wrapped'
data1 = '1'
data1Wrapped = '1Wrapped'
data2 = '2'
data2Wrapped = '2Wrapped'
data3 = '3'
data3Wrapped = '3Wrapped'
data4 = '4'
data4Wrapped = '4Wrapped'
data5 = '5'
data5Wrapped = '5Wrapped'
data6 = '6'
data6Wrapped = '6Wrapped'
data7 = '7'
data7Wrapped = '7Wrapped'


# Create an iterable of 
reportFormatsDictionary = {
    h1 : {
        'text_wrap':'true',
        'bg_color': '#465468',
        'border': 1,
        'font_color': '#FFFFFF',
        'bold': True,
        'align': 'center',
        'font_size': 16,
        },
    h2 : {
        'text_wrap':'true',
        'bg_color': '#465468',
        'border': 1,
        'font_color': '#FFFFFF',
        'bold': True,
        'align': 'center',
        'font_size': 14,
        },
    h3 : {
        'text_wrap':'true',
        'bg_color': '#465468',
        'border': 1,
        'font_color': '#FFFFFF',
        'bold': True,
        'align': 'center',
        'font_size': 12,
        },
    textWrapFormatForMultilineString : {
        'text_wrap':'true',
        },
    textHorizontalCenterAlignFormat : {
        'align': 'center',
        },
    serialNumber : {
        #text_wrap property is kept off because serial numbers don't need to be multi-line.
        'bg_color': '#465468',
        'border': 1,
        'font_color': '#FFFFFF',
        'bold': True,
        'align': 'center',
        #font_size property isn't defined for serialNumbers to let it default to 11.
        },
    data0 : {
        'bg_color': '#f2f2f2',
        'border': 1,
        },
    data0Wrapped : {
        'bg_color': '#f2f2f2',
        'border': 1,
        'text_wrap':'true',
        },
    data1 : {
        'bg_color': '#ded9c5',
        'border': 1,
        },
    data1Wrapped : {
        'bg_color': '#ded9c5',
        'border': 1,
        'text_wrap':'true',
        },
    data2 : {
        'bg_color': '#dce6f2',
        'border': 1,
        },
    data2Wrapped : {
        'bg_color': '#dce6f2',
        'border': 1,
        'text_wrap':'true',
        },
    data3 : {
        'bg_color': '#f2dcda',
        'border': 1,
        },
    data3Wrapped : {
        'bg_color': '#f2dcda',
        'border': 1,
        'text_wrap':'true',
        },
    data4 : {
        'bg_color': '#edf2df',
        'border': 1,
        },
    data4Wrapped : {
        'bg_color': '#edf2df',
        'border': 1,
        'text_wrap':'true',
        },
    data5 : {
        'bg_color': '#e6dfed',
        'border': 1,
        },
    data5Wrapped : {
        'bg_color': '#e6dfed',
        'border': 1,
        'text_wrap':'true',
        },
    data6 : {
        'bg_color': '#daeef3',
        'border': 1,
        },
    data6Wrapped : {
        'bg_color': '#daeef3',
        'border': 1,
        'text_wrap':'true',
        },
    data7 : {
        'bg_color': '#fde9d9',
        'border': 1,
        },
    data7Wrapped : {
        'bg_color': '#fde9d9',
        'text_wrap':'true',
        'border': 1,
        },
    }