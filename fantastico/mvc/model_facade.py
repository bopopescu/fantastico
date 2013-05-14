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
.. py:module:: fantastico.mvc.model_facade
'''
from fantastico.exceptions import FantasticoIncompatibleClassError, FantasticoDbError, FantasticoDbNotFoundError
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm.util import class_mapper

class ModelFacade(object):
    '''This class provides a generic model facade factory. In order to work **Fantastico** base model it is recommended
    to use autogenerated facade objects. A facade object is binded to a given model and given database session.'''
        
    _model_pk = None
    _model_cls = None
    _session = None
    
    @property
    def model_cls(self):
        '''This property holds the model based on which this facade is built.'''
        
        return self._model_cls
    
    def __init__(self, model_cls, session):
        '''
        :raises fantastico.exceptions.FantasticoIncompatibleClassError: It raises this exception if the underlining
            model is not a subclass of BASEMODEL.
        '''        

        self._model_cls = model_cls
        self._session = session
        
        if not isinstance(self.model_cls, DeclarativeMeta):
            raise FantasticoIncompatibleClassError("Class %s does not inherits BASEMODEL." % self.model_cls.__class__.__name__)
        
        self._model_pk = self._get_primary_key()
        
    def new_model(self, *args, **kwargs):
        '''This method is used to obtain an instance of the underlining model. Below you can find a very simple example:
        
        .. code-block:: python
        
            class PersonModel(BASEMODEL):
                __tablename__ = "persons"
                
                id = Column("id", Integer, autoincrement=True, primary_key=True)
                first_name = Column("first_name", String(50))
                last_name = Column("last_name", String(50))
                
                def __init__(self, first_name, last_name):
                    self.first_name = first_name
                    self.last_name = last_name
                    
            facade = ModelFacade(PersonModel, fantastico.mvc.SESSION)
            
            model = facade.new_model("John", last_name="Doe")
            
        :param args: A list of positional arguments we want to pass to underlining model constructor.
        :type args: list
        :param kwargs: A dictionary containing named parameters we want to pass to underlining model constructor.
        :type kwargs: dict
        :returns: A BASEMODEL instance if everything is ok.
        '''
                
        return self.model_cls(*args, **kwargs)
    
    def _get_primary_key(self):
        '''This method introspects the underlining model and detects the primary key of the model.'''
        
        return class_mapper(self.model_cls).primary_key
    
    def create(self, model):
        '''This method add the given model in the database.

        .. code-block:: python
        
            class PersonModel(BASEMODEL):
                __tablename__ = "persons"
                
                id = Column("id", Integer, autoincrement=True, primary_key=True)
                first_name = Column("first_name", String(50))
                last_name = Column("last_name", String(50))
                
                def __init__(self, first_name, last_name):
                    self.first_name = first_name
                    self.last_name = last_name
                    
            facade = ModelFacade(PersonModel, fantastico.mvc.SESSION)
            
            model = facade.new_model("John", last_name="Doe")
            facade.create(model)
        
        :returns: The newly generated primary key or the specified primary key (it might be a scalar value or a tuple).
        :raises fantastico.exceptions.FantasticoDbError: Raised when an unhandled exception occurs. By default, session
            is rollback automatically so that other consumers can still work as expected.
        '''
        
        try:
            self._session.add(model)
            self._session.commit()
        
            return [getattr(model, pk_key.name) for pk_key in self._model_pk]
        except Exception as ex:
            self._session.rollback()
            
            raise FantasticoDbError(ex)
    
    def _get_pk_values(self, model):
        '''This method returns the dictionary of pk values from the given model.'''
        
        pk_values = {}
        
        for pk_col in self._model_pk:
            pk_values[pk_col.name] = getattr(model, pk_col.name)
            
        return pk_values
        
    def update(self, model):
        '''This method updates an existing model from the database based on primary key.
        
        .. code-block:: python
        
            class PersonModel(BASEMODEL):
                __tablename__ = "persons"
                
                id = Column("id", Integer, autoincrement=True, primary_key=True)
                first_name = Column("first_name", String(50))
                last_name = Column("last_name", String(50))
                
                def __init__(self, first_name, last_name):
                    self.first_name = first_name
                    self.last_name = last_name
                    
            facade = ModelFacade(PersonModel, fantastico.mvc.SESSION)
            
            model = facade.new_model("John", last_name="Doe")
            model.id = 5
            facade.update(model)

        :raises fantastico.exceptions.FantasticoDbNotFoundError: Raised when the given model does not exist in database.
            By default, session is rollback automatically so that other consumers can still work as expected.
        :raises fantastico.exceptions.FantasticoDbError: Raised when an unhandled exception occurs. By default, session
            is rollback automatically so that other consumers can still work as expected.
        '''
        
        self.find_by_pk(self._get_pk_values(model))
                
        try:
            self._session.merge(model)
            self._session.commit()
        except Exception as ex:
            self._session.rollback()
            
            raise FantasticoDbError(ex)
        
    def find_by_pk(self, pk_values):
        '''This method returns the entity which matches the given primary key values. 
        
        .. code-block:: python
        
            class PersonModel(BASEMODEL):
                __tablename__ = "persons"
                
                id = Column("id", Integer, autoincrement=True, primary_key=True)
                first_name = Column("first_name", String(50))
                last_name = Column("last_name", String(50))
                
                def __init__(self, first_name, last_name):
                    self.first_name = first_name
                    self.last_name = last_name
                    
            facade = ModelFacade(PersonModel, fantastico.mvc.SESSION)
            model = facade.find_by_pk({PersonModel.id: 1})
        '''
        
        query = self._session.query(self.model_cls)
        
        for pk_col in pk_values.keys():
            query = query.filter(pk_col == pk_values[pk_col])
        
        results = query.all()
        
        if not results:
            self._session.rollback()
            
            pk_msg = ["%s=%s" % (pk_col, pk_values[pk_col]) for pk_col in pk_values.keys()]
            
            raise FantasticoDbNotFoundError("Model %s does not exist." % ",".join(pk_msg))
        
        return results[0]
    
    def delete(self, model):
        '''This method deletes a given model from database. Below you can find a simple example of how to use this:
        
        .. code-block:: python
        
            class PersonModel(BASEMODEL):
                __tablename__ = "persons"
                
                id = Column("id", Integer, autoincrement=True, primary_key=True)
                first_name = Column("first_name", String(50))
                last_name = Column("last_name", String(50))
                
                def __init__(self, first_name, last_name):
                    self.first_name = first_name
                    self.last_name = last_name
                    
            facade = ModelFacade(PersonModel, fantastico.mvc.SESSION)
            model = facade.find_by_pk({PersonModel.id: 1})
            facade.delete(model)

        :raises fantastico.exceptions.FantasticoDbError: Raised when an unhandled exception occurs. By default, session
            is rollback automatically so that other consumers can still work as expected.
        '''
        
        try:
            self._session.delete(model)
            self._session.commit()
        except Exception as ex:
            self._session.rollback()
            
            raise FantasticoDbError(ex)
    
    def get_records_paged(self, start_record, end_record, filter_expr=None, sort_expr=None):
        '''This method retrieves all records matching the given filters sorted by the given expression.

        .. code-block:: python
        
            records = facade.get_records_paged(start_record=0, end_record=5, 
                                       sort_expr=[ModelSort(Blog.create_date, ModelSort.ASC,
                                                  ModelSort(Blog.title, ModelSort.DESC)],
                                       filter_expr=ModelFilterAnd(
                                                       ModelFilter(Blog.id, 1, ModelFilter.GT),
                                                       ModelFilter(Blog.id, 5, ModelFilter.LT))))
        
        :param start_record: A zero indexed integer that specifies the first record number.
        :type start_record: int
        :param end_record: A zero indexed integer that specifies the last record number.
        :type end_record: int
        :param filter_expr: A list of :py:class:`fantastico.mvc.models.model_filter.ModelFilterAbstract` which are applied in order.
        :type filter_expr: list
        :param sort_expr: A list of :py:class:`fantastico.mvc.models.model_sort.ModelSort` which are applied in order.
        :type sort_expr: list
        :returns: A list of matching records strongly converted to underlining model.
        :raises fantastico.exceptions.FantasticoDbError: This exception is raised whenever an exception occurs in retrieving
            desired dataset. The underlining session used is automatically rollbacked in order to guarantee data integrity.
        '''
        
        if filter_expr and not isinstance(filter_expr, list):
            filter_expr = [filter_expr]
            
        if sort_expr and not isinstance(sort_expr, list):
            sort_expr = [sort_expr]

        query = self._session.query(self.model_cls)
        
        try:
            for model_filter in filter_expr or []:
                query = model_filter.build(query)
                
            for model_sort in sort_expr or []:
                query = model_sort.build(query)
            
            query = query.offset(start_record).limit(end_record - start_record)
            
            return query.all()
        except Exception as ex:
            self._session.rollback()
            
            raise FantasticoDbError(ex)
    
    def count_records(self, filter_expr=None):
        '''This method is used for counting the number of records from underlining facade. In addition it applies the
        filter expressions specified (if any).
        
        .. code-block:: python
        
            records = facade.count_records(
                                       filter_expr=ModelFilterAnd(
                                                       ModelFilter(Blog.id, 1, ModelFilter.GT),
                                                       ModelFilter(Blog.id, 5, ModelFilter.LT)))
        
        :param filter_expr: A list of :py:class:`fantastico.mvc.models.model_filter.ModelFilterAbstract` which are applied in order.
        :type filter_expr: list
        :raises fantastico.exceptions.FantasticoDbError: This exception is raised whenever an exception occurs in retrieving
            desired dataset. The underlining session used is automatically rollbacked in order to guarantee data integrity.
        '''
        
        if filter_expr and not isinstance(filter_expr, list):
            filter_expr = [filter_expr]
        
        try:
            query = self._session.query(self.model_cls)
    
            for model_filter in filter_expr or []:
                query = model_filter.build(query)
    
            return query.count()
        except Exception as ex:
            self._session.rollback()
            
            raise FantasticoDbError(ex)