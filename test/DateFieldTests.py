from __future__ import print_function

import datetime

from maka.data.Field import Date

from FieldTests import FieldTests, fieldTestClass

    
@fieldTestClass
class DateFieldTests(FieldTests):
    
    
    fieldClass = Date
    validValue = datetime.date(2013, 7, 29)
    invalidValue = ''
    defaultTypeName = 'date'
    