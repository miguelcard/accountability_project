
from django.http.response import HttpResponse, JsonResponse
import json
from rest_framework.views import APIView

# Assumes user with ID 15 exists
# Theoretical url: api/v1/users/15
class UserDetailView(APIView):
    def get(self, request):
        data = """{
        "id": 15,
        "username": "test17",
        "name": null,
        "last_name": null,
        "email": "test17@gmail.com",
        "profile_photo": null,
        "birthdate": null,
        "gender": null,
        "age": null,
        "tags": [],
        "languages": [],
        "about": null,
        "score_board": 2,
        "is_active": true,
        "is_superuser": false,
        "habits": [3, 4],
        "spaces": [6, 7]
        }"""

        parsed_data = json.loads(data)
        dump = json.dumps(parsed_data)
        return HttpResponse(dump, content_type='application/json')

# Theoretical url: api/v1/habits/3
class HabitDetailView(APIView):
    def get(self, request):
        data =  """{
        "id": 3,
        "owner": 15,
        "tags": [
        {
            "id": 2,
            "name": "Morning Routine"
        },
        {
            "id": 3,
            "name": "Reading"
        }
        ],
        "spaces": [6],
        "name": "Read 30 minutes",
        "description": "I want to read 30 minutes everyday in the morning after waking up",
        "checkmarks": [ 1, 2, 3, 5, 9]
        }"""

        parsed_data = json.loads(data)
        dump = json.dumps(parsed_data)
        return HttpResponse(dump, content_type='application/json')

# Theoretical url: api/v1/habits/3/checkmarks
class CheckMarksView(APIView):

    """[
    {
        "id": 1,
        "date": ,
        "status": "done"
    },
    {
        "id": 2,
        "date": ,
        "status": "not_done"
    },
    {
        "id": 3,
        "date": ,
        "status": "not_planned"
    },
    {
        "id": 5,
        "date": ,
        "status": "done"
    },
    {
        "id": 9,
        "date": ,
        "status": "done"
    }
    ]"""

# Ask Santi: Do we need a detailed checkmark view?: api/v1/habits/3/checkmarks/1
# would return:
#     {
#         "id": 1,
#         "date": ,
#         "status": "done"
#     }

# Theoretical url: api/v1/spaces/6
class SpaceDetailView(APIView):
    def get(self, request):
        data =  """{
        "id": 6,
        "owner": 15,
        "members": [15, 1, 2], 
        "name": "Los Mañaneros",
        "description": "en este espacio compartimos nuestros habitos con quienes nos levantamos temprano para mantenernos responsables entre nosotros",
        "tags": [
        {
            "id": 2,
            "name": "Morning Routine"
        }
        ]
        }"""

        parsed_data = json.loads(data)
        dump = json.dumps(parsed_data)
        return HttpResponse(dump, content_type='application/json')
