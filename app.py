from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from datetime import datetime
import re

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 支持中文JSON

# 数据库配置
DATABASE = 'prescriptions.db'

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    if not os.path.exists(DATABASE):
        conn = get_db()
        cursor = conn.cursor()
        
        # 创建药方表
        cursor.execute('''
            CREATE TABLE prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                efficacy TEXT NOT NULL,
                ingredients TEXT,
                usage TEXT,
                precautions TEXT,
                category VARCHAR(50),
                source VARCHAR(100),
                symptoms TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX idx_efficacy ON prescriptions(efficacy)')
        cursor.execute('CREATE INDEX idx_name ON prescriptions(name)')
        cursor.execute('CREATE INDEX idx_category ON prescriptions(category)')
        cursor.execute('CREATE INDEX idx_symptoms ON prescriptions(symptoms)')
        
        # 插入示例数据
        sample_data = [
            {
                'name': '银翘散',
                'efficacy': '清热解毒，辛凉透表，宣肺止咳',
                'ingredients': '金银花、连翘、桔梗、薄荷、竹叶、生甘草、荆芥穗、淡豆豉、牛蒡子',
                'usage': '水煎服，每日1剂，分2-3次温服',
                'precautions': '忌辛辣油腻，风寒感冒忌用',
                'category': '清热解毒类',
                'source': '《温病条辨》'
            },
            {
                'name': '六味地黄丸',
                'efficacy': '滋阴补肾，养肝明目，强筋骨',
                'ingredients': '熟地黄、山茱萸、山药、泽泻、茯苓、牡丹皮',
                'usage': '口服，每次8丸，每日2次',
                'precautions': '忌食辛辣，脾虚便溏者慎用',
                'category': '滋阴补肾类',
                'source': '《小儿药证直诀》'
            },
            {
                'name': '四君子汤',
                'efficacy': '益气健脾，补中益气，脾胃虚弱',
                'ingredients': '人参、白术、茯苓、炙甘草',
                'usage': '水煎服，每日1剂，分2次服',
                'precautions': '阴虚火旺者慎用',
                'category': '补益类',
                'source': '《太平惠民和剂局方》'
            },
            {
                'name': '血府逐瘀汤',
                'efficacy': '活血化瘀，行气止痛，胸中血瘀',
                'ingredients': '桃仁、红花、当归、生地黄、川芎、赤芍、牛膝、桔梗、柴胡、枳壳、甘草',
                'usage': '水煎服，每日1剂，分2次服',
                'precautions': '孕妇忌用，月经过多者慎用',
                'category': '活血化瘀类',
                'source': '《医林改错》'
            },
            {
                'name': '小柴胡汤',
                'efficacy': '和解少阳，疏肝解郁，调和脾胃',
                'ingredients': '柴胡、黄芩、半夏、人参、甘草、生姜、大枣',
                'usage': '水煎服，每日1剂，分3次服',
                'precautions': '肝阳上亢者慎用',
                'category': '和解类',
                'source': '《伤寒论》'
            }
        ]
        
        for data in sample_data:
            cursor.execute('''
                INSERT INTO prescriptions (name, efficacy, ingredients, usage, precautions, category, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['name'], data['efficacy'], data['ingredients'], data['usage'], 
                  data['precautions'], data['category'], data['source']))
        
        conn.commit()
        conn.close()
        print("数据库初始化完成，已插入示例数据")

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/detail/<int:prescription_id>')
def detail(prescription_id):
    """药方详情页"""
    return render_template('detail.html', prescription_id=prescription_id)


@app.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    """获取所有药方"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 分页参数
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    
    # 筛选参数
    category = request.args.get('category')
    
    query = 'SELECT * FROM prescriptions WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    prescriptions = [dict(row) for row in cursor.fetchall()]
    
    # 获取总数
    count_query = 'SELECT COUNT(*) as total FROM prescriptions WHERE 1=1'
    count_params = []
    if category:
        count_query += ' AND category = ?'
        count_params.append(category)
    
    cursor.execute(count_query, count_params)
    total = cursor.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'prescriptions': prescriptions,
        'total': total,
        'page': page,
        'limit': limit,
        'pages': (total + limit - 1) // limit
    })

@app.route('/api/prescriptions/<int:prescription_id>', methods=['GET'])
def get_prescription(prescription_id):
    """获取单个药方详情"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM prescriptions WHERE id = ?', (prescription_id,))
    prescription = cursor.fetchone()
    
    conn.close()
    
    if prescription:
        return jsonify(dict(prescription))
    else:
        return jsonify({'error': '药方不存在'}), 404

@app.route('/api/prescriptions/search', methods=['GET'])
def search_prescriptions():
    """搜索药方"""
    q = request.args.get('q', '').strip()
    match_type = request.args.get('match_type', 'fuzzy')  # fuzzy, exact, and, or
    limit = int(request.args.get('limit', 20))
    page = int(request.args.get('page', 1))
    offset = (page - 1) * limit
    
    if not q:
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if match_type == 'exact':
            # 精确匹配
            query = '''
                SELECT * FROM prescriptions 
                WHERE efficacy LIKE ? OR name LIKE ? OR ingredients LIKE ? OR symptoms LIKE ?
                ORDER BY id DESC LIMIT ? OFFSET ?
            '''
            params = [f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%', limit, offset]
            
        elif match_type == 'and':
            # AND逻辑：所有关键词都要匹配
            keywords = [kw.strip() for kw in q.split() if kw.strip()]
            conditions = []
            params = []
            
            for keyword in keywords:
                conditions.append('(efficacy LIKE ? OR name LIKE ? OR ingredients LIKE ? OR symptoms LIKE ?)')
                params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
            
            query = f'''
                SELECT * FROM prescriptions 
                WHERE {' AND '.join(conditions)}
                ORDER BY id DESC LIMIT ? OFFSET ?
            '''
            params.extend([limit, offset])
            
        elif match_type == 'or':
            # OR逻辑：任一关键词匹配即可
            keywords = [kw.strip() for kw in q.split() if kw.strip()]
            conditions = []
            params = []
            
            for keyword in keywords:
                conditions.append('(efficacy LIKE ? OR name LIKE ? OR ingredients LIKE ? OR symptoms LIKE ?)')
                params.extend([f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'])
            
            query = f'''
                SELECT * FROM prescriptions 
                WHERE {' OR '.join(conditions)}
                ORDER BY id DESC LIMIT ? OFFSET ?
            '''
            params.extend([limit, offset])
            
        else:
            # 模糊匹配（默认）
            query = '''
                SELECT * FROM prescriptions 
                WHERE efficacy LIKE ? OR name LIKE ? OR ingredients LIKE ? OR symptoms LIKE ?
                ORDER BY id DESC LIMIT ? OFFSET ?
            '''
            params = [f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%', limit, offset]
        
        cursor.execute(query, params)
        prescriptions = [dict(row) for row in cursor.fetchall()]
        
        # 高亮关键词
        highlighted_prescriptions = []
        for prescription in prescriptions:
            highlighted = prescription.copy()
            if isinstance(highlighted['efficacy'], str):
                highlighted['efficacy'] = highlight_keywords(highlighted['efficacy'], q)
            if isinstance(highlighted['name'], str):
                highlighted['name'] = highlight_keywords(highlighted['name'], q)
            highlighted_prescriptions.append(highlighted)
        
        conn.close()
        
        return jsonify({
            'prescriptions': highlighted_prescriptions,
            'total': len(highlighted_prescriptions),
            'page': page,
            'limit': limit,
            'query': q,
            'match_type': match_type
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': f'搜索失败: {str(e)}'}), 500

@app.route('/api/prescriptions', methods=['POST'])
def create_prescription():
    """创建新药方"""
    data = request.get_json()
    
    required_fields = ['name', 'efficacy']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 字段是必需的'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO prescriptions (name, efficacy, ingredients, usage, precautions, category, source, symptoms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['efficacy'],
        data.get('ingredients', ''),
        data.get('usage', ''),
        data.get('precautions', ''),
        data.get('category', ''),
        data.get('source', ''),
        data.get('symptoms', '')
    ))
    
    prescription_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': prescription_id, 'message': '药方创建成功'}), 201

@app.route('/api/prescriptions/<int:prescription_id>', methods=['PUT'])
def update_prescription(prescription_id):
    """更新药方"""
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查药方是否存在
    cursor.execute('SELECT id FROM prescriptions WHERE id = ?', (prescription_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '药方不存在'}), 404
    
    # 更新字段
    updates = []
    params = []
    
    for field in ['name', 'efficacy', 'ingredients', 'usage', 'precautions', 'category', 'source', 'symptoms']:
        if field in data:
            updates.append(f'{field} = ?')
            params.append(data[field])
    
    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(prescription_id)
        
        cursor.execute(f'''
            UPDATE prescriptions 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        
        conn.commit()
    
    conn.close()
    return jsonify({'message': '药方更新成功'})

@app.route('/api/prescriptions/<int:prescription_id>', methods=['DELETE'])
def delete_prescription(prescription_id):
    """删除药方"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM prescriptions WHERE id = ?', (prescription_id,))
    affected_rows = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    if affected_rows > 0:
        return jsonify({'message': '药方删除成功'})
    else:
        return jsonify({'error': '药方不存在'}), 404

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT category FROM prescriptions WHERE category IS NOT NULL ORDER BY category')
    categories = [row['category'] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(categories)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 总药方数
    cursor.execute('SELECT COUNT(*) as total FROM prescriptions')
    total = cursor.fetchone()['total']
    
    # 分类统计
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM prescriptions 
        WHERE category IS NOT NULL 
        GROUP BY category 
        ORDER BY count DESC
    ''')
    category_stats = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'total_prescriptions': total,
        'category_stats': category_stats
    })

def highlight_keywords(text, keywords):
    """高亮关键词"""
    if not text or not keywords:
        return text
    
    keyword_list = [kw.strip() for kw in keywords.split() if kw.strip()]
    if not keyword_list:
        return text
    
    highlighted_text = text
    for keyword in keyword_list:
        # 使用正则表达式进行不区分大小写的替换
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        highlighted_text = pattern.sub(f'<mark>{keyword}</mark>', highlighted_text)
    
    return highlighted_text

def add_symptoms_column():
    """为现有数据库添加symptoms字段"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 检查symptoms字段是否存在
        cursor.execute('PRAGMA table_info(prescriptions)')
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'symptoms' not in columns:
            cursor.execute('ALTER TABLE prescriptions ADD COLUMN symptoms TEXT')
            cursor.execute('CREATE INDEX idx_symptoms ON prescriptions(symptoms)')
            conn.commit()
            print("已添加symptoms字段")
    except Exception as e:
        print(f"添加symptoms字段时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 添加symptoms字段（用于现有数据库）
    add_symptoms_column()
    
    # 启动应用
    app.run(debug=False, host='0.0.0.0', port=5001)