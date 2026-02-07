from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


from orders.common.responses import error_response, success_response
from orders.exceptions import OrderNotFound
from orders.services.order_service import (
    create_order as service_create_order,
    get_order_detail as service_get_order_detail,
    get_user_orders as service_get_user_orders,
)

from .serializers import CreateOrderSerializer


class OrderPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = str(request.user.id)
        data = service_create_order(user_id, serializer.validated_data)
        
        return Response(success_response(data), status=status.HTTP_201_CREATED)


class OrderView(APIView):
    pagination_class = OrderPagination
    permission_classes = [IsAuthenticated]


    def get(self, request: Request, order_id: str | None = None) -> Response:
        if order_id:
            return self._get_detail(order_id)
        return self._get_list(request)


    def _get_detail(self, order_id: str) -> Response:
        try:
            data = service_get_order_detail(str(order_id))
            return Response(success_response(data), status=status.HTTP_200_OK)
        except OrderNotFound as e:
            return Response(error_response(e.code, e.message), status=e.status_code)


    def _get_list(self, request: Request) -> Response:
        user_id = str(request.user.id)
        data = service_get_user_orders(user_id, request, self.pagination_class)
        return Response(success_response(data), status=status.HTTP_200_OK)
