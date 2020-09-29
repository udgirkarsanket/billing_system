from werkzeug.security import check_password_hash

import flask
from functools import wraps
from models import *
from sqlalchemy import join


def requires_auth():
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'username' not in flask.session:
                return unauthorized_abort()
            else:
                return  f(*args, **kwargs)
        return decorated
    return wrapper

def unauthorized_abort():
    return flask.render_template('login.html')

def authenticate(username,password):
    from models import User
    from werkzeug.security import check_password_hash
    userList=db.session.query(User).filter(User.username == username).first()
    if check_password_hash(userList.password,password):
        flask.session['full_name'] = userList.full_name
        flask.session['user_id'] = userList.user_id
        flask.session['role'] = userList.role
        flask.session['username'] = userList.username
        userList.last_login = datetime.datetime.now().strftime("%Y-%m-%d")
        db.session.add(userList)
        db.session.commit()
        return True
    else:
        return False

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)
def before_request():
    db.session.execute("""SET search_path TO "%(schema)s";""" % dict(schema=app.config["SCHEMA_NAME"]))
    db.session.commit()
@app.route('/login/',methods=['GET', 'POST'])
def login():
    auth=authenticate(flask.request.form.get('username',''),flask.request.form.get('password',''))
    if auth:
        return flask.redirect('/')
    else:
        return flask.render_template('/login.html',error="Login Failed")

@app.route('/logout/')
def logout():
    if 'username' in flask.session:
        del flask.session['username']
    if 'role' in flask.session:
        del flask.session['role']
    if 'full_name' in flask.session:
        del flask.session['full_name']
    if 'user_id' in flask.session:
        del flask.session['user_id']
    return flask.redirect('/')


@app.route('/')
@requires_auth()
def home():
    return flask.render_template('main.html')

@app.route('/open_add_product')
@requires_auth()
def open_add_product():
    return flask.render_template('add_product.html')

@app.route('/open_add_receipt')
@requires_auth()
def open_add_receipt():
    from models import Products,Stock
    product_list = [k.to_dict() for k in Products.query.order_by(Products.product_name).all()]
    for product in product_list:
        stocks = Stock.query.filter(Stock.product_name==product['product_name']).all()
        sum=0
        for stock in stocks:
            if stock.entry_type=='sell':
                sum = sum-stock.qty
            elif stock.entry_type=='purchase':
                sum = sum+stock.qty
        product['stock'] = sum
    return flask.render_template('add_receipt.html',product_list=json.dumps(product_list))

@app.route('/open_view_stock')
@requires_auth()
def open_view_stock():
    return flask.render_template('view_stock.html')

@app.route('/open_print_receipt')
@requires_auth()
def open_print_receipt():
    return flask.render_template('print_receipt.html')

@app.route('/add_product',methods=['GET', 'POST'])
def add_product():
    from models import Products,Stock
    if 'product_id' in flask.request.json:
        product = Products.query.get(flask.request.json.get('product_id',''))
        stocks = Stock.query.filter(Stock.product_name==product.product_name).all()
        for stock in stocks:
            stock.product_name = " ".join([flask.request.json.get('company',''),flask.request.json.get('type',''),flask.request.json.get('size',''),flask.request.json.get('weight','')]).upper().strip()
            receipts = Receipt.query.filter(Receipt.receipt_id==stock.receipt_id)
            for receipt in receipts:
                print(receipt.item_list)
                receipt.item_list=json.loads(receipt.item_list)
                for item in receipt.item_list:
                    if(item['product']==product.product_name):
                        item['product']=stock.product_name
                receipt.item_list = json.dumps(receipt.item_list)
                print(receipt.item_list)
                db.session.add(receipt)
                db.session.commit()
            db.session.add(stock)
            db.session.commit()
    else:
        product=Products()
    product.product_name = " ".join([flask.request.json.get('company',''),flask.request.json.get('type',''),flask.request.json.get('size',''),flask.request.json.get('weight','')]).upper().strip()
    product.company = flask.request.json.get('company','').upper()
    product.type = flask.request.json.get('type','').upper()
    product.size = flask.request.json.get('size','').upper()
    product.weight = flask.request.json.get('weight','').upper()
    db.session.add(product)
    db.session.commit()
    return flask.jsonify(ok=True, product_name=product.product_name)

@app.route('/delete_product/<string:id>',methods=['GET'])
def delete_product(id):
    product = Products.query.get(id)
    stocks = Stock.query.filter(Stock.product_name==product.product_name).all()
    for stock in stocks:
        db.session.delete(stock)
        db.session.commit()
    db.session.delete(product)
    db.session.commit()
    return flask.jsonify(ok=True)

@app.route('/add_receipt',methods=['GET', 'POST'])
def add_receipt():
    from models import Receipt,Stock
    receipt = Receipt()
    receipt.item_list = json.dumps(flask.request.json.get('item_list',[]))
    receipt.receipt_details = json.dumps(flask.request.json.get('receipt_details',{}))
    receipt.user_id = flask.session['user_id']
    db.session.add(receipt)
    db.session.commit()
    entry_type = flask.request.json.get('receipt_details',{}).get('entry_type')
    receipt_date = flask.request.json.get('receipt_details',{}).get('creation_date')
    for item in flask.request.json.get('item_list',[]):
        entry=Stock()
        entry.receipt_id =receipt.receipt_id
        entry.product_name = item['product']
        entry.qty = item['qty']
        entry.receipt_date = receipt_date
        entry.entry_type = entry_type
        db.session.add(entry)
        db.session.commit()

    return flask.jsonify(ok=True)

@app.route('/get_all_stock',methods=['GET', 'POST'])
def get_all_stock():
    from models import Stock
    stock=[k.to_dict() for k in Stock.query.all()]
    product_list = list(set([k['product_name'] for k in stock]))
    return flask.jsonify(ok=True,stock=stock,product_list=product_list)

@app.route("/view_receipt/<string:receipt_id>")
def view_receipt(receipt_id):
    from models import Receipt
    receipt=Receipt.query.get(receipt_id)
    return flask.render_template('receipt.html',receipt_details=receipt.receipt_details,item_list=receipt.item_list,receipt_id=receipt.receipt_id)

@app.route("/get_receipts")
def get_receipts():
    from models import Receipt
    receipts=[]
    for receipt in Receipt.query.all():
        receipt.receipt_details = json.loads(receipt.receipt_details)
        temp = dict(receipt_id=receipt.receipt_id,receipt_date=receipt.receipt_details['creation_date'],customer_name=receipt.receipt_details['customer_name'],total=receipt.receipt_details['total_cost'])
        receipts.append(temp)
    return flask.jsonify(ok=True,receipts=receipts)

@app.route("/products_available")
def products_available():
    from models import Products
    product_list = [k.to_dict() for k in Products.query.order_by(Products.company).all()]
    return flask.jsonify(ok=True, product_list=product_list)


@app.route("/get_stock")
def get_stock():
    from models import Stock,Products
    products=[]
    data = [dict(k) for k in db.session.execute("""select a.product_name,b.entry_type,b.qty from "sakshi".products a join "sakshi".stock b on (a.product_name=b.product_name)""")]
    for item in db.session.query(Products.product_name).distinct():
        temp = {}
        temp['product_name'] = item[0]
        sum = 0
        for row in filter(lambda x:x['product_name']==item[0],data):
            if row['entry_type']=='sell':
                sum = sum-row['qty']
            if row['entry_type']=='purchase':
                sum = sum+row['qty']
        temp['stock'] = sum
        products.append(temp)
    return flask.jsonify(ok=True,products=products)


@app.route("/delete_receipt/<string:receipt_id>")
def delete_receipt(receipt_id):
    from models import Stock,Products,Receipt
    receipt = Receipt.query.filter(Receipt.receipt_id==receipt_id).first()
    db.session.delete(receipt)
    db.session.commit()
    stocks=Stock.query.filter(Stock.receipt_id==receipt_id).all()
    for stock in stocks:
        db.session.delete(stock)
        db.session.commit()
    return flask.jsonify(ok=True)


if __name__=='__main__':
    app.run(port=8080)