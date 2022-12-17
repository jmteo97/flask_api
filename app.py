#flask sql db

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root@localhost/customer'
db = SQLAlchemy(app)

# create tbl start
class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    email = db.Column(db.String(50))
    phone = db.Column(db.String(11))
    address = db.Column(db.String(100))
    createdDate = db.Column(db.DateTime)

    def __init__(self,name,email,phone,address,createdDate):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.createdDate = createdDate

with app.app_context(): 
    db.create_all()

#create tbl end

def get_timestamp_now():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

class UserSchema(SQLAlchemyAutoSchema):
    class Meta(SQLAlchemyAutoSchema.Meta):
        model = Users
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=False)
    address = fields.Raw(required=False)
    createdDate = fields.DateTime(required=True)

def errorMsg():
    message = {
        'status': 404,
        'message': 'Record not found',
    }
    respone = jsonify(message)
    return respone

# post one input
@app.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    address = request.json['address']
    createdDate = get_timestamp_now()
    
    new_product = Users(name, email, phone, address, createdDate)
    db.session.add(new_product)
    db.session.commit()
    message = {
        'status': 200,
        'message': 'Customer successfully added!',
        'insert_id': new_product.id
    }
    respone = jsonify(message)
    return respone

# post multiple input in array
@app.route('/add_customers', methods=['POST'])
def add_customers():
    json_dict = request.get_json()
    customer_entries = []
    for info in json_dict:
        new_entry = Users(
            name=info['name'],
            email=info['email'],
            phone=info['phone'],
            address=info['address'],
            createdDate = get_timestamp_now()
        )
        customer_entries.append(new_entry)
    db.session.add_all(customer_entries)
    db.session.commit()
    message = {
        'status': 200,
        'message': 'Customer successfully added!'
    }
    respone = jsonify(message)
    return respone

# get all user
@app.route('/get_all_customers', methods=['GET'])
def get_all_customers():
   get_customers = Users.query.all()
   if get_customers:
        users_schema = UserSchema(many=True)
        get_all = users_schema.dump(get_customers)
        message = {
            'status': 200,
            'message': 'Get all customer successfully!',
            "data_list": get_all
        }
        respone = jsonify(message)
        return respone
   else:
        return errorMsg() 

# get one user
@app.route('/get_specific_customer', methods=['GET'])
def get_specific_customer():
   id = request.json['id']
   get_customer = Users.query.get(id)
   if get_customer:
        users_schema = UserSchema()
        get = users_schema.dump(get_customer)
        message = {
            'status': 200,
            'message': 'Get customer with id: ' + id + ' successfully!',
            "data_list": get
        }
        respone = jsonify(message)
        return respone
   else:
        return errorMsg()  

#update one user
@app.route('/update_customer', methods=['PUT'])
def update_customer():
    id = request.json['id']
    user = Users.query.get(id)
    if user:
        customer_data = request.get_json() #use diff 
        user.name = customer_data["name"]
        user.email = customer_data["email"]
        user.phone = customer_data["phone"]
        user.address = customer_data["address"]
        db.session.commit()
        message = {
            'status': 200,
            'message': 'Customer successfully updated!',
        }
        respone = jsonify(message)
        return respone
    else:
        return errorMsg() 

#update batch users
@app.route('/update_customers', methods=['PUT'])
def update_customers():
    json_dict = request.get_json()
    for info in json_dict:
        id = info['id']
        user = Users.query.get(id)
        if user:
            user.name = info['name']
            user.email = info['email']
            user.phone = info['phone']
            user.address = info['address']
            db.session.commit()
        else:
            continue
        
    message = {
        'status': 200,
        'message': 'Customers successfully updated!',
    }
    respone = jsonify(message)
    return respone

#delete one user
@app.route('/delete_customer', methods=['DELETE'])
def delete_customer():
    id = request.json['id']
    delete_id = Users.query.get(id)
    if delete_id:
        db.session.delete(delete_id)
        db.session.commit()
        message = {
            'status': 200,
            'message': 'Customer successfully deleted!',
        }
        respone = jsonify(message)
        return respone
    else:
        return errorMsg() 
    
# delete batch users
@app.route('/delete_customers', methods=['DELETE'])
def delete_customers():
    json_dict = request.get_json()
    for info in json_dict:
        id = info['id']
        delete_id = Users.query.get(id)
        if delete_id:
            db.session.delete(delete_id)
            db.session.commit()
        else:
            continue

    message = {
        'status': 200,
        'message': 'Customers successfully deleted!',
    }
    respone = jsonify(message)
    return respone

if __name__ == "__main__":
    app.run(debug=True)




