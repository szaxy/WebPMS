-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "hstore";

-- 创建管理员用户
-- 注意：这只是示例，实际生产环境中应通过Django管理命令创建超级用户
-- 实际用户会通过Django的用户表管理
CREATE OR REPLACE FUNCTION create_admin_user() 
RETURNS void AS $$
BEGIN
    RAISE NOTICE 'Admin user will be created through Django migrations';
END;
$$ LANGUAGE plpgsql; 