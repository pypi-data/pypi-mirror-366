from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="calculator-app", host="127.0.0.1", port=8060)

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b


def main():
    transport = "stdio"
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Invalid transport: {transport}")


if __name__ == "__main__":
    main()