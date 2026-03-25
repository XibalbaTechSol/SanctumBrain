const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://sanctum:sanctum_pass@127.0.0.1:5432/sanctum_db',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
});

const tableMapping = {
  'user': 'users',
  'entity': 'projects',
  'area': 'areas',
  'resource': 'resources',
  'archive': 'archives',
  'inboxItem': 'inbox_items',
  'habit': 'habits',
  'habitLog': 'habit_logs',
  'event': 'events',
  'systemWorkflow': 'system_workflows',
  'pushToken': 'push_tokens',
  'mcpServer': 'mcp_servers',
};

const fieldMapping = {
  'userId': 'user_id',
  'createdAt': 'created_at',
  'updatedAt': 'updated_at',
};

const mapFields = (obj, table, reverse = false) => {
  if (!obj || typeof obj !== 'object') return obj;
  const newObj = {};
  for (const [key, value] of Object.entries(obj)) {
    let newKey = key;
    if (reverse) {
      for (const [k, v] of Object.entries(fieldMapping)) {
        if (v === key) {
          newKey = k;
          break;
        }
      }
      if (table === 'projects' && key === 'goal') newKey = 'content';
    } else {
      newKey = fieldMapping[key] || key;
      if (table === 'projects' && key === 'content') newKey = 'goal';
    }
    newObj[newKey] = value;
  }
  return newObj;
};

const buildWhere = (where, table, startIdx = 1) => {
  if (!where || Object.keys(where).length === 0) return { clause: '', values: [] };
  const mappedWhere = mapFields(where, table);
  const keys = Object.keys(mappedWhere);
  const values = Object.values(mappedWhere);
  const clause = ' WHERE ' + keys.map((key, i) => `${key} = $${startIdx + i}`).join(' AND ');
  return { clause, values };
};

const createPgModel = (collectionName) => {
  const table = tableMapping[collectionName];
  if (!table) throw new Error(`Unknown model: ${collectionName}`);

  return {
    findMany: async (args = {}) => {
      const { clause, values } = buildWhere(args.where, table);
      let query = `SELECT * FROM ${table}${clause}`;
      if (args.orderBy) {
        const orderKey = Object.keys(args.orderBy)[0];
        const direction = args.orderBy[orderKey].toUpperCase();
        query += ` ORDER BY ${fieldMapping[orderKey] || orderKey} ${direction}`;
      }
      if (args.take) query += ` LIMIT ${args.take}`;
      const res = await pool.query(query, values);
      return res.rows.map(r => mapFields(r, table, true));
    },
    findUnique: async (args) => {
      const { clause, values } = buildWhere(args.where, table);
      const query = `SELECT * FROM ${table}${clause} LIMIT 1`;
      const res = await pool.query(query, values);
      return res.rows[0] ? mapFields(res.rows[0], table, true) : null;
    },
    findFirst: async (args) => {
      const { clause, values } = buildWhere(args.where, table);
      const query = `SELECT * FROM ${table}${clause} LIMIT 1`;
      const res = await pool.query(query, values);
      return res.rows[0] ? mapFields(res.rows[0], table, true) : null;
    },
    create: async ({ data }) => {
      try {
        const mappedData = mapFields(data, table);
        const keys = Object.keys(mappedData);
        const values = Object.values(mappedData).map(v => 
          (v !== null && typeof v === 'object' && !(v instanceof Date)) ? JSON.stringify(v) : v
        );
        const placeholders = keys.map((_, i) => `$${i + 1}`).join(', ');
        const query = `INSERT INTO ${table} (${keys.join(', ')}) VALUES (${placeholders}) RETURNING *`;
        const res = await pool.query(query, values);
        return mapFields(res.rows[0], table, true);
      } catch (err) {
        console.error(`[DB_CREATE_ERROR] ${err.message}`);
        throw err;
      }
    },
    update: async (args) => {
      try {
        const mappedData = mapFields(args.data, table);
        const keys = Object.keys(mappedData);
        if (keys.length === 0) return await createPgModel(collectionName).findUnique({ where: args.where });
        const values = Object.values(mappedData).map(v => 
          (v !== null && typeof v === 'object' && !(v instanceof Date)) ? JSON.stringify(v) : v
        );
        const setClause = keys.map((key, i) => `${key} = $${i + 1}`).join(', ');
        const { clause, values: whereValues } = buildWhere(args.where, table, values.length + 1);
        if (!clause) return null;
        const query = `UPDATE ${table} SET ${setClause}${clause} RETURNING *`;
        const res = await pool.query(query, [...values, ...whereValues]);
        return res.rows[0] ? mapFields(res.rows[0], table, true) : null;
      } catch (err) {
        console.error(`[DB_UPDATE_ERROR] ${err.message}`);
        throw err;
      }
    },
    delete: async (args) => {
      try {
        const { clause, values } = buildWhere(args.where, table);
        if (!clause) return null;
        const query = `DELETE FROM ${table}${clause} RETURNING *`;
        const res = await pool.query(query, values);
        return res.rows[0] ? mapFields(res.rows[0], table, true) : null;
      } catch (err) {
        console.error(`[DB_DELETE_ERROR] ${err.message}`);
        throw err;
      }
    }
  };
};

const prisma = new Proxy({}, {
  get: (target, prop) => {
    if (prop === 'then') return undefined;
    if (prop === '$connect') return async () => { await pool.query('SELECT 1'); };
    if (prop === '$disconnect') return async () => { await pool.end(); };
    return createPgModel(prop);
  }
});

module.exports = { prisma };
