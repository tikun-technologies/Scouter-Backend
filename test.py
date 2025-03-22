import firebase_admin
from firebase_admin import credentials, messaging

# Load Firebase credentials (Replace with the correct path to your JSON file)
cred = credentials.Certificate("config/firebase.json")
firebase_admin.initialize_app(cred)

dheeraj_token="dNZOBddJ5EaTuoe4DMtR-n:APA91bHrdvC6b3BeuvP1YWRcXSmyQSjGMt_EbT9Iu00Gpa4nzoag33HMBiFS32h2WXiusAQbZKTWp64bODG5E1OIAO2rlsO4vyc5KeLe5Z8z0-ttyfv7G5U"
import firebase_admin
from firebase_admin import credentials, messaging

# Load Firebase credentials
# cred = credentials.Certificate("path/to/firebase_credentials.json")
# firebase_admin.initialize_app(cred)

def send_push_notification_with_data(device_token, title, message, image_url, place_id):
    """Send a push notification with custom data (Supports Android & iOS)"""

    message = messaging.Message(
        # notification=messaging.Notification(
        #     title=title,
        #     body=message,
        #     image=image_url  # ✅ Image for Android & Web
        # ),
        data={  # ✅ Custom Data Payload
            "PlaceId": place_id,
            "click_action": "OPEN_ACTIVITY",  # Can be used in mobile app
            "extra_info": "Some other data"
        },
        token=device_token,
        # android=messaging.AndroidConfig(
        #     notification=messaging.AndroidNotification(
        #         image=image_url  # ✅ Image for Android
        #     )
        # ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    mutable_content=True,  # ✅ Enables rich notifications (image support in iOS)
                    alert=messaging.ApsAlert(title=title, body=message)
                )
            ),
            fcm_options=messaging.APNSFCMOptions(
                image=image_url  # ✅ Image for iOS
            )
        )
    )

    response = messaging.send(message)
    print(f"✅ Notification sent: {response}")

# Example Usage
brown_token = "f3tZNVZ80URYvzMB2Wzs7I:APA91bF_JwZv8yhwla2g_MNNJBW-IbZbC6SBscIpbRRhgW0evcceMkgYKo9Umrp31Y7FOZYcuRRnQPTAbcF5Xyy57JhzwriCTXpqEwOLtj4XoFrH1odqVm4"
send_push_notification_with_data(
    brown_token, 
    "Hello!", 
    "This is a test notification.", 
    "https://tikuntechwebimages.blob.core.windows.net/tikunimages/im.jpg",
    "dd59d78d-f602-47a2-b21d-08dd0ecffaa7"
)
