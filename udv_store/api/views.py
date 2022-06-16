from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
import io

from .models import Activity, UcoinRequest, Present, BalanceHistory, UserInfo
from django.contrib.auth.models import User
from .serializer import UserInfoSerializer, MyTokenObtainPairSerializer, PublicUserInfoSerializer, \
    ActivityListSerializer, UcoinRequestSerializer, ProductsSerializer, OrderSerializer, \
    UcoinRequestListSerializer, OrderListSerializer, PresentSerializer, \
    CustomOrdersSerializer, CustomUcoinsRequestsSerializer, BalanceHistorySerializer, \
    ActivitySerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    return Response(UserInfoSerializer(user.userinfo, many=False).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_requests_latest(request):
    user = request.user

    return Response([
        request.get_info_to_list() for request in user.ucoinrequest_set.all()[:3]
    ])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_requests_full(request):
    user = request.user
    return Response([
        request.get_info_to_list() for request in user.ucoinrequest_set.all()
    ])


@api_view(["GET"])
def get_activities(request):
    return Response(ActivityListSerializer(Activity.objects.all(), many=True).data)


@api_view(["GET", 'POST'])
def manage_activities_admin(request):
    if request.method == "GET":
        activities = Activity.objects.all()
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ActivitySerializer(data=request.data, many=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


@api_view(["GET", "POST", "DELETE"])
def manage_activity_by_pk(request, pk):
    activity = Activity.objects.get(activity_id=pk)

    if request.method == "GET":
        return Response(ActivitySerializer(activity, many=False).data)

    if request.method == "POST":
        pass

    if request.method == "DELETE":
        activity.delete()
        return Response(status=200)


@api_view(["POST"])
def create_request(request):
    serializer = UcoinRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


class BalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        return Response({"balance": request.user.userinfo.balance})


@api_view(["GET"])
def get_requests(request):
    serializer = CustomUcoinsRequestsSerializer(
        [item.get_full_data() for item in UcoinRequest.objects.filter(state="IR")],
        many=True
    )
    return Response(serializer.data)


@api_view(["POST", "DELETE"])
def process_request(request, pk):
    u_request = UcoinRequest.objects.get(request_id=pk)

    if request.method == "POST":
        u_request.set_state_rejected(comment=request.data["rejected_comment"])

    if request.method == "DELETE":
        ucoin_count = u_request.activity_id.ucoins_count
        u_request.user_id.userinfo.change_balance(ucoin_count, "add")
        u_request.set_state_accepted()

        BalanceHistory.objects.create(
            user_id=u_request.user_id,
            action="AD",
            category="RQ",
            category_id=pk,
            ucoin_count=ucoin_count
        )

    return Response({"message": "Successfully!"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_user(request, search_request):
    split_request = search_request.title().split(' ')
    request_length = len(split_request)

    if request_length == 1:
        users = User.objects.filter(
            Q(userinfo__first_name__startswith=search_request) |
            Q(userinfo__last_name__startswith=search_request)
        )[:3]
        if users.exists():
            return Response(
                PublicUserInfoSerializer([user.userinfo for user in users if user != request.user], many=True).data
            )

    if request_length == 2:
        split_request = [*(map(lambda x: x[:6], split_request))]

        q1 = (Q(userinfo__first_name__startswith=split_request[0]) &
              Q(userinfo__last_name__startswith=split_request[1]))

        q2 = (Q(userinfo__first_name__startswith=split_request[1]) &
              Q(userinfo__last_name__startswith=split_request[0]))

        users = User.objects.filter(q1 | q2)
        if users.exists():
            return Response(
                PublicUserInfoSerializer([user.userinfo for user in users if user != request.user], many=True).data
            )

    if request_length > 2:
        return Response({"message": "Too many params, the username consist only of the first name and last name!"})

    return Response({"message": "Nothing found"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_unread_present_count(request):
    return Response({"unread_present_count": request.user.present_set.filter(state="SN").count()})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_unread_present_list(request):
    unread_presents = request.user.present_set.filter(state="SN")

    return Response([present.get_present_info() for present in unread_presents])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_present_list(request):
    presents = request.user.present_set.all()

    return Response([present.get_present_info() for present in presents])


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def manage_present_by_pk(request, pk):
    present = Present.objects.get(id=pk)

    if request.method == "GET":
        return Response(present.get_present_info())

    if request.method == "POST":
        present.set_state_read()
        return Response({"message": "Successfully!"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_present(request):
    request.data["user_from"] = request.user.id

    count = request.data.get("ucoin_count")
    if count is not None:
        request.user.userinfo.change_balance(int(count), "remove")

    serializer = PresentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        # return Response(serializer.data["id"])
        BalanceHistory.objects.create(
            user_id=User.objects.get(id=request.data["user_from"]),
            action="EX",
            category="PR",
            category_id=serializer.data["id"],
            ucoin_count=serializer.data["ucoin_count"]
        )

        BalanceHistory.objects.create(
            user_id=User.objects.get(id=request.data["user_to"]),
            action="AD",
            category="PR",
            category_id=serializer.data["id"],
            ucoin_count=serializer.data["ucoin_count"]
        )

        return Response(status=200)

    return Response(serializer.errors, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_balance_history(request):
    return Response((BalanceHistorySerializer(
        request.user.balancehistory_set.all(), many=True)).data)


@api_view(["POST"])
def create_user(request):
    data = request.data

    username = data["username"]
    user_first_name = data["first_name"]
    user_last_name = data["last_name"]
    user_patronymic = data["patronymic"]

    if len(username) == 0:
        from .utils.table_parser import generate_username

        username = generate_username([user_first_name.lower(), user_last_name[0], user_patronymic[0]])

    new_user = User.objects.create_user(username=username, password="tempPas_" + username)

    UserInfo.objects.create(
        user_id=new_user, first_name=user_first_name,
        last_name=user_last_name, patronymic=user_patronymic
    )

    return Response({"user_id": new_user.id, "user_name": new_user.userinfo.get_full_name(), "username": username})


@api_view(["POST"])
# @parser_classes([MultiPartParser, FormParser])
def create_user_by_table(request):
    # a = request.FILES["table"]
    a = request.data["file"]

    return Response({"message": "Successfully!", "param_a": str(a)})


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_moderator_list(request):
    return Response(PublicUserInfoSerializer(
        [user.userinfo for user in User.objects.filter(userinfo__role="MR")],
        many=True).data)


@api_view(["POST", "DELETE"])
# @permission_classes([IsAuthenticated])
def manage_moderator(request, pk):
    user = User.objects.get(id=pk)

    if request.method == "POST":
        user.userinfo.set_role_moderator()

    if request.method == "DELETE":
        user.userinfo.set_role_employee()

    return Response({"message": "Successfully!"})


@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def create_users_by_table(request):
    from .utils.register_user import register_users

    response = register_users(request.data["delete_users"], request.data["table_name"])
    if type(response) == str:
        return Response(status=200)
    return Response({"error_message": "Some error!"})


class TableUploadAPI(APIView):
    # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        from .utils.table_parser import parse_data_from_file
        from json import loads

        name = request.data["table_name"]
        table_format = name.rsplit(".")[-1]

        response = parse_data_from_file(
            request.data["table"], loads(request.data["table_settings"]), table_format == "csv"
        )

        if type(response) == str:
            return Response({"error_message": response})
        return Response(response)
        # return Response('here!')
