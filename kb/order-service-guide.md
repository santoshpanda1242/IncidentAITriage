# Order Service Troubleshooting Guide

## Overview
This guide covers order service issues including inventory management, payment processing integration, shipping service problems, and order fulfillment failures.

## Common Order Service Issues

### 1. Inventory Service Unavailability During Order Creation

**Symptoms:**
- Order creation failures (ERR-6001)
- "Out of stock" errors for available items
- Inventory check timeouts

**Root Causes:**
- Inventory service downtime or overload
- Network connectivity issues
- Database lock contention
- Insufficient inventory service resources

**Solutions:**

#### Immediate Actions:
1. **Check Inventory Service Status**
   ```python
   import requests
   
   def check_inventory_service_health():
       try:
           response = requests.get('http://inventory-service/health', timeout=5)
           return response.status_code == 200
       except requests.exceptions.RequestException:
           return False
   ```

2. **Implement Inventory Circuit Breaker**
   ```python
   from circuitbreaker import circuit
   
   @circuit(failure_threshold=5, recovery_timeout=60)
   def check_inventory(item_id, quantity):
       response = requests.get(f'http://inventory-service/check/{item_id}/{quantity}')
       return response.json()
   
   def create_order_with_fallback(order_data):
       try:
           inventory_status = check_inventory(order_data['item_id'], order_data['quantity'])
           if inventory_status['available']:
               return process_order(order_data)
       except CircuitBreakerError:
           # Fallback: allow order with manual review
           return create_order_pending_review(order_data)
   ```

3. **Add Inventory Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_cached_inventory(item_id):
       # Cache inventory data for short period
       cached_data = cache.get(f"inventory_{item_id}")
       if cached_data:
           return cached_data
       # Fetch from service
       inventory_data = fetch_inventory_from_service(item_id)
       cache.set(f"inventory_{item_id}", inventory_data, ttl=60)  # 1 minute cache
       return inventory_data
   ```

#### Long-term Solutions:
- Implement inventory service clustering
- Add inventory data replication
- Use message queue for inventory updates
- Implement inventory reservation system

### 2. Payment Callback Processing Failures

**Symptoms:**
- Payment callback handling errors (ERR-6003)
- Order status inconsistencies
- Payment reconciliation issues

**Root Causes:**
- Payment gateway webhook failures
- Network connectivity issues
- Invalid payment callback data
- Database transaction failures

**Solutions:**

#### Immediate Actions:
1. **Implement Payment Callback Queue**
   ```python
   import celery
   
   @celery.task(bind=True, max_retries=3)
   def process_payment_callback(self, callback_data):
       try:
           # Process payment callback
           order_id = callback_data['order_id']
           payment_status = callback_data['status']
           
           # Update order status
           update_order_status(order_id, payment_status)
           
       except Exception as exc:
           # Retry with exponential backoff
           raise self.retry(exc=exc, countdown=2 ** self.request.retries)
   ```

2. **Add Callback Validation**
   ```python
   def validate_payment_callback(callback_data):
       required_fields = ['order_id', 'payment_id', 'status', 'amount', 'signature']
       
       # Check required fields
       if not all(field in callback_data for field in required_fields):
           raise ValidationError("Missing required fields")
       
       # Verify signature
       expected_signature = generate_signature(callback_data)
       if callback_data['signature'] != expected_signature:
           raise SecurityError("Invalid callback signature")
       
       return True
   ```

3. **Implement Idempotent Callback Processing**
   ```python
   def process_callback_idempotently(callback_data):
       order_id = callback_data['order_id']
       payment_id = callback_data['payment_id']
       
       # Check if already processed
       if is_callback_processed(payment_id):
           return {"status": "already_processed", "order_id": order_id}
       
       # Process callback
       result = process_payment_callback(callback_data)
       
       # Mark as processed
       mark_callback_processed(payment_id)
       
       return result
   ```

#### Long-term Solutions:
- Implement payment callback retry mechanism
- Add payment reconciliation batch jobs
- Use webhook signature verification
- Implement payment status polling as fallback

### 3. Order Processing Pipeline Timeout

**Symptoms:**
- Order processing timeouts (ERR-6002)
- Orders stuck in processing state
- Increased order processing time

**Root Causes:**
- Long-running order processing steps
- Insufficient worker resources
- Database performance issues
- External service dependencies

**Solutions:**

#### Immediate Actions:
1. **Implement Pipeline Timeout Handling**
   ```python
   import signal
   from contextlib import contextmanager
   
   @contextmanager
   def timeout(seconds):
       def timeout_handler(signum, frame):
           raise TimeoutError("Pipeline timeout")
       
       signal.signal(signal.SIGALRM, timeout_handler)
       signal.alarm(seconds)
       try:
           yield
       finally:
           signal.alarm(0)
   
   def process_order_with_timeout(order_data, timeout_seconds=30):
       try:
           with timeout(timeout_seconds):
               return process_order_pipeline(order_data)
       except TimeoutError:
           # Move to manual processing queue
           return queue_for_manual_processing(order_data)
   ```

2. **Add Pipeline Step Monitoring**
   ```python
   import time
   
   def process_order_pipeline(order_data):
       start_time = time.time()
       steps = ['validate', 'inventory', 'payment', 'fulfillment']
       
       for step in steps:
           step_start = time.time()
           try:
               execute_step(step, order_data)
               step_duration = time.time() - step_start
               log_step_timing(step, step_duration)
               
               # Alert on slow steps
               if step_duration > 5:  # 5 second threshold
                   alert_slow_step(step, step_duration)
                   
           except Exception as e:
               handle_step_failure(step, order_data, e)
               break
   ```

3. **Implement Pipeline Parallelization**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def process_order_parallel(order_data):
       with ThreadPoolExecutor(max_workers=4) as executor:
           # Run independent steps in parallel
           futures = {
               executor.submit(validate_order, order_data): 'validate',
               executor.submit(check_inventory, order_data): 'inventory',
               executor.submit(check_fraud, order_data): 'fraud'
           }
           
           results = {}
           for future in concurrent.futures.as_completed(futures):
               step = futures[future]
               try:
                   results[step] = future.result()
               except Exception as e:
                   results[step] = {'error': str(e)}
           
           # Continue with dependent steps
           if all('error' not in result for result in results.values()):
               return process_payment(results, order_data)
   ```

#### Long-term Solutions:
- Implement order processing workflow engine
- Add horizontal scaling for order processing workers
- Use message queues for pipeline steps
- Implement order processing SLA monitoring

### 4. Shipping Service Integration Timeout

**Symptoms:**
- Shipping rate calculation failures (ERR-6004)
- Order fulfillment delays
- Shipping method unavailability

**Root Causes:**
- Shipping service downtime
- API rate limiting
- Network connectivity issues
- Invalid shipping addresses

**Solutions:**

#### Immediate Actions:
1. **Implement Shipping Service Circuit Breaker**
   ```python
   from circuitbreaker import circuit
   
   @circuit(failure_threshold=3, recovery_timeout=30)
   def get_shipping_rates(order_data):
       response = requests.post(
           'http://shipping-service/rates',
           json=order_data,
           timeout=10
       )
       return response.json()
   
   def get_shipping_rates_with_fallback(order_data):
       try:
           return get_shipping_rates(order_data)
       except CircuitBreakerError:
           # Fallback to standard rates
           return get_standard_shipping_rates(order_data)
   ```

2. **Add Shipping Rate Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=500)
   def get_cached_shipping_rates(zip_code, weight):
       cache_key = f"shipping_rates_{zip_code}_{weight}"
       cached_rates = cache.get(cache_key)
       if cached_rates:
           return cached_rates
       
       # Fetch from service
       rates = fetch_shipping_rates(zip_code, weight)
       cache.set(cache_key, rates, ttl=3600)  # 1 hour cache
       return rates
   ```

3. **Implement Multiple Shipping Providers**
   ```python
   shipping_providers = ['fedex', 'ups', 'dhl', 'usps']
   
   def get_best_shipping_rate(order_data):
       rates = []
       for provider in shipping_providers:
           try:
               provider_rates = get_provider_rates(provider, order_data)
               rates.extend(provider_rates)
           except ShippingError:
               continue
       
       if not rates:
           raise ShippingError("No shipping providers available")
       
       # Sort by cost and delivery time
       return sorted(rates, key=lambda x: (x['cost'], x['delivery_days']))[0]
   ```

#### Long-term Solutions:
- Implement shipping service clustering
- Add shipping provider health monitoring
- Use shipping API rate limiting
- Implement local shipping rate calculation as fallback

## Order Monitoring and Analytics

### Key Metrics to Monitor:
- Order creation success rate
- Average order processing time
- Inventory check success rate
- Payment callback processing time
- Shipping rate calculation success rate

### Alert Thresholds:
- Order success rate < 95%
- Average processing time > 30 seconds
- Inventory check failure rate > 5%
- Payment callback failure rate > 2%

## Order Recovery Procedures

### Stuck Order Recovery

**Steps:**
1. **Identify Stuck Orders**
   ```sql
   SELECT * FROM orders 
   WHERE status = 'processing' 
   AND created_at < DATE_SUB(NOW(), INTERVAL 1 HOUR);
   ```

2. **Manual Order Review**
   - Check payment status with payment provider
   - Verify inventory availability
   - Review shipping requirements

3. **Order Status Correction**
   ```python
   def recover_stuck_order(order_id):
       order = get_order(order_id)
       
       # Check payment status
       payment_status = check_payment_with_provider(order['payment_id'])
       
       # Update order status based on payment
       if payment_status == 'completed':
           update_order_status(order_id, 'confirmed')
           trigger_fulfillment(order_id)
       elif payment_status == 'failed':
           update_order_status(order_id, 'payment_failed')
           notify_customer(order_id, 'payment_failed')
       else:
           update_order_status(order_id, 'manual_review')
   ```

## Related Documentation
- [Payment Integration Guide](../payment/payment-integration.md)
- [Inventory Management System](../inventory/inventory-guide.md)
- [Shipping API Documentation](../shipping/shipping-api.md)
- [Order Processing SLA](../sla/order-processing-sla.md)