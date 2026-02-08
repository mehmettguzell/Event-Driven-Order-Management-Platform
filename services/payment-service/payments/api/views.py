from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from rest_framework.request import Request
from payments.common.responses import success_response
from payments.services.payment_service import get_order_payments_by_order_id, get_payment_service


class PaymentByOrderView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request:Request, order_id:str) -> Response:
        payment = get_payment_service(order_id)
        return Response(success_response(data=payment), status=status.HTTP_200_OK)


class PaymentListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request:Request) -> Response: 
        order_id = request.query_params.get("order_id")
        serializer = get_order_payments_by_order_id(order_id)
        return Response(success_response(serializer.data), status=status.HTTP_200_OK)