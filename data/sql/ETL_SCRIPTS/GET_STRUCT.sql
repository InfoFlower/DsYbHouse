-- SQLite: Get all tables and their columns
SELECT *
    -- m.tbl_name AS table_name,
    -- p.name AS column_name,
    -- p.type AS column_type,
    -- p.pk AS is_primary_key
FROM 
    sqlite_master m
    LEFT JOIN pragma_table_info((m.tbl_name)) p ON 1=1
WHERE 
    m.type = 'table'
    AND m.name NOT LIKE 'sqlite_%'
ORDER BY 
    m.tbl_name, 
    p.cid;