from django.urls import path

from transactions.apis import TransactionDetailApi, TransactionListApi

urlpatterns = [
    path("", TransactionListApi.as_view(), name="list"),
    path("<uuid:transaction_id>/", TransactionDetailApi.as_view(), name="detail"),
]
