import datetime

from maka.data.Field import Time

from FieldTests import FieldTests, fieldTestClass

    
@fieldTestClass
class TimeFieldTests(FieldTests):
    
    
    fieldClass = Time
    validValue = datetime.time(1, 23, 45)
    invalidValue = ''
    defaultTypeName = 'time'
