import firebase_admin
from firebase_admin import credentials, firestore

# Initialize AlumniConnect Firebase Project
admin_portal_cred = credentials.Certificate('firebase/alumniconnect-adminsdk.json')
admin_portal_app = firebase_admin.initialize_app(admin_portal_cred, name='AlumniConnect')
admin_portal_db = firestore.client(admin_portal_app)

# Initialize ConnectPlatform Firebase Project
student_portal_cred = credentials.Certificate('firebase/connectplatform-b89b4-firebase-adminsdk-1xnin-bdf0e2e35f.json')
student_portal_app = firebase_admin.initialize_app(student_portal_cred, name='ConnectPlatform')
student_portal_db = firestore.client(student_portal_app)
