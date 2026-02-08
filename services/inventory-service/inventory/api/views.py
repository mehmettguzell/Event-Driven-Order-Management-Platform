from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.api.serializers import (
    CreateInventorySerializer,
    UpdateInventorySerializer,
)
from inventory.common.responses import success_response
from inventory.services.inventory_service import (
    create_or_update_inventory,
    get_inventory_detail_by_product_id,
    list_all_inventories,
    update_inventory_quantity,
)


class InventoryListCreateView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        data = list_all_inventories()
        return Response(
            success_response(data),
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = CreateInventorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data, created = create_or_update_inventory(serializer.validated_data)
        return Response(
            success_response(data),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class InventoryDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, product_id) -> Response:
        data = get_inventory_detail_by_product_id(product_id)
        return Response(
            success_response(data),
            status=status.HTTP_200_OK,
        )

    def put(self, request: Request, product_id) -> Response:
        serializer = UpdateInventorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = update_inventory_quantity(product_id, serializer.validated_data)
        return Response(
            success_response(data),
            status=status.HTTP_200_OK,
        )
