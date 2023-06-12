from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from users.serializers import SubscriptionUserSerializer
from users.models import Subscriptions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from users.serializers import CustomUserSerializer
from djoser.serializers import UserCreateSerializer

User = get_user_model()


class SubscriptionUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, ]

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return self.serializer_class

    @action(
        detail=False,
        methods=['GET', ],
        url_path='me',
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request, id=None):
        context = {'request': self.request}
        serializer = CustomUserSerializer(request.user, context=context)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['GET', ],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        subscription = User.objects.filter(
            subscription__subscriber=request.user
        )
        page = self.paginate_queryset(subscription)
        # print(User.objects.filter(subscription__subscriber=request.user).query)
        context = {'request': request}
        serializer = SubscriptionUserSerializer(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)
        #return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated, ]
    )
    def subscribe(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        if request.user == user:
            return Response(
                {'errors': 'You can not subscribe/unsubscribe yourself'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription = Subscriptions.objects.filter(
            subscriber=request.user,
            subscription=user
        ).first()
        if request.method == 'DELETE':
            if not subscription:
                return Response(
                    {'errors': 'Subscription does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # try:
            #     subscription = Subscriptions.objects.get(
            #         subscriber=request.user,
            #         subscription=user
            #     )
            # except Subscriptions.DoesNotExist:
            #     return Response(
            #         {'errors': 'Subscription does not exist'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'POST':
            # context = {
            #     'request': request
            # }
            # serializer = SubscriptionUserSerializer(instance=user, data=request.data, context=context)
            # if not serializer.is_valid():
            #     return Response(serializer.errors)
            context = {'request': request}
            serializer = SubscriptionUserSerializer(instance=user, context=context)
            if subscription:
                return Response(
                    {'errors': 'Subscription already exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.create(
                subscriber=request.user,
                subscription=user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )





# class SubscriptionViewSet(APIView):
#     def get(self, request, user_id):
#         return Response({'user_id': user_id})

# class SubscriptionViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = SubscriptionUserSerializer