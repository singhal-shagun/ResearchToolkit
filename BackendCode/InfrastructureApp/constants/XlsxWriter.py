class DataValidationOptions:
    """
    Data validation options for XlsxWriter's worksheet.data_validation() method.
    Reference: https://xlsxwriter.readthedocs.io/working_with_data_validation.html#working-with-data-validation
    """
    VALIDATE = "validate"
    CRITERIA = "criteria"
    VALUE = "value"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    SOURCE = "source"
    IGNORE_BLANK = "ignore_blank"
    DROPDOWN = "dropdown"
    INPUT_TITLE = "input_title"
    INPUT_MESSAGE = "input_message"
    SHOW_INPUT = "show_input"
    ERROR_TITLE = "error_title"
    ERROR_MESSAGE = "error_message"
    ERROR_TYPE = "error_type"
    SHOW_ERROR = "show_error"
    MULTI_RANGE = "multi_range"

    class CriteriaValues:
        """
        When `criteria` is used as a DataValidation option, it can be passed one of these values.
        """
        BETWEEN = "between"
        NOT_BETWEEN = "not between"
        EQUAL_TO = "equal to"
        NOT_EQUAL_TO = "not equal to"
        GREATER_THAN = "greater than"
        LESS_THAN = "less than"
        GREATER_THAN_OR_EQUAL_TO = "greater than or equal to"
        LESS_THAN_OR_EQUAL_TO = "less than or equal to"

