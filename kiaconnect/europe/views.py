from django.contrib.auth.models import Group, User
from django.http import HttpRequest
from rest_framework import permissions, viewsets
from hyundai_kia_connect_api import VehicleManager
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser 
import dataclasses, json

from kiaconnect.europe.serializers import GroupSerializer, UserSerializer



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
def login(request:HttpRequest):
    """
    API to fetch user
    """
    if request.method == "POST":
        post_data = JSONParser().parse(request)
        if not post_data['email'] or not post_data['password'] or not post_data['pin'] or not post_data['vehicle_id']:
            return Response({"error": "Incorrect info passed"}, status=status.HTTP_400_BAD_REQUEST)
        vehicles = KiaVehicleManage.fetchVehicles(KiaVehicleManage,post_data['email'],post_data['password'],post_data['pin'])
        data = {}
        for vehicle in vehicles:
            print(json.dumps(dataclasses.asdict(vehicles[vehicle]), indent=4, sort_keys=True, default=str))
            data[vehicle] = json.loads(json.dumps(dataclasses.asdict(vehicles[vehicle]), default=str))
        return Response({"vehicles":data}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def lock(request:HttpRequest):
    """
    API to lock car
    """
    if request.method == "POST":
        post_data = JSONParser().parse(request)
        if not post_data['email'] or not post_data['password'] or not post_data['pin'] or not post_data['vehicle_id']:
            return Response({"error": "Incorrect info passed"}, status=status.HTTP_400_BAD_REQUEST)
        result = KiaVehicleManage.lockVehicle(KiaVehicleManage,post_data['email'],post_data['password'],post_data['pin'],post_data['vehicle_id'])
        if result:
            return Response( True, status=status.HTTP_200_OK)
        else:
            return Response(False, status=status.HTTP_304_NOT_MODIFIED)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def unlock(request:HttpRequest):
    """
    API to lock car
    """
    if request.method == "POST":
        post_data = JSONParser().parse(request)
        if not post_data['email'] or not post_data['password'] or not post_data['pin'] or not post_data['vehicle_id']:
            return Response({"error": "Incorrect info passed"}, status=status.HTTP_400_BAD_REQUEST)
        result = KiaVehicleManage.unlockVehicle(KiaVehicleManage,post_data['email'],post_data['password'],post_data['pin'],post_data['vehicle_id'])
        if result:
            return Response( True, status=status.HTTP_200_OK)
        else:
            return Response(False, status=status.HTTP_304_NOT_MODIFIED)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


class KiaVehicleManage:
    """
    Kia vehicle manage class
    """
    def __init__(self) -> None:
        self.vm = None
    
    def fetchVehicles(self,username,password,pin) -> dict:
        """
        login user
        """
        self.vm = VehicleManager(region=1, brand=1, username=username, password=password, pin=pin)
        self.vm.check_and_refresh_token()
        self.vm.update_all_vehicles_with_cached_state()
        
        return self.vm.vehicles

    def lockVehicle(self,username,password,pin,vehicleId) -> dict:
        """
        login user
        """
        vehicles = self.fetchVehicles(self,username=username,password=password,pin=pin)
        if vehicles[vehicleId]:
            self.vm.lock(vehicleId)
            return True
        else:
            return False

    def unlockVehicle(self,username,password,pin,vehicleId) -> dict:
        """
        login user
        """
        vehicles = self.fetchVehicles(self,username=username,password=password,pin=pin)
        if vehicles[vehicleId]:
            self.vm.unlock(vehicleId)
            return True
        else:
            return False
