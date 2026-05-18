# 部署文档索引

---

## 一、部署架构

```
                    ┌─────────────────┐
                    │   Nginx (443)   │
                    │   TLS1.3+限流   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  FastAPI (8000)  │
                    │  Gunicorn Workers│
                    └────────┬────────┘
                             │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
│ cad-data-quality│ │ cad-model-pool│ │ cad-fusion-eng │ 
└────────────────┘  └───────────────┘  └───────────────┘
```

---

## 二、部署模式

### 2.1 蓝绿部署

```
蓝绿部署流程：
1. 新版本部署到Green组（待机）
2. 流量切换10%到Green
3. 监控无异常后，切换100%
4. Green变为新的Blue组
5. 旧版本待机作为新的Green组
```

### 2.2 热切换

- 模型文件存储在MinIO
- LoadBalancer检测到新模型后自动reload
- 服务不中断，模型切换时间<30秒

---

## 三、部署步骤

### 3.1 环境检查

```bash
# 1. 检查依赖
docker --version
docker-compose --version
kubectl version

# 2. 检查资源
kubectl top nodes
kubectl get pvc
```

### 3.2 部署流程

```bash
# 1. 拉取镜像
docker pull cad-service:latest

# 2. 更新配置
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# 3. 滚动更新
kubectl rollout restart deployment/cad-service

# 4. 验证
kubectl rollout status deployment/cad-service
```

---

## 四、运维手册

### 4.1 日常巡检

| 检查项 | 频率 | 命令 |
|--------|------|------|
| Pod状态 | 每日 | kubectl get pods |
| 日志错误 | 每日 | kubectl logs -f cad-service --tail=100 |
| 资源使用 | 每日 | kubectl top pods |
| 磁盘使用 | 每周 | kubectl exec cad-service -- df -h |

### 4.2 故障处理

| 故障 | 排查命令 | 处理措施 |
|------|---------|---------|
| Pod无法启动 | kubectl describe pod | 检查镜像/配置 |
| 服务响应慢 | kubectl top pod | 增加副本数 |
| 模型加载失败 | 检查MinIO连接 | 重新上传模型 |
| 降级触发 | 检查Redis连接 | 恢复后自动回滚 |
