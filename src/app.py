import json
from flask import Flask, request
import db
import datetime

app = Flask(__name__)
DB = db.DatabaseDriver()


@app.route("/")
@app.route("/api/users/")
def get_users():
    """
    Endpoint for getting all tasks
    """
    return json.dumps({"users": DB.get_all_users()}), 200


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)
    if "name" not in body:
        return json.dumps({"error": "name is required"}), 400
    if "username" not in body:
        return json.dumps({"error": "username is required"}), 400
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "Creating this user did not work"}), 400

    response = {
        "id" : user_id,
        "name" : name,
        "username" : username,
        "balance" : balance,
        "transactions" : DB.get_user_transxs(user_id)
    }

    return json.dumps(response), 201


@app.route("/api/users/<int:user_id>/")
def get_user_by_id(user_id):
    """
    Endpoint for getting a user by their id
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error" : "User not found"}), 404
    return json.dumps(user), 200
    

@app.route("/api/send/", methods=["POST"])
def send_money():
    """
    Endpoint for sending money from user to user
    """
    body = json.loads(request.data)
    if "receiver_id" not in body:
        return json.dumps({"error": "receiver's id is required"}), 400
    if "sender_id" not in body:
        return json.dumps({"error": "sender's id is required"}), 400
    if "amount" not in body:
        return json.dumps({"error": "amount is required"}), 400
    receiver_id = body.get("receiver_id")
    sender_id = body.get("sender_id")
    amount = body.get("amount")
    
    if amount > DB.get_user_balance(sender_id):
        return json.dumps({"error" : "cannot overdraw balance"}), 400
 
    DB.update_user_by_id(DB.get_user_balance(receiver_id) + amount, receiver_id)
    DB.update_user_by_id(DB.get_user_balance(sender_id) - amount, sender_id)

    response_data = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "amount": amount
    }
    return json.dumps(response_data), 200

@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a user from the database
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error" : "User not found"}), 404
    DB.delete_user_by_id(user_id)
    return json.dumps(user), 200

@app.route("/api/transactions/", methods = ["POST"])
def create_transxs():
    """
    Endpoint for creating a transaction between two users
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted")
    timestamp = datetime.datetime.now()
    transx_id = DB.insert_transx(timestamp, sender_id, receiver_id, amount, message, accepted)
    transx = DB.get_transx_by_id(transx_id)

    if DB.get_user_balance(sender_id) < transx["amount"]:
        return json.dumps({"error": "not enough money in senders account"}), 403

    if accepted:
        DB.update_user_by_id(DB.get_user_balance(receiver_id) + amount, receiver_id)
        DB.update_user_by_id(DB.get_user_balance(sender_id) - amount, sender_id)


    if transx["accepted"] != None:
        transx["accepted"] = bool(transx["accepted"])


    if transx is None: 
        return json.dumps({"error": "could not create transaction"}), 400
    return json.dumps(transx), 201

@app.route("/api/transactions/<int:transx_id>/", methods= ["POST"])
def accept_deny_payment_request(transx_id):
    body=json.loads(request.data)
    accepted = body.get("accepted")
    transx = DB.get_transx_by_id(transx_id)
    sender_id = transx["sender_id"]
    receiver_id = transx["receiver_id"]
    amount = transx["amount"]

    if transx["accepted"] is not None:
        return json.dumps({"error:" : "This transaction has already been accepted or denied"}), 403


    if accepted:
        if DB.get_user_balance(sender_id) > transx["amount"]:
            DB.update_transx(transx_id, accepted)
            DB.update_user_by_id(DB.get_user_balance(receiver_id) + amount, receiver_id)
            DB.update_user_by_id(DB.get_user_balance(sender_id) - amount, sender_id)
            transx["timestamp"] = datetime.datetime.now().isoformat()
            transx["accepted"] = True
            print(transx["accepted"])
        else:   
            return json.dumps({"error": "not enough balance in account"}), 403
    
    if not accepted:
        DB.update_transx(transx_id, accepted)
        transx["accepted"] = bool(transx["accepted"])
    

    return json.dumps(transx), 200

@app.route("/api/users/<int:user_id>/", methods= ["DELETE"])
def delete_user_by_id(user_id):
    """
    Endpoint for deleting a task from the databse
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error" : "User not found"}), 404
    DB.delete_user_by_id(user_id)
    return json.dumps(user), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
