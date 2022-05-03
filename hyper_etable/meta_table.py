import hyperc.util

class TableElementMeta(type):
    @hyperc.util.side_effect_decorator
    def __str__(self):
        return self.__table_name__
    
    @hyperc.util.side_effect_decorator
    def __repr__(self):
        # return str(self)  #  what was the reason for this?
        return self.__table_name__
