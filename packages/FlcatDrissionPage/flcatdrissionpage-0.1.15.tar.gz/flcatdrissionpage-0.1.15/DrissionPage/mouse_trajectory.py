import loguru
import requests
import time
import json

def request_trajectory(target_point, endpoint='http://mouse-trajectory.flcat.top/infer', max_retries=3):
    """
    带重试机制的轨迹请求函数
    :param endpoint: 服务地址，例如 "http://mouse-trajectory.flcat.top/infer"
    :param target_point: 目标终点坐标，格式为 (x, y)
    :param max_retries: 最大重试次数（默认3次）
    :return: 请求结果字典 或 None
    """
    headers = {"Content-Type": "application/json"}
    payload = {"x": target_point[0], "y": target_point[1]}
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                endpoint,
                data=json.dumps(payload),
                headers=headers,
                timeout=10  # 设置10秒超时
            )
            
            # 检查HTTP状态码
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            error_type = type(e).__name__
            loguru.logger.error(f"第{attempt+1}次尝试失败 - 错误类型: {error_type}")
            
            if attempt < max_retries:
                # 指数退避策略（1, 2, 4秒）
                wait_time = 2 ** attempt
                loguru.logger.error(f"{wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                loguru.logger.error(f"达到最大重试次数（{max_retries}次），请求失败")
                return None

# 使用示例
if __name__ == "__main__":
    target_point = (500.0, 300.0)  # 替换为实际坐标
    
    loguru.logger.debug(f"正在请求轨迹生成服务，目标点：{target_point}")
    result = request_trajectory(target_point)
    
    if result:
        loguru.logger.debug("\n生成的轨迹数据：")
        loguru.logger.debug(f"轨迹点数: {result['point_count']}")
        loguru.logger.debug("坐标点数据：")
        for point in result['trajectory']:
            loguru.logger.debug(f"  ({point[0]:.2f}, {point[1]:.2f})")
    else:
        loguru.logger.error("请求失败，请检查服务状态或网络连接")