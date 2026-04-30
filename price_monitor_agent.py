from typing import Dict, Any, List
from datetime import datetime, timedelta
import statistics
from .base_agent import BaseAgent, AgentContext, AgentResult

class PriceMonitorAgent(BaseAgent):
    """
    价格监控专家 - 竞品价格追踪、异常检测、告警 [citation:6][citation:9]
    """
    
    async def execute(self, context: AgentContext) -> AgentResult:
        task = context.input_data.get("task", "")
        
        # 1. 解析监控目标
        targets = await self._parse_targets(task)
        
        # 2. 采集价格数据
        price_data = await self._collect_prices(targets)
        
        # 3. 异常检测（3sigma原则） [citation:6]
        anomalies = await self._detect_anomalies(price_data)
        
        # 4. 生成告警和报表
        alerts = await self._generate_alerts(anomalies)
        
        return AgentResult(
            success=True,
            output={
                "price_data": price_data,
                "anomalies": anomalies,
                "alerts": alerts,
                "report_summary": await self._generate_summary(price_data, anomalies)
            }
        )
    
    async def _detect_anomalies(self, price_data: List[Dict]) -> List[Dict]:
        """
        异常波动检测算法 [citation:6]
        采用3sigma原则：|价格 - 均值| > 3 * 标准差 视为异常
        """
        anomalies = []
        
        for product in price_data:
            prices = [p["price"] for p in product.get("history", [])]
            if len(prices) < 7:  # 至少7个数据点
                continue
                
            window_size = min(7, len(prices))
            window = prices[-window_size:]
            
            mean = statistics.mean(window)
            std = statistics.stdev(window) if len(window) > 1 else 0
            current_price = prices[-1]
            
            if std > 0 and abs(current_price - mean) > 3 * std:
                anomalies.append({
                    "sku": product["sku"],
                    "current_price": current_price,
                    "expected_price": mean,
                    "deviation": (current_price - mean) / mean,
                    "timestamp": datetime.now().isoformat()
                })
        
        return anomalies
    
    async def _generate_alerts(self, anomalies: List[Dict]) -> List[Dict]:
        """根据异常类型生成不同优先级告警 [citation:6]"""
        alerts = []
        
        for anomaly in anomalies:
            deviation = anomaly["deviation"]
            
            if deviation < -0.3:  # 降价30%以上
                priority = "紧急"
                alert_type = "低价预警"
                action = "建议补货或调整定价策略"
            elif deviation > 0.5:  # 涨价50%以上
                priority = "高"
                alert_type = "波动预警"
                action = "检查竞品动态"
            else:
                priority = "中"
                alert_type = "常规监控"
                action = "持续跟踪"
            
            alerts.append({
                **anomaly,
                "alert_type": alert_type,
                "priority": priority,
                "suggested_action": action
            })
        
        return alerts
