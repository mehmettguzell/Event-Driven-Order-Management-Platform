from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


from orders.common.jwt_auth import StatelessJWTAuthentication
from orders.common.responses import error_response, success_response
from orders.exceptions import OrderNotFound
from orders.models import Order
from orders.common.order_detail_cache import get as get_detail_cache, set as set_detail_cache
from orders.selectors import get_all_orders_by_user_id, get_order_by_id


from .serializers import OrderDetailSerializer

class OrderPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        data = request.data
        # TODO: 3. validate payload, create order, publish event
        return Response(
            success_response(data=None),
            status=status.HTTP_201_CREATED,
        )


class OrderView(APIView):
    pagination_class = OrderPagination

    ### TODO: 2. Bu methodu temizle 
    permission_classes = [IsAuthenticated]

    def get(
        self,
        request: Request,
        order_id: str | None = None,

    ) -> Response:
        
        if order_id:
            cached = get_detail_cache(order_id)
            if cached:
                return Response(
                    success_response(data=cached),
                    status=status.HTTP_200_OK
                )
            order = get_order_by_id(order_id)
            if not order:
                raise OrderNotFound()
            data = OrderDetailSerializer(order).data
            set_detail_cache(order_id, data)
            return Response(
                    success_response(data=data),
                    status=status.HTTP_200_OK
                )

        ### TODO: 1. GET USERS ORDER da kaldım burada pagination uygulayacağım yine 
        user_id = (request.query_params.get("user_id") or "").strip() or None
        orders_qs = get_all_orders_by_user_id(user_id)
        paginator = self.pagination_class()
        

        return Response(
            success_response(data=[]),
            status=status.HTTP_200_OK,
        )
