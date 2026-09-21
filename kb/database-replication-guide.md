# Database Replication Lag Troubleshooting Guide

## Overview
This guide addresses MySQL master-slave replication lag issues that can cause data inconsistency across services. Critical for maintaining data integrity in read-heavy applications.

## Understanding Replication Lag

**What is Replication Lag?**
Replication lag occurs when slave servers fall behind the master in applying transaction changes, causing read operations to return stale data.

**Impact:**
- Data inconsistency between read and write operations
- Incorrect business decisions based on stale data
- User experience issues with outdated information
- Potential data corruption in critical applications

## Common Causes and Solutions

### 1. Network Latency Between Master and Slave

**Symptoms:**
- Replication lag increases during network congestion
- Intermittent replication failures
- Network timeout errors in replication logs

**Diagnosis:**
```sql
-- Check replication status on slave
SHOW SLAVE STATUS\G

-- Look at these key metrics:
-- Seconds_Behind_Master: Should be 0 or low
-- Slave_IO_Running: Should be "Yes"
-- Slave_SQL_Running: Should be "Yes"
```

**Solutions:**

#### Immediate Actions:
1. **Check Network Connectivity**
   ```bash
   # Test network latency
   ping master_db_server
   traceroute master_db_server
   ```

2. **Optimize Network Configuration**
   ```bash
   # Increase TCP buffer sizes
   sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
   sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
   ```

#### Long-term Solutions:
- Place master and slave in same data center/region
- Use dedicated network for replication traffic
- Implement network monitoring and alerting
- Consider MySQL Group Replication for better fault tolerance

### 2. Slave Server Resource Exhaustion

**Symptoms:**
- Replication lag correlates with high CPU/memory usage
- Slow query performance on slave
- System resource exhaustion warnings

**Diagnosis:**
```bash
# Check system resources
top
htop
free -h
iostat -x 1

# Check MySQL performance
SHOW PROCESSLIST;
SHOW ENGINE INNODB STATUS;
```

**Solutions:**

#### Immediate Actions:
1. **Resource Optimization**
   ```sql
   -- Optimize InnoDB buffer pool
   SET GLOBAL innodb_buffer_pool_size = 4G;  -- Adjust based on available RAM
   
   -- Optimize query cache (if using)
   SET GLOBAL query_cache_size = 256M;
   ```

2. **Identify and Optimize Slow Queries**
   ```sql
   -- Enable slow query log
   SET GLOBAL slow_query_log = 'ON';
   SET GLOBAL long_query_time = 2;
   
   -- Analyze slow queries
   mysqldumpslow /var/log/mysql/mysql-slow.log
   ```

#### Long-term Solutions:
- Upgrade slave server hardware
- Implement read scaling with multiple slaves
- Use SSD storage for better I/O performance
- Implement read/write splitting at application level

### 3. Long-Running Transactions on Master

**Symptoms:**
- Replication lag spikes during specific operations
- Large transactions cause significant delays
- Batch processing operations impact replication

**Diagnosis:**
```sql
-- Find long-running transactions
SELECT * FROM information_schema.innodb_trx
ORDER BY trx_started ASC;

-- Check for long-running queries
SHOW PROCESSLIST;
```

**Solutions:**

#### Immediate Actions:
1. **Break Large Transactions**
   ```python
   # Instead of one large transaction
   # process_large_batch(data)
   
   # Use smaller chunks
   for chunk in chunks(data, batch_size=1000):
       with transaction():
           process_chunk(chunk)
   ```

2. **Optimize Batch Operations**
   ```sql
   -- Use bulk inserts instead of row-by-row
   INSERT INTO table (col1, col2) VALUES 
   (val1, val2),
   (val3, val4),
   (val5, val6);
   ```

#### Long-term Solutions:
- Implement transaction monitoring
- Use queue systems for batch processing
- Optimize application logic to avoid large transactions
- Consider online schema change tools

### 4. Schema Differences Between Master and Slave

**Symptoms:**
- Replication stops with schema mismatch errors
- Specific tables fail to replicate
- Inconsistent table structures

**Diagnosis:**
```sql
-- Compare schemas
SHOW CREATE TABLE table_name;
-- Run on both master and slave

-- Check for schema differences
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'your_database';
```

**Solutions:**

#### Immediate Actions:
1. **Synchronize Schemas**
   ```bash
   # Use mysqldump to copy schema
   mysqldump --no-data --skip-add-locks master_db | mysql slave_db
   ```

2. **Use pt-table-checksum**
   ```bash
   # Check data consistency
   pt-table-checksum --host=master --user=root --password=pass \
     --databases=your_database
   ```

#### Long-term Solutions:
- Implement schema change management process
- Use tools like pt-online-schema-change for schema changes
- Automate schema synchronization
- Implement schema version control

## Emergency Procedures

### When Replication Lag Exceeds Thresholds

**Critical Threshold:** > 5 minutes
**Warning Threshold:** > 1 minute

**Emergency Steps:**

1. **Assess Impact**
   ```sql
   -- Check current lag
   SHOW SLAVE STATUS\G
   -- Look at Seconds_Behind_Master
   ```

2. **Redirect Read Traffic**
   ```python
   # Temporarily direct reads to master
   if replication_lag > threshold:
       read_connection = master_connection
   else:
       read_connection = slave_connection
   ```

3. **Skip Problematic Transaction (Last Resort)**
   ```sql
   -- STOP SLAVE;
   -- SET GLOBAL sql_slave_skip_counter = 1;
   -- START SLAVE;
   -- ⚠️ Use only in emergencies, can cause data inconsistency
   ```

4. **Promote Slave to Master (If Needed)**
   ```bash
   # Emergency master promotion
   # 1. Stop writes to current master
   # 2. Ensure slave is caught up
   # 3. Promote slave to master
   # 4. Update application configuration
   ```

## Monitoring and Prevention

### Key Metrics to Monitor:
- `Seconds_Behind_Master` from `SHOW SLAVE STATUS`
- Replication throughput (bytes/second)
- Binary log disk usage
- Network latency between master/slave
- Slave server resource utilization

### Monitoring Queries:
```sql
-- Replication lag monitoring
SELECT 
    CONCAT(SUBSTRING_INDEX(SUBSTRING_INDEX(host, ' ', 1), '.', -1), ' node') AS node,
    VARIABLE_VALUE AS current_lag
FROM performance_schema.threads t
JOIN performance_schema.threads s ON s.PROCESSLIST_ID = t.PROCESSLIST_ID
WHERE t.NAME = 'thread/replication/apply';
```

### Alert Configuration:
- **Critical:** Replication lag > 5 minutes
- **Warning:** Replication lag > 1 minute  
- **Info:** Replication lag > 30 seconds

## Best Practices

### 1. Replication Topology
- Use multiple slaves for read scaling
- Implement circular replication for multi-master setups
- Consider MySQL Group Replication for automatic failover

### 2. Configuration Optimization
```ini
# my.cnf optimizations for replication
[mysqld]
# Binary logging
log_bin = mysql-bin
binlog_format = ROW
binlog_cache_size = 4M
max_binlog_size = 1G

# Replication settings
relay_log = relay-bin
relay_log_index = relay-bin.index
read_only = 1
slave_parallel_workers = 4
slave_parallel_type = LOGICAL_CLOCK
```

### 3. Backup Strategy
- Regular backups from master (using Percona XtraBackup)
- Point-in-time recovery capability
- Test backup restoration procedures
- Document recovery time objectives (RTO/RPO)

## Related Documentation
- [MySQL Replication Documentation](https://dev.mysql.com/doc/refman/8.0/en/replication.html)
- [Per Toolkit for MySQL](https://www.percona.com/software/database-tools/percona-toolkit)
- [High Availability Architecture](../architecture/high-availability.md)
- [Database Backup Procedures](../database/backup-procedures.md)