import datetime
import uuid
from flask import Blueprint, request, jsonify
from models.user_device_model import User_Device
from models.user_model import User
from config.db_config import  USER_COLLECTION
from utils.helper import apply_filters, upload_to_azure
from flask_jwt_extended import create_access_token, decode_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth", __name__)

# ✅ Get auths (Read with Filters & Pagination)
@auth_bp.route("/RegisterDeviceWithPhone", methods=["POST"])
def get_auths():
    """Fetch auths using filters and pagination."""
    try:
        data = request.get_json()
        json_data = data.get("Json", {})

        # Extract User & UserDevice data
        user_data_ = json_data.get("User", {})
        user_device_data = json_data.get("UserDevice", {})
        print(user_data_)

        user=USER_COLLECTION.find_one({"Phone":user_data_["Phone"]})
        print(user)
        if  user:
            user_data=user
            device_data=User_Device.update_or_insert_user_device(user["DeviceId"],user_device_data)
            is_new_user=False
        else:
            device_id=str(uuid.uuid4())
            user_device_data["_id"]=device_id
            user_device_data["DeviceId"]=device_id
            device_data=User_Device.update_or_insert_user_device(device_id,user_device_data)
            
            user_id=str(uuid.uuid4())
            user_data_["_id"]=user_id
            user_data_["UserId"]=user_id
            user_data_["DeviceId"]=device_id
            user_data_["favourite"]={"favouriteEvent":[],"favouritePlace":[]}
            
            user_data_["MigratedProfileImage"]=upload_to_azure(user_data_["MigratedProfileImage"],"image")
            user_data=User.insert_user(user_data_)
            print(user_data)
            is_new_user=True
            
            
            
        access_token = create_access_token(identity=user_data["UserId"], expires_delta=datetime.timedelta(days=30))  
        result={
            "status":True,
            "data":{
            "Users":user_data,
            "UserDevice":device_data,
            "UserId":user_data["UserId"],
            "IsNewUser":is_new_user,
            "token":access_token
        }}    
            

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

