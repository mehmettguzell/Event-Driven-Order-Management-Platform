from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from rest_framework.request import Request
from payments.api.serializers import PaymentSerializer
from payments.models import Payment


class PaymentByOrderView(APIView):
    """
    GET /payments/order/<order_id>/
    Sipariş oluşturulunca OrderCreated event'i payment-consumer tarafından dinlenir,
    Payment kaydı oluşturulur (SUCCESS veya FAILED). Bu endpoint ile o siparişin
    ödeme durumunu kontrol edebilirsin.
    """
    permission_class = [IsAuthenticated]

    def get(self, request:Request, order_id:str) -> Response:

        payment = Payment.objects.filter(order_id=order_id).order_by("-created_at").first()
        if not payment:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Bu sipariş için henüz ödeme kaydı yok. OrderCreated event'i payment-service'e ulaşmamış olabilir.",
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": PaymentSerializer(payment).data},
            status=status.HTTP_200_OK,
        )


class PaymentListView(APIView):
    """GET /payments/ — Tüm ödemeleri listele (debug / kontrol için)."""
    permission_class = [IsAuthenticated]

    def get(self, request):
        order_id = request.query_params.get("order_id")
        qs = Payment.objects.all().order_by("-created_at")
        if order_id:
            qs = qs.filter(order_id=order_id)
        serializer = PaymentSerializer(qs[:50], many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
