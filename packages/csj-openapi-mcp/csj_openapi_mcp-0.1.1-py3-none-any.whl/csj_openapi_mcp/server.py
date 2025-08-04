from fastmcp.server import FastMCP


# ==== start 该部分编写在包中，媒体import即可 ========
def Create_server():
    mcp = FastMCP(name="File Demo", instructions="Get files from the server or URL.")

    @mcp.tool(
        name="获取天气",  # Custom tool name for the LLM
        description="获取当天当地的天气 location: 地区",  # Custom description
    )
    def get_weather(location: str):
        return location + " 阴天有雨"

    return mcp


# ===== end =======


# import 包之后，获取create_server().媒体在本地或者自身服务器上进行部署
def main():
    Create_server().run(transport="stdio")


if __name__ == '__main__':
    main()
