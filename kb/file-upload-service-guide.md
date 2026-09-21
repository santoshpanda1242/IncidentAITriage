# File Upload Service Troubleshooting Guide

## Overview
This guide covers file upload service issues including S3 connectivity problems, virus scanning failures, file validation issues, and CDN integration problems.

## Common File Upload Issues

### 1. S3 Upload Connection Timeout

**Symptoms:**
- S3 upload timeout errors (ERR-8001)
- File upload failures
- User inability to upload content

**Root Causes:**
- Network connectivity issues to S3
- S3 service downtime or degradation
- Large file upload timeouts
- Insufficient timeout configurations

**Solutions:**

#### Immediate Actions:
1. **Check S3 Connectivity**
   ```python
   import boto3
   from botocore.exceptions import EndpointConnectionError
   
   def check_s3_connectivity():
       try:
           s3_client = boto3.client('s3')
           s3_client.list_buckets()
           return True
       except EndpointConnectionError:
           log.error("S3 endpoint connection failed")
           return False
   ```

2. **Implement Upload Retry with Exponential Backoff**
   ```python
   import time
   from botocore.exceptions import ClientError
   
   def upload_with_retry(file_path, bucket, key, max_retries=3):
       s3_client = boto3.client('s3')
       
       for attempt in range(max_retries):
           try:
               s3_client.upload_file(file_path, bucket, key)
               return True
           except ClientError as e:
               if attempt < max_retries - 1:
                   wait_time = 2 ** attempt  # Exponential backoff
                   time.sleep(wait_time)
                   continue
               raise
   ```

3. **Add S3 Upload Timeout Configuration**
   ```python
   def configure_s3_timeout():
       config = boto3.Config(
           connect_timeout=10,  # 10 seconds connection timeout
           read_timeout=30,    # 30 seconds read timeout
           retries={'max_attempts': 3}
       )
       s3_client = boto3.client('s3', config=config)
       return s3_client
   ```

#### Long-term Solutions:
- Implement multipart upload for large files
- Add S3 region failover
- Use S3 Transfer Acceleration
- Implement upload queue with worker pool

### 2. Virus Scan Service Unavailable

**Symptoms:**
- Virus scan service errors (ERR-8003)
- File upload blocking
- Security validation failures

**Root Causes:**
- Antivirus service downtime
- Network connectivity to scan service
- License or configuration issues
- Service overload

**Solutions:**

#### Immediate Actions:
1. **Implement Virus Scan Fallback**
   ```python
   def scan_file_with_fallback(file_path):
       try:
           # Primary virus scan service
           return primary_virus_scan(file_path)
       except VirusScanError:
           log.warning("Primary virus scan failed, using fallback")
           try:
               # Fallback virus scan service
               return fallback_virus_scan(file_path)
           except VirusScanError:
               # Last resort: basic file validation
               return basic_file_validation(file_path)
   ```

2. **Add Virus Scan Queue**
   ```python
   import celery
   
   @celery.task(bind=True, max_retries=3)
   def async_virus_scan(self, file_path):
       try:
           scan_result = perform_virus_scan(file_path)
           return scan_result
       except VirusScanError as exc:
           # Retry with exponential backoff
           raise self.retry(exc=exc, countdown=2 ** self.request.retries)
   ```

3. **Implement Scan Result Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_cached_scan_result(file_hash):
       # Check cache for scan result
       cached_result = cache.get(f"scan_{file_hash}")
       if cached_result:
           return cached_result
       
       # Perform scan if not cached
       result = perform_virus_scan_by_hash(file_hash)
       cache.set(f"scan_{file_hash}", result, ttl=86400)  # 24 hours
       return result
   ```

#### Long-term Solutions:
- Implement multiple virus scan providers
- Add virus scan service clustering
- Use cloud-based virus scanning services
- Implement file hash-based scanning

### 3. File Size Validation Failed

**Symptoms:**
- File size validation errors (ERR-8002)
- Upload rejections for valid files
- User confusion about size limits

**Root Causes:**
- Incorrect size limit configuration
- Network timeouts during size check
- Client-side vs server-side size mismatch
- File corruption during upload

**Solutions:**

#### Immediate Actions:
1. **Implement Progressive File Size Check**
   ```python
   def validate_file_size_progressive(file_path, max_size_mb=100):
       # Check file system size first
       file_size = os.path.getsize(file_path)
       max_size_bytes = max_size_mb * 1024 * 1024
       
       if file_size > max_size_bytes:
           raise FileSizeError(f"File size {file_size} exceeds limit {max_size_bytes}")
       
       # Stream-based validation for large files
       if file_size > 10 * 1024 * 1024:  # > 10MB
           return validate_large_file_streaming(file_path, max_size_bytes)
       else:
           return True
   ```

2. **Add Client-Side Validation**
   ```javascript
   // Client-side file size validation
   function validateFileSize(file, maxSizeMB) {
       const maxSizeBytes = maxSizeMB * 1024 * 1024;
       if (file.size > maxSizeBytes) {
           alert(`File size ${file.size} exceeds limit ${maxSizeBytes}`);
           return false;
       }
       return true;
   }
   ```

3. **Implement File Size Limit per User Type**
   ```python
   def get_user_file_size_limit(user):
       # Different limits for different user types
       user_limits = {
           'free': 10 * 1024 * 1024,      # 10MB
           'premium': 100 * 1024 * 1024,   # 100MB
           'enterprise': 1024 * 1024 * 1024  # 1GB
       }
       
       return user_limits.get(user.subscription_type, 10 * 1024 * 1024)
   ```

#### Long-term Solutions:
- Implement user-specific storage quotas
- Add file compression for large files
- Use chunked upload for very large files
- Implement storage tiering (hot/cold storage)

### 4. Thumbnail Generation Failed

**Symptoms:**
- Thumbnail generation errors (ERR-8004)
- Image uploads without previews
- Performance degradation during image processing

**Root Causes:**
- Image processing service overload
- Corrupted or unsupported image formats
- Insufficient memory for image processing
- Timeout during processing

**Solutions:**

#### Immediate Actions:
1. **Implement Thumbnail Generation with Timeout**
   ```python
   import signal
   from contextlib import contextmanager
   
   @contextmanager
   def timeout_context(seconds):
       def timeout_handler(signum, frame):
           raise TimeoutError("Thumbnail generation timeout")
       
       signal.signal(signal.SIGALRM, timeout_handler)
       signal.alarm(seconds)
       try:
           yield
       finally:
           signal.alarm(0)
   
   def generate_thumbnail_with_timeout(image_path, timeout_seconds=10):
       try:
           with timeout_context(timeout_seconds):
               return generate_thumbnail(image_path)
       except TimeoutError:
           log.warning(f"Thumbnail generation timeout for {image_path}")
           return generate_default_thumbnail(image_path)
   ```

2. **Add Thumbnail Generation Queue**
   ```python
   import celery
   
   @celery.task(bind=True, max_retries=2)
   def async_thumbnail_generation(self, image_path):
       try:
           thumbnail = generate_thumbnail(image_path)
           upload_thumbnail_to_cdn(thumbnail)
           return thumbnail
       except ImageProcessingError as exc:
           # Retry with reduced quality
           if self.request.retries < 2:
               raise self.retry(exc=exc, countdown=5)
           else:
               return generate_low_quality_thumbnail(image_path)
   ```

3. **Implement Thumbnail Format Fallback**
   ```python
   def generate_thumbnail_with_fallback(image_path):
       formats = ['WEBP', 'JPEG', 'PNG']
       
       for format in formats:
           try:
               thumbnail = generate_thumbnail(image_path, format=format)
               return thumbnail
           except ImageProcessingError:
               continue
       
       # Ultimate fallback: resize only
       return simple_resize_image(image_path)
   ```

#### Long-term Solutions:
- Implement dedicated image processing service
- Use CDN for thumbnail delivery
- Add thumbnail generation caching
- Implement progressive image loading

### 5. Storage Quota Exceeded

**Symptoms:**
- Storage quota errors (ERR-8007)
- Upload rejections for valid files
- User unable to manage storage

**Root Causes:**
- User storage limits reached
- Insufficient overall storage capacity
- Unrestricted file retention policies
- Lack of storage cleanup processes

**Solutions:**

#### Immediate Actions:
1. **Implement Storage Quota Management**
   ```python
   def check_user_storage_quota(user_id, file_size):
       user_storage = get_user_storage_usage(user_id)
       user_quota = get_user_storage_quota(user_id)
       
       if user_storage['used'] + file_size > user_quota:
           available = user_quota - user_storage['used']
           raise StorageQuotaError(
               f"Storage quota exceeded. Available: {available} bytes"
           )
       
       return True
   ```

2. **Add Storage Cleanup Automation**
   ```python
   def cleanup_old_files(user_id, days_threshold=30):
       # Find files older than threshold
       old_files = find_files_by_age(user_id, days_threshold)
       
       for file in old_files:
           if not file['is_permanent']:
               delete_file(file['id'])
               log.info(f"Deleted old file: {file['name']}")
       
       # Update user storage usage
       update_user_storage_usage(user_id)
   ```

3. **Implement Storage Usage Alerts**
   ```python
   def check_storage_usage_alerts():
       users = get_all_users()
       
       for user in users:
           storage = get_user_storage_usage(user['id'])
           quota = get_user_storage_quota(user['id'])
           usage_percent = (storage['used'] / quota) * 100
           
           if usage_percent > 90:
               send_storage_alert(user, usage_percent)
           elif usage_percent > 75:
               send_storage_warning(user, usage_percent)
   ```

#### Long-term Solutions:
- Implement tiered storage pricing
- Add automatic storage cleanup policies
- Use storage lifecycle management
- Implement storage compression and deduplication

## File Upload Monitoring

### Key Metrics to Monitor:
- Upload success rate
- Average upload time
- Virus scan success rate
- Storage usage trends
- CDN cache hit ratio
- Thumbnail generation success rate

### Monitoring Dashboard:
```python
def get_upload_service_metrics():
    return {
        'total_uploads': get_total_uploads_today(),
        'success_rate': calculate_upload_success_rate(),
        'avg_upload_time': calculate_avg_upload_time(),
        'virus_scan_rate': calculate_virus_scan_success_rate(),
        'storage_usage': get_total_storage_usage(),
        'cdn_performance': get_cdn_metrics()
    }
```

## Security Considerations

### File Upload Security Best Practices:
1. **File Type Validation**
   ```python
   ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx'}
   
   def validate_file_type(filename):
       extension = os.path.splitext(filename)[1].lower()
       if extension not in ALLOWED_EXTENSIONS:
           raise FileTypeError(f"File type {extension} not allowed")
       return True
   ```

2. **Content-Type Validation**
   ```python
   def validate_content_type(file_path, expected_type):
       import magic
       
       mime = magic.Magic(mime=True)
       actual_type = mime.from_file(file_path)
       
       if actual_type != expected_type:
           raise ContentTypeError(f"Content type mismatch: {actual_type} vs {expected_type}")
   ```

3. **File Name Sanitization**
   ```python
   def sanitize_filename(filename):
       # Remove path components
       filename = os.path.basename(filename)
       
       # Remove dangerous characters
       filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
       
       # Limit length
       filename = filename[:255]
       
       return filename
   ```

## Related Documentation
- [S3 Best Practices](../storage/s3-best-practices.md)
- [File Upload Security](../security/file-upload-security.md)
- [CDN Integration Guide](../cdn/cdn-integration.md)
- [Image Processing Optimization](../performance/image-optimization.md)