from google.appengine.ext import ndb

from core.models import BaseModel


class TimezoneOffset(BaseModel):
    tzo = ndb.IntegerProperty(required=True)

    @classmethod
    def create(cls, tzo):
        if -12 <= int(tzo) <= 14:
            TimeZone = TimezoneOffset.query().get()
            if TimeZone:
                TimeZone.tzo = int(tzo)
            else:
                TimeZone = TimezoneOffset(tzo=int(tzo))
            TimeZone.put()
            return True
        else:
            return False
