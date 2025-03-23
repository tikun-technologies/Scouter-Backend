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

def send_push_notification_with_data(title, message,device_token, image_url=None, place_id=None):
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




def send_notifications_to_all(title, message,device_tokens, image_url=None, place_id=None):
    """
    Sends push notifications to all active users in batches of 450.
    
    :param title: Notification title
    :param message: Notification message
    :param image_url: Optional image URL for rich notifications
    :param place_id: Optional custom data (e.g., Place ID)
    :return: JSON response with success/failure count and batch results
    """
    try:
        batch_size = 450  # ✅ Batch size set to 450 (below FCM limit of 500)
        total_sent = 0
        total_failed = 0
        batch_results = []

        # ✅ Send notifications in batches of 450
        for i in range(0, len(device_tokens), batch_size):
            batch_tokens = device_tokens[i:i + batch_size]
            
            message_data = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                    image=image_url if image_url else None
                ),
                tokens=batch_tokens,
                data={"PlaceId": place_id} if place_id else {},
            )
            print("after messaging ")
            response = messaging.send_multicast(message_data)
            total_sent += response.success_count
            total_failed += response.failure_count
            batch_results.append({
                "batch_start": i + 1,
                "batch_end": i + len(batch_tokens),
                "success_count": response.success_count,
                "failure_count": response.failure_count
            })
        print({
            "TotalUsers": len(device_tokens),
            "TotalSent": total_sent,
            "TotalFailed": total_failed,
            "Batches": batch_results
        }
)
        return {
            "TotalUsers": len(device_tokens),
            "TotalSent": total_sent,
            "TotalFailed": total_failed,
            "Batches": batch_results
        }

    except Exception as e:
        print("❌ ERROR: ", str(e))  # Print the full error message
        import traceback
        traceback.print_exc()  # Print full error traceback
        return {"success": False, "error": str(e)}
# Example Usage
brown_token = "f3tZNVZ80URYvzMB2Wzs7I:APA91bF_JwZv8yhwla2g_MNNJBW-IbZbC6SBscIpbRRhgW0evcceMkgYKo9Umrp31Y7FOZYcuRRnQPTAbcF5Xyy57JhzwriCTXpqEwOLtj4XoFrH1odqVm4"
send_push_notification_with_data(
    "Hello!", 
    "This is a test notification.", 
    dheeraj_token,
    "https://tikuntechwebimages.blob.core.windows.net/tikunimages/im.jpg",
    "dd59d78d-f602-47a2-b21d-08dd0ecffaa7"
)




# from config.db_config import USER_DEVICE_COLLECTION

# USER_DEVICE_COLLECTION.delete_one({"DeviceId":"8D94BC14-CE5D-4C3D-BC7C-DC4EB0294BD6"})
