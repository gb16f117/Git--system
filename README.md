# 中药方管理系统

一个基于Flask的中药方信息管理系统，支持中药方的增删改查、智能搜索和数据管理。

## 功能特性

### 核心功能
- 📋 **药方管理**：添加、编辑、删除、查看中药方信息
- 🔍 **智能搜索**：支持关键词搜索、模糊匹配、AND/OR逻辑搜索
- 📊 **分类筛选**：按疗效类型分类浏览和管理
- 📝 **详情展示**：完整的药方信息展示和相关推荐
- 🏷️ **搜索历史**：保存和管理搜索记录

### 搜索功能
- **关键词搜索**：支持药方名称、疗效、成分的全文搜索
- **匹配模式**：
  - 模糊匹配：最灵活的搜索方式
  - AND逻辑：包含所有关键词
  - OR逻辑：包含任一关键词
- **高亮显示**：搜索结果中关键词高亮显示
- **快捷标签**：常用疗效关键词一键添加

### 数据管理
- **完整的CRUD操作**：创建、读取、更新、删除
- **分类管理**：支持药方分类和筛选
- **批量操作**：支持批量导入导出
- **数据统计**：实时统计药方数量和分类分布

## 技术栈

### 后端
- **Python 3.8+**
- **Flask 2.3.3**：Web框架
- **SQLite3**：轻量级数据库
- **Flask-CORS 4.0.0**：跨域支持

### 前端
- **HTML5/CSS3**：页面结构和样式
- **Bootstrap 5.1.3**：响应式UI框架
- **JavaScript ES6+**：交互逻辑
- **Bootstrap Icons 1.7.2**：图标库

### 数据库设计
```sql
CREATE TABLE prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,           -- 药方名称
    efficacy TEXT NOT NULL,               -- 治疗疗效（主要搜索字段）
    ingredients TEXT,                     -- 主要成分
    usage TEXT,                           -- 用法用量
    precautions TEXT,                     -- 注意事项
    category VARCHAR(50),                 -- 分类
    source VARCHAR(100),                  -- 来源/出处
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 安装和运行

### 1. 克隆项目
```bash
git clone <repository-url>
cd 中药方管理系统
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行应用
```bash
python app.py
```

### 5. 访问应用
打开浏览器访问：http://localhost:5000

## API接口

### 药方管理
- `GET /api/prescriptions` - 获取药方列表（支持分页和筛选）
- `GET /api/prescriptions/{id}` - 获取单个药方详情
- `POST /api/prescriptions` - 创建新药方
- `PUT /api/prescriptions/{id}` - 更新药方
- `DELETE /api/prescriptions/{id}` - 删除药方

### 搜索功能
- `GET /api/prescriptions/search` - 搜索药方
  - 参数：`q`（搜索关键词）、`match_type`（匹配模式）、`limit`（结果数量）

### 其他接口
- `GET /api/categories` - 获取所有分类
- `GET /api/stats` - 获取统计信息

## 页面结构

### 主要页面
- **首页 (`/`)**：药方列表展示和管理
- **搜索页 (`/search`)**：高级搜索功能
- **详情页 (`/detail/{id}`)**：药方详细信息

### 功能组件
- **左侧操作面板**：添加药方、筛选、统计信息
- **搜索栏**：快速搜索和匹配模式选择
- **结果展示**：列表/网格视图切换、分页

## 数据示例

系统预置了经典中药方数据：
- 银翘散 - 清热解毒类
- 六味地黄丸 - 滋阴补肾类
- 四君子汤 - 补益类
- 血府逐瘀汤 - 活血化瘀类
- 小柴胡汤 - 和解类

## 开发说明

### 目录结构
```
中药管理系统/
├── app.py              # Flask应用主文件
├── requirements.txt     # 依赖包列表
├── prescriptions.db    # SQLite数据库（自动创建）
├── static/             # 静态文件
│   ├── css/
│   │   └── style.css   # 自定义样式
│   └── js/
│       └── main.js     # JavaScript工具函数
└── templates/          # HTML模板
    ├── base.html       # 基础模板
    ├── index.html      # 首页
    ├── search.html     # 搜索页
    └── detail.html     # 详情页
```

### 自定义功能
- **关键词高亮**：搜索结果自动高亮匹配关键词
- **搜索历史**：localStorage保存最近10条搜索记录
- **响应式设计**：适配桌面和移动设备
- **Toast通知**：用户友好的操作反馈

## 部署说明

### 开发环境
```bash
python app.py
```

### 生产环境
建议使用WSGI服务器如Gunicorn：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 扩展功能

系统设计支持以下扩展：
- 用户认证和权限管理
- 药方图片上传
- 批量导入导出功能
- 数据分析和可视化
- 移动端APP API
- 云存储集成

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。