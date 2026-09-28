from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Transaction
from transactions.selectors import get_transaction, list_transactions


class TransactionDetailApi(APIView):
    permission_classes = (IsAuthenticated,)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def get(self, request, transaction_id):
        transaction = get_transaction(user=request.user, transaction_id=transaction_id)

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
