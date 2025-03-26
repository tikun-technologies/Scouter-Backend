# # import firebase_admin
# # from firebase_admin import credentials, messaging

# # # Load Firebase credentials (Replace with the correct path to your JSON file)
# # cred = credentials.Certificate("config/firebase.json")
# # firebase_admin.initialize_app(cred)

# # dheeraj_token="dNZOBddJ5EaTuoe4DMtR-n:APA91bHrdvC6b3BeuvP1YWRcXSmyQSjGMt_EbT9Iu00Gpa4nzoag33HMBiFS32h2WXiusAQbZKTWp64bODG5E1OIAO2rlsO4vyc5KeLe5Z8z0-ttyfv7G5U"
# # import firebase_admin
# # from firebase_admin import credentials, messaging

# # # Load Firebase credentials
# # # cred = credentials.Certificate("path/to/firebase_credentials.json")
# # # firebase_admin.initialize_app(cred)

# # def send_push_notification_with_data(title, message,device_token, image_url=None, place_id=None):
# #     """Send a push notification with custom data (Supports Android & iOS)"""

# #     message = messaging.Message(
# #         # notification=messaging.Notification(
# #         #     title=title,
# #         #     body=message,
# #         #     image=image_url  # ✅ Image for Android & Web
# #         # ),
# #         data={  # ✅ Custom Data Payload
# #             "PlaceId": place_id,
# #             "click_action": "OPEN_ACTIVITY",  # Can be used in mobile app
# #             "extra_info": "Some other data"
# #         },
# #         token=device_token,
# #         # android=messaging.AndroidConfig(
# #         #     notification=messaging.AndroidNotification(
# #         #         image=image_url  # ✅ Image for Android
# #         #     )
# #         # ),
# #         apns=messaging.APNSConfig(
# #             payload=messaging.APNSPayload(
# #                 aps=messaging.Aps(
# #                     mutable_content=True,  # ✅ Enables rich notifications (image support in iOS)
# #                     alert=messaging.ApsAlert(title=title, body=message)
# #                 )
# #             ),
# #             fcm_options=messaging.APNSFCMOptions(
# #                 image=image_url  # ✅ Image for iOS
# #             )
# #         )
# #     )

# #     response = messaging.send(message)
# #     print(f"✅ Notification sent: {response}")




# # def send_notifications_to_all(title, message,device_tokens, image_url=None, place_id=None):
# #     """
# #     Sends push notifications to all active users in batches of 450.
    
# #     :param title: Notification title
# #     :param message: Notification message
# #     :param image_url: Optional image URL for rich notifications
# #     :param place_id: Optional custom data (e.g., Place ID)
# #     :return: JSON response with success/failure count and batch results
# #     """
# #     try:
# #         batch_size = 450  # ✅ Batch size set to 450 (below FCM limit of 500)
# #         total_sent = 0
# #         total_failed = 0
# #         batch_results = []

# #         # ✅ Send notifications in batches of 450
# #         for i in range(0, len(device_tokens), batch_size):
# #             batch_tokens = device_tokens[i:i + batch_size]
            
# #             message_data = messaging.MulticastMessage(
# #                 notification=messaging.Notification(
# #                     title=title,
# #                     body=message,
# #                     image=image_url if image_url else None
# #                 ),
# #                 tokens=batch_tokens,
# #                 data={"PlaceId": place_id} if place_id else {},
# #             )
# #             print("after messaging ")
# #             response = messaging.send_multicast(message_data)
# #             total_sent += response.success_count
# #             total_failed += response.failure_count
# #             batch_results.append({
# #                 "batch_start": i + 1,
# #                 "batch_end": i + len(batch_tokens),
# #                 "success_count": response.success_count,
# #                 "failure_count": response.failure_count
# #             })
# #         print({
# #             "TotalUsers": len(device_tokens),
# #             "TotalSent": total_sent,
# #             "TotalFailed": total_failed,
# #             "Batches": batch_results
# #         }
# # )
# #         return {
# #             "TotalUsers": len(device_tokens),
# #             "TotalSent": total_sent,
# #             "TotalFailed": total_failed,
# #             "Batches": batch_results
# #         }

# #     except Exception as e:
# #         print("❌ ERROR: ", str(e))  # Print the full error message
# #         import traceback
# #         traceback.print_exc()  # Print full error traceback
# #         return {"success": False, "error": str(e)}
# # # Example Usage
# # brown_token = "f3tZNVZ80URYvzMB2Wzs7I:APA91bF_JwZv8yhwla2g_MNNJBW-IbZbC6SBscIpbRRhgW0evcceMkgYKo9Umrp31Y7FOZYcuRRnQPTAbcF5Xyy57JhzwriCTXpqEwOLtj4XoFrH1odqVm4"
# # send_push_notification_with_data(
# #     "Hello!", 
# #     "This is a test notification.", 
# #     dheeraj_token,
# #     "https://tikuntechwebimages.blob.core.windows.net/tikunimages/im.jpg",
# #     "dd59d78d-f602-47a2-b21d-08dd0ecffaa7"
# # )




# # from config.db_config import USER_DEVICE_COLLECTION

# # USER_DEVICE_COLLECTION.delete_one({"DeviceId":"8D94BC14-CE5D-4C3D-BC7C-DC4EB0294BD6"})

# # from config.db_config import ACTIVITY_COLLECTION


# # ACTIVITY_COLLECTION.update_many({},{"$set": {"ViewCount": 0}})
# import requests
# import csv
# import time
# from urllib.parse import urljoin, urlparse
# from bs4 import BeautifulSoup

# # ✅ Extracted headers from your cURL command
# HEADERS = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Priority": "u=0, i",
#     "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
#     "Sec-Ch-Ua-Mobile": "?0",
#     "Sec-Ch-Ua-Platform": '"Windows"',
#     "Sec-Fetch-Dest": "document",
#     "Sec-Fetch-Mode": "navigate",
#     "Sec-Fetch-Site": "none",
#     "Sec-Fetch-User": "?1",
#     "Upgrade-Insecure-Requests": "1",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
# }

# # ✅ Use your full cookie string here
# COOKIES = {
#     "_je_utm_medium": "direct",
#     "_je_utm_source": "direct",
#     "je_country_code": "IN",
#     "je-currency": "INR",
#     "_je_session": "32aebb742cfb286ad3504e2a3c2dfd92",
#     "_ga": "GA1.1.730095472.1742995135",
#     "cf_clearance": "oVNvSXCz99ZYn6BQvgs_oQal4wrbtf6f.QMCgDk2Pt8-1742996810-1.2.1.1-TjYx1lM0...",
# }

# # ✅ Session for persistent headers & cookies
# session = requests.Session()
# session.headers.update(HEADERS)
# session.cookies.update(COOKIES)

# # ✅ Tracking visited URLs to prevent duplicates
# visited_urls = set()

# # ✅ Output CSV file
# CSV_FILE = "jamesedition_sub_urls.csv"

# # ✅ Create CSV file with headers if it doesn't exist
# with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(["Parent URL", "Sub URL", "Status Code"])


# def get_links(url):
#     """Fetch a webpage and extract all internal links."""
#     try:
#         response = session.get(url, timeout=10)
#         status_code = response.status_code
#         print(f"📡 [Status: {status_code}] {url}")

#         if status_code != 200:
#             return [], status_code  # Return empty if page is blocked

#         soup = BeautifulSoup(response.text, "html.parser")
#         links = set()

#         for a_tag in soup.find_all("a", href=True):
#             full_url = urljoin(url, a_tag["href"])
#             parsed_url = urlparse(full_url)

#             # ✅ Ensure link is internal (same domain)
#             if parsed_url.netloc == urlparse(url).netloc:
#                 links.add(full_url)

#         return list(links), status_code

#     except requests.RequestException as e:
#         print(f"❌ Error fetching {url}: {str(e)}")
#         return [], None


# def crawl(url, depth=3):
#     """Recursively crawl and extract sub-URLs up to a max depth."""
#     if depth == 0 or url in visited_urls:
#         return

#     visited_urls.add(url)
#     links, status_code = get_links(url)

#     # ✅ Save results to CSV
#     with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)
#         for link in links:
#             writer.writerow([url, link, status_code])

#     # ✅ Crawl deeper
#     for link in links:
#         crawl(link, depth - 1)
#         time.sleep(2)  # ✅ Add delay to prevent blocking


# # ✅ Start Crawling
# START_URL = "https://www.jamesedition.com"
# crawl(START_URL, depth=3)

# print(f"\n✅ Crawl Completed! Results saved in {CSV_FILE}")



# ✅ Convert documents to bulk operations (only insert if ActivityId doesn't exist)
# operations = [
#     UpdateOne({"ActivityId": doc["ActivityId"]}, {"$setOnInsert": doc}, upsert=True)
#     for doc in documents
# ]

# # ✅ Execute bulk operation
# if operations:
#     ACTIVITY_COLLECTION.bulk_write(operations)