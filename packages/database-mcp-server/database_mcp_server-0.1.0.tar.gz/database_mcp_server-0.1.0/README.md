database-mcp-python/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database_mcp.py          # 主MCP类
│   │   └── manager.py               # 管理器类
│   ├── datasource/
│   │   ├── __init__.py
│   │   ├── base.py                  # DataSource基类
│   │   ├── mysql_datasource.py      # MySQL数据源
│   │   ├── oracle_datasource.py     # Oracle数据源
│   │   └── factory.py               # 数据源工厂
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── database_strategy.py     # 数据库策略基类（当前文件）
│   │   ├── mysql_strategy.py        # MySQL策略
│   │   └── oracle_strategy.py       # Oracle策略
│   ├── model/
│   │   ├── __init__.py
│   │   ├── data_group.py            # DataGroup类
│   │   ├── delete_condition.py      # DeleteCondition类
│   │   ├── query_condition.py       # 查询条件类
│   │   └── table_metadata.py        # 表元数据类
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config_loader.py         # 配置加载器
│   │   └── database_config.py       # 数据库配置类
│   ├── exception/
│   │   ├── __init__.py
│   │   ├── database_error.py        # 数据库异常类
│   │   └── connection_error.py      # 连接异常类
│   └── utils/
│       ├── __init__.py
│       ├── connection_pool.py       # 连接池工具
│       └── validator.py             # 验证工具
├── tests/
│   ├── __init__.py
│   ├── core/
│   ├── datasource/
│   ├── strategy/
│   ├── model/
│   └── utils/
├── examples/
│   ├── __init__.py
│   └── usage_example.py
├── docs/
│   └── README.md
├── requirements.txt
└── setup.py