from django.urls import path

from transactions.apis import (
    TransactionCreateApi,
    TransactionDetailApi,
    TransactionListApi,
)

urlpatterns = [
    path("", TransactionListApi.as_view(), name="transaction-list"),
    path(
        "create-transaction/", TransactionCreateApi.as_view(), name="transaction-create"
    ),
    path(
        "<uuid:transaction_id>/",
        TransactionDetailApi.as_view(),
        name="transaction-detail",
    ),
]
