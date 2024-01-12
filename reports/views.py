# Create your views here.

from rest_framework import generics
from .serializers import InvoiceSerializer
from rest_framework.permissions import IsAuthenticated

from .models import Invoice
import logging

LOG = logging.getLogger(__name__)


class InvoiceListAPIView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_email = self.request.user
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')

        queryset = Invoice.objects.filter(
            user__email=user_email)

        invoices = Invoice.objects.filter(
            user__email=user_email).prefetch_related('invoice_record')

        # Iterate over the invoices and LOG.debug the desired format
        for invoice in invoices:
            LOG.debug(f"Invoice: {invoice}")
            LOG.debug("Invoice Records:")
            for record in invoice.invoice_record.all():
                LOG.debug(record)

     # Filter by start_time if provided
        if start_time:
            queryset = queryset.filter(start_date__gte=start_time)

        # Filter by end_time if provided
        if end_time:
            queryset = queryset.filter(end_date__lte=end_time)

        return queryset
