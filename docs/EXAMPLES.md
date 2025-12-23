# Database Backup Utility - Input/Output Examples

Clear examples showing what users type and what they see.

---

## 1. SQLite Backup

**Input:**
```bash
db-backup backup --type sqlite --database ./myapp.db --output ./backups/
```

**Output:**
```
🔍 Connecting to SQLite database: ./myapp.db
✅ Connection successful

📦 Starting FULL backup...
   Database: myapp.db
   Size: 45.2 MB

🗜️  Compressing backup...
   Original: 45.2 MB → Compressed: 12.8 MB

💾 Saving to: ./backups/myapp_2024-01-15_143022.db.gz

✅ Backup completed successfully!
   Duration: 8.2 seconds
   File: ./backups/myapp_2024-01-15_143022.db.gz
```

---

## 2. MySQL Backup to S3

**Input:**
```bash
db-backup backup \
    --type mysql \
    --host localhost \
    --port 3306 \
    --user root \
    --password secret \
    --database ecommerce \
    --storage s3 \
    --s3-bucket my-backups \
    --compress
```

**Output:**
```
🔍 Connecting to MySQL database...
   Host: localhost:3306
   Database: ecommerce
✅ Connection successful (MySQL 8.0.35)

📦 Starting FULL backup...
   Tables: 42
   Estimated size: 1.2 GB

🗜️  Compressing with gzip (level 6)...
   Original: 1.2 GB → Compressed: 320 MB

☁️  Uploading to S3...
   Bucket: my-backups
   Key: mysql/ecommerce/ecommerce_2024-01-15_143022.sql.gz
   Progress: [████████████████████] 100%

✅ Backup completed successfully!
   Duration: 2 minutes 34 seconds
   Location: s3://my-backups/mysql/ecommerce/ecommerce_2024-01-15_143022.sql.gz
   Size: 320 MB
```

---

## 3. Restore from Backup

**Input:**
```bash
db-backup restore \
    --type mysql \
    --file s3://my-backups/mysql/ecommerce/ecommerce_2024-01-15_143022.sql.gz \
    --host localhost \
    --user root \
    --password secret \
    --database ecommerce_restored
```

**Output:**
```
☁️  Downloading from S3...
   File: ecommerce_2024-01-15_143022.sql.gz
   Size: 320 MB
   Progress: [████████████████████] 100%

🗜️  Decompressing...
   320 MB → 1.2 GB

🔍 Connecting to MySQL...
   Host: localhost:3306
   Target database: ecommerce_restored
✅ Connection successful

⚠️  Warning: Database 'ecommerce_restored' will be overwritten. Continue? [y/N]: y

📥 Restoring database...
   Progress: [████████████████████] 100%
   Tables restored: 42/42

✅ Restore completed successfully!
   Duration: 3 minutes 12 seconds
   Database: ecommerce_restored
```

---

## 4. Selective Restore (Specific Tables)

**Input:**
```bash
db-backup restore \
    --type mysql \
    --file ./backups/ecommerce.sql.gz \
    --database ecommerce \
    --tables users,orders,products
```

**Output:**
```
🗜️  Decompressing backup...
✅ Backup file validated

🔍 Connecting to MySQL database: ecommerce
✅ Connection successful

📋 Tables to restore:
   • users
   • orders  
   • products

📥 Restoring selected tables...
   [1/3] users ✅
   [2/3] orders ✅
   [3/3] products ✅

✅ Selective restore completed!
   Duration: 45 seconds
   Tables restored: 3
```

---

## 5. Connection Test (Before Backup)

**Input:**
```bash
db-backup test-connection --type postgres --host db.example.com --user admin --database production
```

**Output (Success):**
```
🔍 Testing PostgreSQL connection...
   Host: db.example.com:5432
   User: admin
   Database: production

✅ Connection successful!
   Server: PostgreSQL 15.4
   Databases accessible: 3
   Tables in 'production': 67
```

**Output (Failure):**
```
🔍 Testing PostgreSQL connection...
   Host: db.example.com:5432
   User: admin
   Database: production

❌ Connection failed!
   Error: Authentication failed for user 'admin'
   
💡 Suggestions:
   • Verify username and password
   • Check if user has access to database 'production'
   • Ensure host allows connections from your IP
```

---

## 6. List Backups

**Input:**
```bash
db-backup list --storage s3 --bucket my-backups
```

**Output:**
```
📋 Backups in s3://my-backups

┌──────────────────────────────────────────────────┬──────────┬─────────────────────┐
│ File                                             │ Size     │ Created             │
├──────────────────────────────────────────────────┼──────────┼─────────────────────┤
│ mysql/ecommerce/ecommerce_2024-01-15_143022.sql.gz│ 320 MB   │ 2024-01-15 14:30:22 │
│ mysql/ecommerce/ecommerce_2024-01-14_020000.sql.gz│ 318 MB   │ 2024-01-14 02:00:00 │
│ postgres/analytics/analytics_2024-01-15.sql.gz   │ 1.2 GB   │ 2024-01-15 03:00:00 │
│ mongodb/logs/logs_2024-01-15.archive.gz          │ 890 MB   │ 2024-01-15 04:00:00 │
└──────────────────────────────────────────────────┴──────────┴─────────────────────┘

Total: 4 backups, 2.7 GB
```

---

## 7. Schedule Backup

**Input:**
```bash
db-backup schedule add \
    --name "daily-ecommerce" \
    --cron "0 2 * * *" \
    --config ./configs/ecommerce-backup.yaml
```

**Output:**
```
📅 Creating scheduled backup job...

   Name: daily-ecommerce
   Schedule: 0 2 * * * (Daily at 2:00 AM)
   Config: ./configs/ecommerce-backup.yaml

✅ Schedule created successfully!

   Next run: 2024-01-16 02:00:00 (in 11 hours)
   
💡 To start the scheduler daemon: db-backup schedule start
```

---

## 8. Error Handling

**Input (Missing Tool):**
```bash
db-backup backup --type mysql --database myapp
```

**Output:**
```
❌ Error: mysqldump not found

   The MySQL backup requires 'mysqldump' to be installed.

💡 Installation:
   • Ubuntu/Debian: sudo apt install mysql-client
   • macOS: brew install mysql-client
   • Windows: Download MySQL Community Server

   After installation, ensure mysqldump is in your PATH.
```

**Input (Disk Space):**
```bash
db-backup backup --type postgres --database bigdb --output ./backups/
```

**Output:**
```
⚠️  Warning: Low disk space

   Required: ~2.5 GB (estimated)
   Available: 1.2 GB
   
   Options:
   1. Free up disk space
   2. Use cloud storage: --storage s3 --bucket your-bucket
   3. Enable compression: --compress (reduces size by ~70%)

❌ Backup aborted. Resolve disk space issue and retry.
```

---

## 9. Help Command

**Input:**
```bash
db-backup --help
```

**Output:**
```
                                                                       
 Usage: db-backup [OPTIONS] COMMAND [ARGS]...                          
                                                                       
 🗄️  Database Backup Utility - Backup and restore any database         
                                                                       
╭─ Commands ───────────────────────────────────────────────────────────╮
│ backup          Create a database backup                             │
│ restore         Restore database from backup                         │
│ list            List available backups                               │
│ test-connection Test database connection                             │
│ schedule        Manage backup schedules                              │
│ config          Configuration management                             │
╰──────────────────────────────────────────────────────────────────────╯

╭─ Options ────────────────────────────────────────────────────────────╮
│ --version       Show version and exit                                │
│ --help          Show this message and exit                           │
╰──────────────────────────────────────────────────────────────────────╯

Examples:
  db-backup backup --type sqlite --database ./app.db --output ./backups/
  db-backup restore --type mysql --file backup.sql.gz --database myapp
  db-backup schedule add --cron "0 2 * * *" --config backup.yaml
```
