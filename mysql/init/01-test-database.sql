-- Development-only database used by Django's automated test runner.
CREATE DATABASE IF NOT EXISTS test_ai_attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON test_ai_attendance_db.* TO 'attendance_user'@'%';
FLUSH PRIVILEGES;
