from django.apps import AppConfig


class FirebaseConfig(AppConfig):
    name = "firebase"
    verbose_name = "Firebase Integration"

    def ready(self):
        from firebase.firebase_init import initialize_firebase
        initialize_firebase()
