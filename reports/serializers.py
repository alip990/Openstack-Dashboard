from rest_framework import serializers
from .models import Invoice, InvoiceRecord

class InvoiceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceRecord
        fields = ('id', 'name', 'description', 'usage', 'record_type', 'unit_price')

class InvoiceSerializer(serializers.ModelSerializer):
    invoice_record = InvoiceRecordSerializer(many=True, read_only=True)
    is_paid = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ('id', 'user', 'start_date', 'end_date', 'total_amount', 'invoice_record', 'is_paid')

    def get_is_paid(self, obj):
        # This method will be used to determine the value of the is_paid field
        return False
