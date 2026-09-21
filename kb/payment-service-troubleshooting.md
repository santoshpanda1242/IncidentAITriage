# Payment Service Troubleshooting Guide

## Overview
This guide covers common issues and solutions for the payment service, including database connectivity, payment gateway integration, and transaction processing problems.

## Common Issues and Solutions

### 1. Database Connection Timeout During Payment Processing

**Symptoms:**
- Payment failures during peak hours
- Database connection timeout errors (ERR-5001)
- Increased transaction processing time

**Root Causes:**
- Database connection pool exhaustion
- Network latency between payment service and database
- Insufficient database resources during high load

**Solutions:**

#### Immediate Actions:
1. **Check Database Connection Pool Status**
   ```bash
   # Monitor connection pool metrics
   SHOW PROCESSLIST;
   SHOW STATUS LIKE 'Threads_connected';
   ```

2. **Implement Connection Pooling**
   ```python
   # Increase connection pool size
   connection_pool = SQLAlchemy(
       engine=create_engine(
           'mysql://user:pass@localhost/db',
           pool_size=20,
           max_overflow=10,
           pool_timeout=30
       )
   )
   ```

3. **Add Retry Logic with Exponential Backoff**
   ```python
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
   def process_payment(payment_data):
       # Payment processing logic
       pass
   ```

#### Long-term Solutions:
- Implement database read replicas for payment queries
- Add database connection monitoring and alerting
- Consider database sharding for payment data
- Implement circuit breaker for database calls

### 2. Payment Gateway API Rate Limiting

**Symptoms:**
- Payment gateway API rate limit errors (ERR-5002)
- Failed transactions during peak periods
- API timeout errors

**Root Causes:**
- Exceeding payment gateway API rate limits
- Inefficient API call patterns
- Lack of request queuing

**Solutions:**

#### Immediate Actions:
1. **Implement Rate Limiting**
   ```python
   from ratelimit import limits, sleep_and_retry
   
   @sleep_and_retry
   @limits(calls=100, period=60)  # 100 calls per minute
   def call_payment_gateway_api(payment_data):
       # API call logic
       pass
   ```

2. **Add Request Queuing**
   ```python
   # Use message queue for payment processing
   queue.enqueue(process_payment, payment_data)
   ```

#### Long-term Solutions:
- Implement payment batching to reduce API calls
- Add payment gateway API monitoring
- Negotiate higher rate limits with payment provider
- Implement multiple payment gateway fallback

### 3. Transaction Deadlock Detection

**Symptoms:**
- Transaction deadlock errors (ERR-5003)
- Payment processing hangs
- Database lock wait timeouts

**Root Causes:**
- Concurrent transaction conflicts
- Long-running transactions
- Inconsistent transaction ordering

**Solutions:**

#### Immediate Actions:
1. **Identify Deadlocking Transactions**
   ```sql
   SHOW ENGINE INNODB STATUS;
   ```

2. **Implement Transaction Retry Logic**
   ```python
   def execute_with_retry(transaction_func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return transaction_func()
           except DatabaseError as e:
               if 'Deadlock' in str(e) and attempt < max_retries - 1:
                   time.sleep(2 ** attempt)  # Exponential backoff
                   continue
               raise
   ```

#### Long-term Solutions:
- Review and optimize transaction boundaries
- Implement consistent transaction ordering
- Add deadlock monitoring and alerting
- Consider row-level locking instead of table locks

### 4. SSL Certificate Validation Failures

**Symptoms:**
- SSL certificate validation errors (ERR-5004)
- Payment gateway connection failures
- Security handshake failures

**Root Causes:**
- Expired or invalid SSL certificates
- Certificate chain issues
- Time synchronization problems

**Solutions:**

#### Immediate Actions:
1. **Check SSL Certificate Validity**
   ```bash
   openssl s_client -connect payment-gateway.com:443 -showcerts
   ```

2. **Update Certificate Bundle**
   ```python
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context  # For testing only
   ```

#### Long-term Solutions:
- Implement certificate monitoring and auto-renewal
- Add certificate validation to deployment pipeline
- Use certificate pinning for payment gateway
- Implement SSL/TLS best practices

### 5. Fraud Detection Service Timeout

**Symptoms:**
- Fraud detection service timeout errors (ERR-5005)
- High-risk transaction processing delays
- Payment processing hangs

**Root Causes:**
- Fraud detection service overload
- Network latency to fraud detection service
- Inefficient fraud detection algorithms

**Solutions:**

#### Immediate Actions:
1. **Implement Fraud Detection Timeout**
   ```python
   import signal
   
   def timeout_handler(signum, frame):
       raise TimeoutError("Fraud detection timeout")
   
   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(5)  # 5 second timeout
   ```

2. **Add Fallback Fraud Detection**
   ```python
   def check_fraud_with_fallback(transaction_data):
       try:
           return primary_fraud_service.check(transaction_data)
       except TimeoutError:
           return fallback_fraud_rules.apply(transaction_data)
   ```

#### Long-term Solutions:
- Implement fraud detection service scaling
- Add local fraud detection rules as fallback
- Optimize fraud detection algorithms
- Implement fraud detection result caching

## Monitoring and Alerting

### Key Metrics to Monitor:
- Payment success rate
- Average payment processing time
- Database connection pool utilization
- Payment gateway API response time
- Fraud detection service response time

### Alert Thresholds:
- Payment success rate < 95%
- Average processing time > 5 seconds
- Database connection pool utilization > 80%
- API error rate > 5%

## Emergency Contacts
- Payment Service Team: payments-team@company.com
- Database Team: database-team@company.com
- Security Team: security-team@company.com

## Related Documentation
- [Payment Gateway API Documentation](https://payment-gateway.com/docs)
- [Database Performance Tuning Guide](../database/database-tuning.md)
- [Security Best Practices](../security/security-practices.md)