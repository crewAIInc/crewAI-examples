class SnowflakeCortexCustomServiceError(Exception):  # use this for all your exceptions
    """
    Custom exception class for handling errors related to the Custom LLM.

    This class extends the built-in `Exception` class and serves as a 
    custom exception type for errors encountered specifically within the 
    custom LLM implementation. It can be used to raise and handle errors 
    related to the processing or interaction with the custom LLM, making 
    error handling more structured and specific to the application.

    Inherits from:
        Exception: The base class for all built-in exceptions.

    Usage:
        Raise this exception to indicate an error specifically related to 
        the custom LLM processing or interactions.
    """
    def __init__(
        self,
        status_code,
        message,
    ):
        self.status_code = status_code
        self.message = message
        super().__init__(
            self.message
        )  
