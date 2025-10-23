# Claude Prompt Tracker - 测试套件

这个目录包含Claude Prompt Tracker系统的完整测试套件，包括单元测试、集成测试和测试数据。

## 文件结构

```
tests/
├── README.md                   # 本文件
├── test_prompt_tracker.py      # 单元测试套件
├── test_data.py               # 测试数据生成器
├── run_tests.py               # 手动测试运行器
└── test_data/                 # 生成的测试数据
    ├── scenario_*.json        # 完整场景测试数据
    └── individual_events/     # 单独事件测试文件
        └── scenario_*/
            └── *.json
```

## 运行测试

### 1. 单元测试

运行完整的单元测试套件：

```bash
cd /Users/sam/.claude/scripts/tests
python -m unittest test_prompt_tracker.py -v
```

### 2. 手动测试

#### 交互式测试
```bash
python run_tests.py
```

#### 运行所有场景
```bash
python run_tests.py all [延迟秒数]
```

#### 运行特定场景
```bash
python run_tests.py scenario_1 [延迟秒数]
```

#### 验证数据库
```bash
python run_tests.py verify
```

### 3. 单个事件测试

使用生成的JSON文件手动测试单个事件：

```bash
cat test_data/individual_events/scenario_1/01_userpromptsubmit.json | python ../ccnotify.py
```

## 测试场景说明

根据设计文档，包含以下6个测试场景：

### 场景1：单次完整prompt流程
- UserPromptSubmit → Stop
- 测试基本的prompt记录和完成通知

### 场景2：包含等待用户输入的完整流程  
- UserPromptSubmit → Notification（等待输入）→ Stop
- 测试等待通知功能

### 场景3：同一会话的连续多个prompt
- 测试seq字段的自动递增功能
- 3个连续的prompt-stop循环

### 场景4：多个不同会话同时进行
- 测试并发会话处理
- 3个不同会话的prompt和stop事件

### 场景5：包含多次等待和通知的会话
- 复杂的交互流程
- 多种类型的通知事件

### 场景6：不同工作目录的会话
- 测试不同项目目录的处理
- Python、Node.js、文档项目

## 验证检查项

测试完成后，应验证以下内容：

1. **数据库记录正确性**
   - 每个UserPromptSubmit事件都有对应记录
   - session_id、prompt、dirname字段正确填充

2. **序号自增功能**
   - 同一session_id下的记录seq值正确递增
   - 不同session_id之间的seq值独立

3. **时间字段更新**
   - Stop事件正确更新stoped_at字段
   - Notification事件正确更新lastWaitUserAt字段

4. **通知系统**
   - 任务完成时发送带耗时的通知
   - 等待输入时发送提醒通知
   - 使用正确的项目目录名作为标题

5. **错误处理**
   - 处理无效JSON输入
   - 处理缺失字段
   - 不会因为异常而崩溃

## 数据库查询示例

测试完成后，可以直接查询数据库验证结果：

```bash
# 连接到数据库
sqlite3 ~/.claude/ccnotify/ccnotify.db

# 查看所有记录
SELECT session_id, seq, dirname, prompt, 
       created_at, stoped_at, lastWaitUserAt 
FROM prompt 
ORDER BY created_at;

# 按会话统计
SELECT session_id, COUNT(*) as count, MAX(seq) as max_seq
FROM prompt 
GROUP BY session_id;

# 查看完成状态
SELECT 
  COUNT(CASE WHEN stoped_at IS NOT NULL THEN 1 END) as completed,
  COUNT(CASE WHEN stoped_at IS NULL THEN 1 END) as incomplete
FROM prompt;
```

## 故障排除

### 常见问题

1. **"terminal-notifier not found"**
   - 这是正常的，如果没安装terminal-notifier，通知会被跳过
   - 安装：`brew install terminal-notifier`

2. **数据库权限错误**
   - 确保~/.claude目录存在并有写权限
   - 检查数据库文件权限

3. **JSON解析错误**
   - 检查测试数据格式是否正确
   - 确保JSON文件编码为UTF-8

### 调试输出

所有调试信息都输出到stderr，可以查看：

```bash
python run_tests.py scenario_1 2>&1 | grep "PROMPT_TRACKER"
```

## 扩展测试

如需添加新的测试场景：

1. 在`test_data.py`中添加新的场景数据生成方法
2. 在`TestDataGenerator.get_all_scenarios()`中注册新场景
3. 运行`python test_data.py`重新生成测试数据文件
4. 使用`run_tests.py`测试新场景