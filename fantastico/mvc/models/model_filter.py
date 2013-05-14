'''
Copyright 2013 Cosnita Radu Viorel

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. codeauthor:: Radu Viorel Cosnita <radu.cosnita@gmail.com>
.. py:module:fantastico.mvc.models.model_filter
'''
from abc import abstractmethod, ABCMeta
from fantastico.exceptions import FantasticoNotSupportedError

class ModelFilterAbstract(metaclass=ABCMeta):
    '''This is the base class that defines the contract a model filter must follow.'''
    
    @abstractmethod
    def build(self, query):
        '''This method is used for appending the current filter to the query using sqlalchemy specific language.'''
    
    @abstractmethod
    def get_expression(self):
        '''This method is used for retrieving native sqlalchemy expression held by this filter.'''

class ModelFilter(ModelFilterAbstract):
    '''This class provides a model filter wrapper used to dynamically transform an operation to sql alchemy filter
    statements. You can see below how to use it:
    
    .. code-block:: python
    
        id_gt_filter = ModelFilter(PersonModel.id, 1, ModelFilter.GT)'''
    
    GT = "gt"
    GE = "ge"
    EQ = "eq"
    LE = "le"    
    LT = "lt"
    LIKE = "like"
    IN = "in"
    
    _column = None
    _ref_value = None
    _operation = None
    
    @property
    def column(self):
        '''This property holds the column used in the current filter.'''
        
        return self._column

    @property
    def ref_value(self):
        '''This property holds the reference value used in the current filter.'''
        
        return self._ref_value

    @property
    def operation(self):
        '''This property holds the operation used in the current filter.'''
        
        return self._operation
    
    @staticmethod
    def get_supported_operations():
        '''This method returns all supported operations for model filter. For now only the following operations are supported:
        
            * GT - greater than comparison
            * GE - greater or equals than comparison
            * EQ - equals comparison
            * LE - less or equals than comparison
            * LT - less than comparison
            * LIKE - like comparison
            * IN - in comparison.
        '''
        
        return [ModelFilter.GT, ModelFilter.GE, ModelFilter.EQ, ModelFilter.LT, ModelFilter.LE, ModelFilter.LIKE,
                ModelFilter.IN]
    
    def __init__(self, column, ref_value, operation):
        if not self._is_operation_supported(operation):
            raise FantasticoNotSupportedError("Operation %s not supported by ModelFilter." % operation)
        
        self._column = column
        self._ref_value = ref_value
        self._operation = operation        
    
    def _is_operation_supported(self, operation):
        '''This method determines if an operation is supported or not.'''
        
        return operation in ModelFilter.get_supported_operations()
    
    def build(self, query):
        '''This method appends the current filter to a query object.'''
        
        if not query:
            return None

        return query.filter(self.get_expression())
        
    def get_expression(self):
        '''Method used to return the underlining sqlalchemy exception held by this filter.'''
        
        expr = None
        
        if self.operation == ModelFilter.GT:
            expr = self.column > self.ref_value
        elif self.operation == ModelFilter.GE:
            expr = self.column >= self.ref_value
        elif self.operation == ModelFilter.EQ:
            expr = self.column == self.ref_value
        elif self.operation == ModelFilter.LE:
            expr = self.column <= self.ref_value
        elif self.operation == ModelFilter.LT:
            expr = self.column < self.ref_value        
        elif self.operation == ModelFilter.LIKE:
            expr = self.column.like(self.ref_value)
        elif self.operation == ModelFilter.IN:
            if not isinstance(self.ref_value, list):
                raise FantasticoNotSupportedError("Ref value %s is not a list. Lists are required for in comparison." %\
                                                  self.ref_value)

            expr = self.column.in_(self.ref_value)
        
        return expr