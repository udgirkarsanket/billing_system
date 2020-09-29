from flask_sqlalchemy import SQLAlchemy
import datetime
import decimal
import json
db = SQLAlchemy()
class Products(db.Model):
    product_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    product_name=db.Column(db.String(300),nullable=False)
    company=db.Column(db.String(300))
    type=db.Column(db.String(300))
    size=db.Column(db.String(300))
    weight=db.Column(db.String(300))

    def to_dict(self):
        fields = {}
        for field in [x for x in dir(self) if not x.startswith("_") and x != 'metadata']:
            data = self.__getattribute__(field)
            if type(data) is datetime.datetime:
                data = data.strftime('%Y-%m-%dT%H:%M:%SZ')
            if type(data) is datetime.date:
                data = data.strftime('%Y-%m-%d')
            if not hasattr(data, '__call__'):
                try:
                    json.dumps(data)
                    if field[-4:] == "List" and type(data) is not list:
                        fields[field] = [x for x in data.split(",") if x.strip() != ""]
                    else:
                        fields[field] = data
                except TypeError:
                    if type(data) is decimal.Decimal:
                        fields[field] = float(data)
                    else:
                        fields[field] = None
        return fields

    __table_args__ = {'schema': 'sakshi'}
class Receipt(db.Model):
    receipt_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    receipt_details=db.Column(db.Text(),nullable=False)
    item_list=db.Column(db.Text(),nullable=False)
    user_id=db.Column(db.Integer)

    def to_dict(self):
        fields = {}
        for field in [x for x in dir(self) if not x.startswith("_") and x != 'metadata']:
            data = self.__getattribute__(field)
            if type(data) is datetime.datetime:
                data = data.strftime('%Y-%m-%dT%H:%M:%SZ')
            if type(data) is datetime.date:
                data = data.strftime('%Y-%m-%d')
            if not hasattr(data, '__call__'):
                try:
                    json.dumps(data)
                    if field[-4:] == "List" and type(data) is not list:
                        fields[field] = [x for x in data.split(",") if x.strip() != ""]
                    else:
                        fields[field] = data
                except TypeError:
                    if type(data) is decimal.Decimal:
                        fields[field] = float(data)
                    else:
                        fields[field] = None
        return fields

    __table_args__ = {'schema': 'sakshi'}
class Stock(db.Model):
    stock_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    receipt_id=db.Column(db.Integer())
    receipt_date=db.Column(db.String(300))
    product_name=db.Column(db.String(300),nullable=False)
    entry_type=db.Column(db.String(300),nullable=False)
    qty=db.Column(db.Integer())

    def to_dict(self):
        fields = {}
        for field in [x for x in dir(self) if not x.startswith("_") and x != 'metadata']:
            data = self.__getattribute__(field)
            if type(data) is datetime.datetime:
                data = data.strftime('%Y-%m-%dT%H:%M:%SZ')
            if type(data) is datetime.date:
                data = data.strftime('%Y-%m-%d')
            if not hasattr(data, '__call__'):
                try:
                    json.dumps(data)
                    if field[-4:] == "List" and type(data) is not list:
                        fields[field] = [x for x in data.split(",") if x.strip() != ""]
                    else:
                        fields[field] = data
                except TypeError:
                    if type(data) is decimal.Decimal:
                        fields[field] = float(data)
                    else:
                        fields[field] = None
        return fields

    __table_args__ = {'schema': 'sakshi'}
class User(db.Model):
    user_id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    username=db.Column(db.String(300))
    password=db.Column(db.String(300),nullable=False)
    role=db.Column(db.String(300),nullable=False)
    last_login=db.Column(db.String(200))
    full_name=db.Column(db.String(200))

    def to_dict(self):
        fields = {}
        for field in [x for x in dir(self) if not x.startswith("_") and x != 'metadata']:
            data = self.__getattribute__(field)
            if type(data) is datetime.datetime:
                data = data.strftime('%Y-%m-%dT%H:%M:%SZ')
            if type(data) is datetime.date:
                data = data.strftime('%Y-%m-%d')
            if not hasattr(data, '__call__'):
                try:
                    json.dumps(data)
                    if field[-4:] == "List" and type(data) is not list:
                        fields[field] = [x for x in data.split(",") if x.strip() != ""]
                    else:
                        fields[field] = data
                except TypeError:
                    if type(data) is decimal.Decimal:
                        fields[field] = float(data)
                    else:
                        fields[field] = None
        return fields

    __table_args__ = {'schema': 'sakshi'}
