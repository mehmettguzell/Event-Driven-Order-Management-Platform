from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from products.api.serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
)
from products.api.product_list_params import parse_product_list_params
from products.common.responses import success_response, paginated_product_list_data
from products.common.product_list_cache import (
    get_response,
    set_response,
    invalidate as invalidate_list_cache,
)
from products.common.product_detail_cache import get as get_detail_cache, set as set_detail_cache, delete as delete_detail_cache
from products.exceptions import ProductNotFound
from products.selectors import get_all_products, get_product_by_id
from products.services.product_service import create_product, update_product

class ProductPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductView(APIView):
    pagination_class = ProductPagination

    def get(self, request : Request):
        filters = parse_product_list_params(request)
        page = request.query_params.get("page",1)

        cached = get_response(filters, page)
        if cached: 
            return Response(
                success_response(cached),
                status=status.HTTP_200_OK
                )
        
        products_qs = get_all_products(**filters)
        paginator = self.pagination_class()
        paginated = paginator.paginate_queryset(products_qs, request)
        response_data = paginated_product_list_data(
            ProductSerializer(paginated, many=True).data,
            paginator
        )
        set_response(filters, page, response_data)
        return Response(
            success_response(response_data),
            status=status.HTTP_200_OK
        )


class ProductDetailView(APIView):
    def get(self, request, product_id):
        cached = get_detail_cache(product_id)
        if cached:
            return Response(success_response(cached), status=status.HTTP_200_OK)

        product = get_product_by_id(product_id)
        if not product:
            raise ProductNotFound()

        data = ProductSerializer(product).data
        set_detail_cache(product_id, data)
        return Response(success_response(data), status=status.HTTP_200_OK)


class ProductCreateView(APIView):
    def post(self, request: Request):
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = create_product(**serializer.validated_data)
        invalidate_list_cache()
        
        response_serializer = ProductSerializer(product)
        
        return Response(
            success_response(response_serializer.data),
            status=status.HTTP_201_CREATED,
        )


class ProductUpdateView(APIView):
    def put(self, request, product_id):
        serializer = ProductUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = update_product(product_id=product_id, **serializer.validated_data)

        delete_detail_cache(product_id)
        invalidate_list_cache()
        
        response_serializer = ProductSerializer(product)
        
        return Response(
            success_response(response_serializer.data),
            status=status.HTTP_200_OK,
        )

