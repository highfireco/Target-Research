import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyDRf9tWUNAJ4rSN7NbjN58NW-DkDldJs_E",
    "authDomain": "target-research-183e0.firebaseapp.com",
    "projectId": "target-research-183e0",
    "storageBucket": "target-research-183e0.firebasestorage.app",
    "messagingSenderId": "620151660988",
    "appId": "1:620151660988:web:77b9ef782db820cf484bb9",
    "databaseURL": "https://target-research-183e0-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()