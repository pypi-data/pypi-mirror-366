from .data_ana import V1_ana
from .data_sci import V1_sci
from version import Version

class V1_version(Version):
    def create_data_type(self, type_of_data):
        if type_of_data == 'ana':
            return V1_ana()
        if type_of_data == 'sci':
            return V1_sci()
        raise Exception('Unknown data type.')
__all__ = ['V1_version', 'V1_ana', 'V1_sci']
