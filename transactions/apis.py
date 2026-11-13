from decimal import Decimal

from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.choices import MovementType, PaymentMethod
from transactions.models import Transaction
from transactions.selectors import get_transaction, list_transactions
from transactions.services import create_transaction


class TransactionCreateApi(APIView):
    permission_classes = (IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=150)
        description = serializers.CharField(
            required=False, allow_null=True, allow_blank=True
        )
        amount = serializers.DecimalField(
            max_digits=12, decimal_places=2, min_value=Decimal("0.01")
        )
        movement_type = serializers.ChoiceField(choices=MovementType.choices)
        payment_method = serializers.ChoiceField(choices=PaymentMethod.choices)
        category_id = serializers.UUIDField()
        credit_card_id = serializers.UUIDField(required=False, allow_null=True)
        subscription_id = serializers.UUIDField(required=False, allow_null=True)
        transaction_date = serializers.DateField()

    serializer_class = InputSerializer

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction = create_transaction(user=request.user, **serializer.validated_data)

        data = self.OutputSerializer(transaction).data

        return Response(data, status=status.HTTP_201_CREATED)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class TransactionDetailApi(APIView):
    permission_classes = (IsAuthenticated,)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def get(self, request, transaction_id):
        try:
            transaction = get_transaction(
                user=request.user, transaction_id=transaction_id
            )
        except ValidationError as exc:
            raise Http404("Transaction not found.") from exc

        data = self.OutputSerializer(transaction).data
        return Response(data)


class TransactionListApi(APIView):
    permission_classes = (IsAuthenticated,)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Transaction
            fields = (
                "id",
                "name",
                "amount",
            )

    def get(self, request):
        transactions = list_transactions(user=request.user)

        data = self.OutputSerializer(transactions, many=True).data

        return Response(data)
