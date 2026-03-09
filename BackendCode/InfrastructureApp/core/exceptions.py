def extractErrorMessagesFromException(exception):
    errorMessages = []
    if hasattr(exception, 'message_dict') and len(exception.message_dict) > 0:
        """Case-1: When the exception has 'message_dict' attribute, we extract those messages."""
        for (key, exceptionList) in exception.message_dict.items():
            for message in exceptionList:
                errorMessages.append(key + ": " + message)
    elif hasattr(exception, 'messages') and len(exception.messages) > 0:
        """Case-1: When the exception has 'messages' attribute, we extract those messages."""
        [errorMessages.append(errorMessage) for errorMessage in exception.messages]
    else:
        """Case-2: When the exception doesn't have 'messages' attribute, we extract error messages from 'args' attribute."""
        [errorMessages.append(arg) for arg in exception.args]
    return errorMessages
