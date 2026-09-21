# Integration Service Troubleshooting Guide

## Overview
This guide covers integration service issues including external API client problems, data transformation failures, webhook handling, and rate limiting challenges.

## Common Integration Issues

### 1. External API Client Authentication Token Expired

**Symptoms:**
- API authentication errors (ERR-18001)
- External service integration failures
- Token refresh failures

**Root Causes:**
- Expired OAuth tokens
- Invalid API credentials
- Token refresh mechanism failures
- Authentication provider issues

**Solutions:**

#### Immediate Actions:
1. **Implement Token Refresh Logic**
   ```python
   import requests
   from datetime import datetime, timedelta
   
   class APIClient:
       def __init__(self, client_id, client_secret):
           self.client_id = client_id
           self.client_secret = client_secret
           self.access_token = None
           self.token_expiry = None
       
       def get_valid_token(self):
           # Check if token exists and is valid
           if self.access_token and self.token_expiry > datetime.now():
               return self.access_token
           
           # Refresh token
           return self.refresh_token()
       
       def refresh_token(self):
           token_url = "https://api.provider.com/oauth/token"
           
           response = requests.post(token_url, data={
               'grant_type': 'client_credentials',
               'client_id': self.client_id,
               'client_secret': self.client_secret
           })
           
           if response.status_code == 200:
               token_data = response.json()
               self.access_token = token_data['access_token']
               self.token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'])
               return self.access_token
           else:
               raise AuthenticationError("Token refresh failed")
   ```

2. **Add Token Health Monitoring**
   ```python
   def monitor_token_health():
       while True:
           try:
               # Test token validity
               test_api_call()
           except AuthenticationError:
               send_alert("API token expired or invalid")
               attempt_token_refresh()
           
           time.sleep(300)  # Check every 5 minutes
   ```

3. **Implement Token Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=10)
   def get_cached_token(client_id):
       cache_key = f"api_token_{client_id}"
       cached_token = cache.get(cache_key)
       
       if cached_token and not is_token_expired(cached_token):
           return cached_token
       
       # Fetch new token
       new_token = fetch_new_token(client_id)
       cache.set(cache_key, new_token, ttl=3600)  # 1 hour cache
       return new_token
   ```

#### Long-term Solutions:
- Implement OAuth 2.0 with refresh tokens
- Add token management service
- Use token encryption and secure storage
- Implement token rotation policies

### 2. Data Transformation Pipeline Failed

**Symptoms:**
- Data transformation errors (ERR-18002)
- Integration data inconsistencies
- Mapping failures

**Root Causes:**
- Invalid input data formats
- Complex transformation logic
- Schema mismatches
- Transformation service overload

**Solutions:**

#### Immediate Actions:
1. **Add Data Validation**
   ```python
   from jsonschema import validate, ValidationError
   
   def validate_input_data(data, schema):
       try:
           validate(instance=data, schema=schema)
           return True
       except ValidationError as e:
           log.error(f"Data validation failed: {e.message}")
           return False
   ```

2. **Implement Robust Transformation Pipeline**
   ```python
   def transform_data_with_validation(input_data, transformation_rules):
       try:
           # Validate input
           if not validate_input_data(input_data, get_input_schema()):
               raise DataValidationError("Invalid input data")
           
           # Apply transformations
           transformed_data = apply_transformations(input_data, transformation_rules)
           
           # Validate output
           if not validate_input_data(transformed_data, get_output_schema()):
               raise DataValidationError("Invalid transformed data")
           
           return transformed_data
           
       except Exception as e:
           log.error(f"Transformation failed: {e}")
           # Store failed transformation for analysis
           store_failed_transformation(input_data, str(e))
           raise
   ```

3. **Add Transformation Fallback**
   ```python
   def transform_with_fallback(input_data):
       transformation_strategies = [
           'full_transformation',
           'partial_transformation', 
           'minimal_transformation'
       ]
       
       for strategy in transformation_strategies:
           try:
               return apply_transformation_strategy(input_data, strategy)
           except TransformationError:
               continue
       
       # Ultimate fallback: return raw data
       return {'raw_data': input_data, 'transformation_failed': True}
   ```

#### Long-term Solutions:
- Implement data transformation engine
- Add transformation testing framework
- Use schema registry for validation
- Implement transformation analytics

### 3. Webhook Signature Validation Failed

**Symptoms:**
- Webhook validation errors (ERR-18003)
- Integration security failures
- Webhook rejection

**Root Causes:**
- Invalid webhook signatures
- Clock synchronization issues
- Secret key mismatches
- Signature algorithm changes

**Solutions:**

#### Immediate Actions:
1. **Implement Robust Signature Validation**
   ```python
   import hmac
   import hashlib
   
   def validate_webhook_signature(payload, signature, secret):
       # Calculate expected signature
       expected_signature = hmac.new(
           secret.encode('utf-8'),
           payload.encode('utf-8'),
           hashlib.sha256
       ).hexdigest()
       
       # Compare signatures securely
       return hmac.compare_digest(expected_signature, signature)
   ```

2. **Add Clock Skew Tolerance**
   ```python
   from datetime import datetime, timedelta
   
   def validate_webhook_timestamp(timestamp, max_skew_seconds=300):
       webhook_time = datetime.fromtimestamp(timestamp)
       current_time = datetime.now()
       time_diff = abs((current_time - webhook_time).total_seconds())
       
       if time_diff > max_skew_seconds:
           raise SecurityError(f"Webhook timestamp skew too large: {time_diff}s")
       
       return True
   ```

3. **Implement Webhook Replay Protection**
   ```python
   def check_webhook_replay(webhook_id):
       cache_key = f"webhook_processed_{webhook_id}"
       
       if cache.get(cache_key):
           raise SecurityError("Webhook already processed - possible replay attack")
       
       # Mark as processed
       cache.set(cache_key, True, ttl=3600)  # 1 hour
       return True
   ```

#### Long-term Solutions:
- Implement webhook signature rotation
- Add webhook analytics and monitoring
- Use standardized webhook security
- Implement webhook delivery guarantees

### 4. Bulk Data Sync Job Failed Due to API Rate Limiting

**Symptoms:**
- Bulk sync failures (ERR-18004)
- API rate limiting errors
- Incomplete data synchronization

**Root Causes:**
- Exceeding API rate limits
- Inefficient batch processing
- Lack of rate limiting implementation
- Large data volumes

**Solutions:**

#### Immediate Actions:
1. **Implement Adaptive Rate Limiting**
   ```python
   import time
   from ratelimit import limits, sleep_and_retry
   
   class AdaptiveRateLimiter:
       def __init__(self, initial_rate=100):
           self.current_rate = initial_rate
           self.success_count = 0
           self.failure_count = 0
       
       @sleep_and_retry
       @limits(calls=100, period=60)  # Will be adjusted dynamically
       def make_api_request(self, request_func):
           try:
               result = request_func()
               self.success_count += 1
               self.adjust_rate(success=True)
               return result
           except RateLimitError:
               self.failure_count += 1
               self.adjust_rate(success=False)
               raise
       
       def adjust_rate(self, success):
           if success and self.success_count > 10:
               self.current_rate = min(self.current_rate * 1.1, 200)  # Increase rate
           elif not success:
               self.current_rate = max(self.current_rate * 0.8, 10)  # Decrease rate
   ```

2. **Implement Chunked Bulk Processing**
   ```python
   def process_bulk_data_with_chunking(data, chunk_size=100):
       results = []
       
       for i in range(0, len(data), chunk_size):
           chunk = data[i:i + chunk_size]
           
           try:
               chunk_result = process_data_chunk(chunk)
               results.extend(chunk_result)
               
               # Add delay between chunks to respect rate limits
               time.sleep(1)
               
           except RateLimitError:
               # Implement exponential backoff
               time.sleep(2 ** (i // chunk_size))
               # Retry chunk
               chunk_result = process_data_chunk(chunk)
               results.extend(chunk_result)
       
       return results
   ```

3. **Add Sync Progress Tracking**
   ```python
   def track_sync_progress(sync_id, total_items, processed_items):
       progress = {
           'sync_id': sync_id,
           'total_items': total_items,
           'processed_items': processed_items,
           'progress_percentage': (processed_items / total_items) * 100,
           'status': 'in_progress' if processed_items < total_items else 'completed',
           'timestamp': datetime.now()
       }
       
       # Update progress in database
       update_sync_progress(progress)
       
       # Send progress update if significant milestone
       if processed_items % 100 == 0:
           send_progress_update(progress)
   ```

#### Long-term Solutions:
- Implement incremental data sync
- Use queue-based batch processing
- Add API rate limit monitoring
- Implement sync optimization algorithms

## Integration Service Monitoring

### Key Metrics to Monitor:
- API success rate by provider
- Average API response time
- Transformation success rate
- Webhook delivery rate
- Rate limit utilization
- Sync job completion rate

### Monitoring Dashboard:
```python
def get_integration_metrics():
    return {
        'api_success_rate': calculate_api_success_rate(),
        'avg_response_time': calculate_avg_response_time(),
        'transformation_success_rate': calculate_transformation_success_rate(),
        'webhook_delivery_rate': calculate_webhook_delivery_rate(),
        'rate_limit_utilization': calculate_rate_limit_utilization(),
        'sync_completion_rate': calculate_sync_completion_rate()
    }
```

## Integration Security

### Security Best Practices:
1. **Credential Management**
   ```python
   def secure_credential_storage():
       # Use environment variables for sensitive data
       api_secret = os.getenv('API_SECRET')
       
       # Never log credentials
       log.info("Using API credentials from environment")
       
       # Rotate credentials regularly
       if credential_needs_rotation():
           rotate_credentials()
   ```

2. **Request/Response Logging**
   ```python
   def safe_log_request(request_data):
       # Remove sensitive data before logging
       safe_data = request_data.copy()
       
       sensitive_fields = ['password', 'api_key', 'secret', 'token']
       for field in sensitive_fields:
           safe_data.pop(field, None)
       
       log.info(f"API request: {safe_data}")
   ```

3. **Input Sanitization**
   ```python
   def sanitize_integration_input(input_data):
       # Remove potentially malicious content
       if isinstance(input_data, str):
           # Remove SQL injection patterns
           sanitized = re.sub(r'(\bunion\b.*?\bselect\b)', '', input_data, flags=re.IGNORECASE)
           # Remove XSS patterns
           sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.IGNORECASE)
           return sanitized
       elif isinstance(input_data, dict):
           return {k: sanitize_integration_input(v) for k, v in input_data.items()}
       return input_data
   ```

## Integration Testing

### Automated Integration Tests:
```python
def test_integration_endpoint(integration_config):
    test_cases = [
        {
            'name': 'happy_path',
            'input': {'test': 'data'},
            'expected_status': 200
        },
        {
            'name': 'invalid_input',
            'input': {'invalid': 'data'},
            'expected_status': 400
        },
        {
            'name': 'rate_limit',
            'input': {'test': 'data'},
            'expected_status': 429,
            'repeat': 101  # Exceed rate limit
        }
    ]
    
    results = []
    for test_case in test_cases:
        result = run_integration_test(integration_config, test_case)
        results.append(result)
    
    return generate_test_report(results)
```

## Emergency Procedures

### Integration Service Outage

**Steps:**
1. **Assess Impact**
   - Identify which integrations are affected
   - Check dependent services
   - Monitor error rates

2. **Implement Circuit Breakers**
   ```python
   def activate_integration_circuit_breaker(integration_name):
       circuit_breaker = get_circuit_breaker(integration_name)
       circuit_breaker.open()
       log.warning(f"Circuit breaker activated for {integration_name}")
   ```

3. **Enable Fallback Mechanisms**
   ```python
   def enable_integration_fallback(integration_name):
       fallback_config = get_fallback_config(integration_name)
       
       if fallback_config['type'] == 'cache':
           enable_cache_fallback(integration_name)
       elif fallback_config['type'] == 'alternative_provider':
           enable_alternative_provider(integration_name)
       elif fallback_config['type'] == 'manual_processing':
           enable_manual_processing(integration_name)
   ```

## Related Documentation
- [API Integration Patterns](../patterns/api-integration.md)
- [Webhook Security Guide](../security/webhook-security.md)
- [Data Transformation Best Practices](../data/transformation.md)
- [Rate Limiting Strategies](../api/rate-limiting.md)