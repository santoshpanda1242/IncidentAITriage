# Notification Service Troubleshooting Guide

## Overview
This guide covers notification service issues including email delivery failures, SMS gateway problems, message queue issues, and template rendering failures.

## Common Notification Issues

### 1. Email Provider API Authentication Failed

**Symptoms:**
- Email authentication errors (ERR-4001)
- Email delivery failures
- Authentication credential issues

**Root Causes:**
- Expired API credentials
- Invalid authentication tokens
- Account suspension by email provider
- Configuration changes in email provider

**Solutions:**

#### Immediate Actions:
1. **Verify Email Provider Credentials**
   ```python
   import smtplib
   from email.mime.text import MIMEText
   
   def test_email_credentials():
       try:
           server = smtplib.SMTP('smtp.email-provider.com', 587)
           server.starttls()
           server.login('username', 'password')
           server.quit()
           return True
       except smtplib.SMTPAuthenticationError:
           log.error("Email authentication failed")
           return False
   ```

2. **Implement Credential Rotation**
   ```python
   def rotate_email_credentials():
       # Generate new API credentials
       new_credentials = generate_email_provider_credentials()
       
       # Update configuration
       update_email_config(new_credentials)
       
       # Test new credentials
       if test_email_credentials():
           log.info("Email credentials rotated successfully")
           return True
       else:
           # Rollback to old credentials
           rollback_email_credentials()
           return False
   ```

3. **Add Email Provider Fallback**
   ```python
   def send_email_with_fallback(to_address, subject, body):
       email_providers = [
           'primary-provider',
           'backup-provider', 
           'emergency-provider'
       ]
       
       for provider in email_providers:
           try:
               return send_email_via_provider(provider, to_address, subject, body)
           except EmailError as e:
               log.warning(f"Email provider {provider} failed: {e}")
               continue
       
       raise EmailError("All email providers failed")
   ```

#### Long-term Solutions:
- Implement multiple email provider support
- Add credential management system
- Use OAuth2 for email authentication
- Implement email provider health monitoring

### 2. Message Queue Connection Lost

**Symptoms:**
- Message queue connection errors (ERR-4002)
- Notification delivery failures
- Queue backlog increasing

**Root Causes:**
- Message broker downtime
- Network connectivity issues
- Authentication/authorization issues
- Resource exhaustion

**Solutions:**

#### Immediate Actions:
1. **Check Message Queue Status**
   ```python
   import pika
   
   def check_message_queue_status():
       try:
           connection = pika.BlockingConnection(
               pika.ConnectionParameters('message-broker')
           )
           channel = connection.channel()
           
           # Check queue status
           queue_info = channel.queue_declare(
               queue='notifications',
               passive=True
           )
           
           return {
               'connection': 'healthy',
               'queue_size': queue_info.method.message_count,
               'consumers': queue_info.method.consumer_count
           }
           
       except pika.exceptions.AMQPConnectionError:
           return {'connection': 'failed'}
   ```

2. **Implement Connection Retry with Backoff**
   ```python
   import time
   from retrying import retry
   
   @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
   def establish_queue_connection():
       try:
           connection = pika.BlockingConnection(
               pika.ConnectionParameters('message-broker',
                                       connection_attempts=3,
                                       retry_delay=5)
           )
           return connection
       except pika.exceptions.AMQPConnectionError as e:
           log.error(f"Queue connection failed: {e}")
           raise
   ```

3. **Add Queue Connection Monitoring**
   ```python
   def monitor_queue_connection():
       while True:
           status = check_message_queue_status()
           
           if status['connection'] == 'failed':
               send_alert("Message queue connection lost")
               attempt_reconnection()
           
           # Check queue backlog
           if status['queue_size'] > 10000:
               send_alert(f"Queue backlog high: {status['queue_size']}")
           
           time.sleep(60)  # Check every minute
   ```

#### Long-term Solutions:
- Implement message broker clustering
- Add queue connection pooling
- Use persistent connections
- Implement queue monitoring and alerting

### 3. SMS Gateway Rate Limiting

**Symptoms:**
- SMS rate limit warnings (WARN-3001)
- SMS delivery delays
- Rate limit errors

**Root Causes:**
- Exceeding SMS provider rate limits
- Inefficient SMS sending patterns
- Lack of rate limiting implementation
- SMS provider policy changes

**Solutions:**

#### Immediate Actions:
1. **Implement SMS Rate Limiting**
   ```python
   from ratelimit import limits, sleep_and_retry
   
   @sleep_and_retry
   @limits(calls=10, period=60)  # 10 SMS per minute
   def send_sms(phone_number, message):
       try:
           return sms_provider.send(phone_number, message)
       except RateLimitError:
           log.warning("SMS rate limit reached")
           raise
   ```

2. **Add SMS Queue with Rate Limiting**
   ```python
   import celery
   import time
   
   @celery.task(rate_limit='10/m')
   def send_sms_task(phone_number, message):
       try:
           return sms_provider.send(phone_number, message)
       except RateLimitError:
           # Retry with exponential backoff
           time.sleep(60)
           return send_sms_task.retry()
   ```

3. **Implement SMS Provider Load Balancing**
   ```python
   def send_sms_with_load_balancing(phone_number, message):
       sms_providers = [
           {'name': 'twilio', 'weight': 5},
           {'name': 'nexmo', 'weight': 3},
           {'name': 'plivo', 'weight': 2}
       ]
       
       # Weighted random selection
       provider = weighted_choice(sms_providers)
       
       try:
           return send_sms_via_provider(provider, phone_number, message)
       except SMSError:
           # Try next provider
           return send_sms_with_fallback(phone_number, message)
   ```

#### Long-term Solutions:
- Implement SMS aggregation service
- Add SMS analytics and optimization
- Use multiple SMS providers
- Implement SMS delivery optimization

### 4. Template Rendering Failed

**Symptoms:**
- Template rendering errors (ERR-4003)
- Notification delivery failures
- Malformed notification content

**Root Causes:**
- Invalid template syntax
- Missing template variables
- Template engine errors
- Malformed input data

**Solutions:**

#### Immediate Actions:
1. **Add Template Validation**
   ```python
   from jinja2 import Template, TemplateSyntaxError
   
   def validate_template(template_string):
       try:
           Template(template_string)
           return True
       except TemplateSyntaxError as e:
           log.error(f"Template syntax error: {e}")
           return False
   ```

2. **Implement Safe Template Rendering**
   ```python
   from jinja2 import Template, Undefined
   
   class SafeUndefined(Undefined):
       def __str__(self):
           return ''  # Return empty string for undefined variables
   
   def render_template_safely(template_string, context):
       try:
           template = Template(template_string, undefined=SafeUndefined)
           return template.render(**context)
       except Exception as e:
           log.error(f"Template rendering error: {e}")
           # Return basic fallback template
           return render_fallback_template(context)
   ```

3. **Add Template Versioning**
   ```python
   def get_template_version(template_name, version='latest'):
       template_cache = load_template_cache()
       
       if version == 'latest':
           version = template_cache[template_name]['latest_version']
       
       template_data = template_cache[template_name]['versions'][version]
       
       return template_data['content']
   ```

#### Long-term Solutions:
- Implement template management system
- Add template testing and validation
- Use template inheritance for consistency
- Implement template analytics

### 5. Push Notification Service Timeout

**Symptoms:**
- Push notification timeout errors (ERR-4004)
- Push delivery failures
- User notification delays

**Root Causes:**
- Push service provider overload
- Network connectivity issues
- Invalid device tokens
- Push service configuration issues

**Solutions:**

#### Immediate Actions:
1. **Implement Push Notification Timeout Handling**
   ```python
   import concurrent.futures
   
   def send_push_with_timeout(device_token, message, timeout=5):
       with concurrent.futures.ThreadPoolExecutor() as executor:
           future = executor.submit(
               send_push_notification, 
               device_token, 
               message
           )
           try:
               return future.result(timeout=timeout)
           except concurrent.futures.TimeoutError:
               log.warning(f"Push notification timeout for {device_token}")
               return queue_push_for_retry(device_token, message)
   ```

2. **Add Device Token Validation**
   ```python
   def validate_device_token(device_token):
       # Check token format
       if not is_valid_token_format(device_token):
           return False
       
       # Check if token is expired
       if is_token_expired(device_token):
           return False
       
       # Check if token is blacklisted
       if is_token_blacklisted(device_token):
           return False
       
       return True
   ```

3. **Implement Push Notification Batching**
   ```python
   def send_batch_push_notifications(notifications):
       # Group by platform (iOS, Android, Web)
       grouped = group_by_platform(notifications)
       
       results = {}
       for platform, platform_notifications in grouped.items():
           try:
               results[platform] = send_batch_to_platform(
                   platform, 
                   platform_notifications
               )
           except PushError as e:
               log.error(f"Batch push failed for {platform}: {e}")
               results[platform] = {'failed': len(platform_notifications)}
       
       return results
   ```

#### Long-term Solutions:
- Implement push notification service clustering
- Add push delivery analytics
- Use multiple push providers
- Implement push notification optimization

## Notification Service Monitoring

### Key Metrics to Monitor:
- Email delivery success rate
- SMS delivery success rate
- Push notification delivery rate
- Average delivery time
- Queue backlog size
- Template rendering success rate

### Monitoring Dashboard:
```python
def get_notification_metrics():
    return {
        'email_success_rate': calculate_email_success_rate(),
        'sms_success_rate': calculate_sms_success_rate(),
        'push_success_rate': calculate_push_success_rate(),
        'average_delivery_time': calculate_avg_delivery_time(),
        'queue_backlog': get_queue_backlog_size(),
        'template_errors': get_template_error_count()
    }
```

## Notification Performance Optimization

### Delivery Optimization:
```python
def optimize_notification_delivery(notifications):
    # Prioritize critical notifications
    prioritized = prioritize_notifications(notifications)
    
    # Batch similar notifications
    batched = batch_notifications(prioritized)
    
    # Use optimal delivery channels
    optimized = select_optimal_channels(batched)
    
    return optimized
```

### Template Caching:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_template(template_name):
    template = load_template_from_db(template_name)
    cache.set(f"template_{template_name}", template, ttl=3600)
    return template
```

## Security Considerations

### Notification Security Best Practices:
1. **Validate Recipient Information**
   ```python
   def validate_recipient(recipient_type, recipient_value):
       if recipient_type == 'email':
           return is_valid_email(recipient_value)
       elif recipient_type == 'sms':
           return is_valid_phone_number(recipient_value)
       elif recipient_type == 'push':
           return is_valid_device_token(recipient_value)
       return False
   ```

2. **Sanitize Template Content**
   ```python
   def sanitize_template_content(content):
       # Remove potentially dangerous content
       sanitized = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.IGNORECASE)
       sanitized = re.sub(r'on\w+=".*?"', '', sanitized, flags=re.IGNORECASE)
       return sanitized
   ```

3. **Implement Rate Limiting per Recipient**
   ```python
   def check_recipient_rate_limit(recipient_type, recipient_value):
       key = f"rate_limit_{recipient_type}_{recipient_value}"
       current_count = cache.incr(key)
       
       if current_count == 1:
           cache.expire(key, 3600)  # 1 hour window
       
       limits = {
           'email': 100,  # 100 emails per hour
           'sms': 20,     # 20 SMS per hour
           'push': 50     # 50 push notifications per hour
       }
       
       return current_count <= limits.get(recipient_type, 100)
   ```

## Emergency Procedures

### Notification Service Outage

**Steps:**
1. **Assess Impact**
   - Check which notification channels are affected
   - Monitor delivery success rates
   - Identify affected user segments

2. **Implement Emergency Fallback**
   ```python
   def emergency_notification_fallback(notification):
       # Try alternative channels
       if notification['channel'] == 'email':
           return send_via_sms(notification['recipient'], notification['message'])
       elif notification['channel'] == 'sms':
           return send_via_push(notification['recipient'], notification['message'])
       else:
           return send_via_email(notification['recipient'], notification['message'])
   ```

3. **Enable Status Page Updates**
   ```python
   def update_status_page(message):
       status_page.update(
           service='notification-service',
           status='degraded',
           message=message
       )
   ```

## Related Documentation
- [Email Provider Integration](../integrations/email-providers.md)
- [SMS Gateway Configuration](../integrations/sms-gateways.md)
- [Push Notification Setup](../mobile/push-notifications.md)
- [Template Management Guide](../content/template-management.md)