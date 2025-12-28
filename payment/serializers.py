from rest_framework import serializers
from payment.models import Payment
from uuid import uuid4


class PaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Payment
        fields='__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
        read_only_fields = ('status', 'amount', 'invoice_id', 'payment_date', 'payment_url')

    def create(self, validated_data):
        user = validated_data.get('user')
        course = validated_data.get('course')

        validated_data['amount'] = course.price
        validated_data['invoice_id'] = str(uuid4())[:8]

        return super().create(validated_data)
