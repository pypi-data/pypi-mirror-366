# -*- coding: utf-8 -*-
import asyncio
import anyio
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.shared._httpx_utils import create_mcp_http_client
import logging
from mcp_12306.query_12306 import TrainInfoQuery
from datetime import date 
import json
from redis import Redis
import re
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_server(redis_client: Optional[Redis] = None) -> int:
    print("start server " + ("with redis_client" if redis_client else "without redis_client"))  
    # 实例化查询引擎
    try:
        query_engine = TrainInfoQuery()
        logger.info("12306查询引擎初始化成功")
        print("12306查询引擎初始化成功")
    except Exception as e:
        logger.error(f"查询引擎初始化失败: {e}")
        print(f"查询引擎初始化失败: {e}")
        exit(1)

    app = Server("mcp-12306-server")

    # 将车站名转为车站代码
    def station_name_to_code(station_name: str) -> str:
        # 检查车站名并返回车站名
        def check_station(station: str) -> tuple[bool, Optional[str]]:
            if station in query_engine.station_name_dict:
                return True, station
            # 可能是因为输入的是城市名称或带了市/站字，需要转换为车站代码
            if station not in query_engine.city_station_dict:
                if station[-1] == "站":
                    station = station[:-1]
                elif station[-1] == "市":
                    station = station[:-1]
            if station in query_engine.city_station_dict:
                return True, station
            return False, None

        name_is_valid, valid_station_name = check_station(station_name)
        # 车站名不合法
        if not name_is_valid or not valid_station_name:
            raise ValueError(f"Invalid station name: {station_name}")
        return query_engine.get_station_code_by_name(valid_station_name)

    async def query_train_info(arguments: dict) -> list[types.ContentBlock]:
        # 必须参数
        for param in ["train_no", "train_date"]:
            if param not in arguments:
                raise ValueError(f"Missing required argument '{param}'")
        data = await query_engine.query_train_info(
            train_no=arguments["train_no"],
            train_date=arguments["train_date"]
        )
        return [types.TextContent(type="text", text=json.dumps(data))]
    
    async def query_train_price(arguments: dict) -> list[types.ContentBlock]:
        print(arguments)
        # 必须参数
        for param in ["from_station", "to_station", "train_date"]:
            if param not in arguments:
                raise ValueError(f"Missing required argument '{param}'")
        from_station = station_name_to_code(arguments["from_station"])
        to_station = station_name_to_code(arguments["to_station"])
        data = await query_engine.query_train_price(
            from_station=from_station,
            to_station=to_station,
            train_date=arguments["train_date"]
        )
        return [types.TextContent(type="text", text=json.dumps(data))]

    async def query_train_id(arguments: dict) -> list[types.ContentBlock]:
        # 必须参数
        for param in ["train_no", "train_date"]:
            if param not in arguments:
                raise ValueError(f"Missing required argument '{param}'")
        data = await query_engine.query_train_id(
            train_no=arguments["train_no"],
            train_date=arguments["train_date"]
        )
        return types.TextContent(type="text", text=json.dumps(data))

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
        if name == "query_tickets":
            return await query_tickets(arguments)
        elif name == "get_station_code":
            return await get_station_code(arguments)
        elif name == "get_station_name":
            return await get_station_name(arguments)
        elif name == "query_train_info":
            return await query_train_info(arguments)
        elif name == "query_train_price":
            return await query_train_price(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def query_tickets(arguments: dict) -> list[types.ContentBlock]:
        # 必须参数
        for param in ["from_station", "to_station"]:
            if param not in arguments:
                raise ValueError(f"Missing required argument '{param}'")
        # 可选参数，建议填写，不填则填默认值
        if "train_date" not in arguments:
            arguments["train_date"] = date.today().strftime("%Y-%m-%d")
        if "purpose_codes" not in arguments:
            arguments["purpose_codes"] = "ADULT"
        
        # 对参数进行检查，判断格式是否符合要求
        from_station = arguments["from_station"]
        to_station = arguments["to_station"]
        train_date = arguments["train_date"]
        purpose_codes = arguments["purpose_codes"]

        # 检查 train_date 格式
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, train_date):
            raise ValueError(f"Invalid date format: {train_date}，应为YYYY-MM-DD")
        try:
            datetime.strptime(train_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date: {train_date}，无法转换为日期")
        if not query_engine.is_date_can_query(train_date):
            raise ValueError(f"Invalid date: {train_date}，查询日期超出范围")
        if purpose_codes not in ["ADULT", "0X00"]:
            raise ValueError(f"Invalid purpose codes: {purpose_codes}")

        # 其他参数校验
        # 检查出发车站与到达车站并，将车站名转为车站代码
        from_station_code = station_name_to_code(from_station)
        to_station_code = station_name_to_code(to_station)

        # redis 缓存查询数据
        redis_key = f"ticket:{from_station_code}:{to_station_code}:{train_date}:{purpose_codes}"
        print("redis_key:", redis_key)
        if redis_client:
            result = await redis_client.get(redis_key)
            if result:
                return [types.TextContent(type="text", text=result.decode("utf-8"))]

        # redis没有获取到数据才进行请求     
        result = await query_engine.query_left_tickets(
            from_station=from_station_code,
            to_station=to_station_code,
            train_date=train_date,
            purpose_codes=purpose_codes,
        )

        # 将结果缓存到redis
        # 设置key有效时间为5分钟    ticket:5min
        if redis_client:
            cache_time = 2
            cache_data = json.dumps(result)
            await redis_client.set(redis_key, cache_data, ex=cache_time)

        # 筛选查询的信息，并返回
        # filtered_result = TrainInfoQuery.filter_train_info(query={}, result=result)
        # filtered_result = json.dumps(filtered_result)
        return [types.TextContent(type="text", text=json.dumps(result))]
    
    # @app.call_tool()
    async def get_station_code(arguments: dict) -> list[types.ContentBlock]:
        if "station_name" not in arguments:
            raise ValueError("Missing required argument 'station_name'")
        station_code = query_engine.get_station_code_by_name(arguments["station_name"])
        return [types.TextContent(type="text", text=station_code)]
    
    # @app.call_tool()
    async def get_station_name(arguments: dict) -> list[types.ContentBlock]:
        if "station_code" not in arguments:
            raise ValueError("Missing required argument 'station_code'")
        query_station_code = arguments["station_code"].upper()
        for station_name, station_code in query_engine.station_code_dict.items():
            if station_code == query_station_code:
                return [types.TextContent(type="text", text=station_name)]
        raise ValueError(f"Invalid station code: {arguments['station_code']}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            # 工具描述
            types.Tool(
                name="query_tickets",
                title="query tickets",
                description="查询火车票信息，只需要传入出发车站名、到达车站名、出发日期、乘客类型，如: 北京, 汉口, 2025-07-15, ADULT",
                inputSchema={
                    "type": "object",
                    "required": ["from_station", "to_station"],
                    "properties": {
                        "from_station": {
                            "type": "string",
                            "description": "出发车站的中文车站名，如: 北京",
                        },
                        "to_station": {
                            "type": "string",
                            "description": "到达车站的中文车站名，如: 汉口",
                        },
                        "train_date": {
                            "type": "string",
                            "description": "出发日期，如: 2025-07-15",
                        },
                        "purpose_codes": {
                            "type": "string",
                            "description": "乘客类型，默认是成人：ADULT, 学生：0X00",
                        },
                    },
                },
            ),
            types.Tool(
                name="query_train_info",
                title="query train info",
                description="查询火车车次信息，包括时刻表、途径站、停靠时间等信息",
                inputSchema={
                    "type": "object",
                    "required": ["train_no", "train_date"],
                    "properties": {
                        "train_no": {
                            "type": "string",
                            "description": "车次编号，如: G1234",
                        },
                        "train_date": {
                            "type": "string",
                            "description": "出发日期，如: 2025-07-15",
                        },
                    },
                },
            ),
            types.Tool(
                name="query_train_price",
                title="query train price",
                description="查询火车的车票价格，需要出发车站名，到达车站名，出发日期",
                inputSchema={
                    "type": "object",
                    "required": ["from_station", "to_station", "train_date"],
                    "properties": {
                        "from_station": {
                            "type": "string",
                            "description": "出发车站，中文车站名，如: 北京",
                        },
                        "to_station": {
                            "type": "string",
                            "description": "到达车站，中文车站名，如: 汉口",
                        },
                        "train_date": {
                            "type": "string",
                            "description": "出发日期，如: 2025-07-15",
                        },
                    },
                },
            ),
            types.Tool(
                name="get_station_code",
                title="get station code",
                description="获取车站中文名的code(代号/代码)",
                inputSchema={
                    "type": "object",
                    "required": ["station_name"],
                    "properties": {
                        "station_name": {
                            "type": "string",
                            "description": "车站的中文名",
                        },
                    },
                },
            )
        ]

   
    from mcp.server.stdio import stdio_server

    async def arun():
        async with stdio_server() as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )

    print("12306 MCP server is running: stdio")
    anyio.run(arun)

    
    return 0

if __name__ == "__main__":
    start_server()
