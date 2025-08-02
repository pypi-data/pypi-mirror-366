from yta_general_utils.url.dataclasses import UrlParameter, UrlParameters
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from typing import Union


class UrlHandler:
    """
    Class to wrap the functionality related with urls.
    """

    @staticmethod
    def encode_url_parameter(
        parameter: Union[UrlParameter, str]
    ) -> str:
        """
        Get the provided 'parameter' encoded based on
        the RFC 3986.

        - From 'hola dani' to 'hola%20dani'.
        - From 'key=value largo' to 'key%3Dvalue%20largo'
        """
        ParameterValidator.validate_mandatory_instance_of('parameter', parameter, [UrlParameter, str])

        parameter = (
            UrlParameter.from_str(parameter)
            if PythonValidator.is_string(parameter) else
            parameter 
        )
        
        return parameter.encoded
    
    @staticmethod
    def encode_url_parameters(
        parameters: Union[UrlParameters, dict]
    ) -> str:
        """
        Get the provided 'parameters' encoded based on
        the RFC 3986.

        - From 'hola dani&do_force' to 'hola%20dani&do_force'.
        - From 'key=value largo&do_force' to 'key%3Dvalue%20largo&do_forceo'
        """
        ParameterValidator.validate_mandatory_instance_of('parameters', parameters, [UrlParameters, dict])

        parameters = (
            UrlParameters.from_dict(parameters)
            if PythonValidator.is_dict(parameters) else
            parameters
        )

        return parameters.encoded