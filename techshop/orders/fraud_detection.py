"""
Fraud Detection Module
Analyzes orders for suspicious patterns to prevent fraud and chargebacks
"""
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from orders.models import WebOrder, PaymentTransaction


class FraudDetector:
    """
    Analyze orders for suspicious patterns
    """
    
    # Thresholds for fraud detection
    HIGH_VALUE_ORDER_THRESHOLD = 50000  # Currency units
    MULTIPLE_ORDERS_THRESHOLD = 3
    NEW_CUSTOMER_ORDER_LIMIT = 3
    
    def __init__(self, request, customer, cart_total):
        self.request = request
        self.customer = customer
        self.cart_total = cart_total
        self.risk_score = 0
        self.red_flags = []
    
    def analyze_order(self):
        """
        Main method to analyze an order for fraud indicators
        Returns: (is_suspicious, risk_level, reason)
        """
        # Check order value
        self._check_order_value()
        
        # Check multiple orders from same customer
        self._check_multiple_orders()
        
        # Check IP address patterns
        self._check_ip_patterns()
        
        # Check shipping/billing address mismatch
        self._check_address_mismatch()
        
        # Check new customer high value orders
        self._check_new_customer_orders()
        
        # Determine overall risk level
        if self.risk_score >= 75:
            return True, 'HIGH', '; '.join(self.red_flags)
        elif self.risk_score >= 40:
            return True, 'MEDIUM', '; '.join(self.red_flags)
        elif self.risk_score >= 20:
            return True, 'LOW', '; '.join(self.red_flags)
        
        return False, 'NONE', 'No suspicious patterns detected'
    
    def _check_order_value(self):
        """Check if order value is unusually high"""
        if self.cart_total >= self.HIGH_VALUE_ORDER_THRESHOLD:
            self.risk_score += 25
            self.red_flags.append(f'High value order: {self.cart_total}')
    
    def _check_multiple_orders(self):
        """Check if same customer has multiple recent orders"""
        recent_orders = WebOrder.objects.filter(
            customer=self.customer,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        if recent_orders >= self.MULTIPLE_ORDERS_THRESHOLD:
            self.risk_score += 30
            self.red_flags.append(f'Multiple orders in 24h: {recent_orders}')
    
    def _check_ip_patterns(self):
        """Check for suspicious IP patterns"""
        ip = self.get_client_ip()
        
        # Check for multiple orders from same IP in last hour
        recent_orders = WebOrder.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).values('customer__user__username').annotate(
            order_count=Count('id')
        )
        
        # Check if this IP has placed multiple orders recently
        if ip:
            # Note: In production, you'd store IP with orders and query properly
            # This is a simplified version
            pass
    
    def _check_address_mismatch(self):
        """Check if shipping and billing addresses differ significantly"""
        # This would require billing address in the order
        # For now, we check if address is incomplete
        pass
    
    def _check_new_customer_orders(self):
        """Check if new customer is placing high value orders"""
        # Check if customer has any previous orders
        previous_orders = WebOrder.objects.filter(customer=self.customer).count()
        
        if previous_orders == 0 and self.cart_total > self.HIGH_VALUE_ORDER_THRESHOLD:
            self.risk_score += 35
            self.red_flags.append('New customer with high-value first order')
    
    def get_client_ip(self):
        """Get client IP address from request"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def flag_order_for_review(order, risk_level, reason):
        """Mark an order for manual review"""
        order.status = 'pending'
        order.notes = f"[FRAUD ALERT - {risk_level}] {reason}"
        order.save()
        
        # Log the fraud detection event
        PaymentTransaction.objects.create(
            order=order,
            transaction_id=f"FRAUD-{order.order_number}",
            payment_method='FLAGged',
            amount=order.total_amount,
            status='flagged'
        )


def check_order_security(request, customer, cart_total):
    """
    Convenience function to check order security
    Returns: (is_safe, risk_info)
    """
    detector = FraudDetector(request, customer, cart_total)
    is_suspicious, risk_level, reason = detector.analyze_order()
    
    return not is_suspicious, {
        'risk_level': risk_level,
        'reason': reason,
        'risk_score': detector.risk_score
    }
