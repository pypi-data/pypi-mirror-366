def main():
    """A MCP server to query ticket information in 12306."""
    import argparse
    from redis import Redis
    from mcp_12306.mcp_12306_server import start_server

    parser = argparse.ArgumentParser(
        description="A MCP server to query ticket information in 12306."
    )
    parser.add_argument("--redis", type=int, help="指定启动本地 Redis 服务的端口")
    args = parser.parse_args()

    redis_client = None
    if args.redis:
        try:
            redis_client = Redis(host="localhost", port=args.redis, db=0)
            print("启动 Redis 成功")
        except Exception as e:
            print("启动 Redis 失败:", e)
            redis_client = None

    # 确保始终传递所有必需的参数
    start_server(redis_client)

if __name__ == "__main__":
    main()