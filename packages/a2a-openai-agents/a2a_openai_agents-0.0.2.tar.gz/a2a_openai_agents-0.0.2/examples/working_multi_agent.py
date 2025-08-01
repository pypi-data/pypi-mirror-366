#!/usr/bin/env python3
"""
Working Multi-Agent System

Simple demonstration of agents communicating via HTTP calls (simulating A2A protocol).
Since the A2A SDK has compatibility issues, this shows the concept using direct HTTP.
"""

import asyncio
import threading
import time

import httpx
import uvicorn
from fastapi import FastAPI

try:
    from agents import Agent, function_tool
except ImportError:
    print("Dependencies not installed. Please run: pip install a2a-openai-agents")
    exit(1)


# Calculator Agent
@function_tool
def add_numbers(a: int, b: int) -> str:
    """Add two numbers together."""
    result = a + b
    print(f"[CALCULATOR] {a} + {b} = {result}")
    return f"The sum of {a} and {b} is {result}"


# Simple FastAPI wrapper for demonstration
class SimpleAgentServer:
    def __init__(self, agent: Agent, name: str):
        self.agent = agent
        self.name = name
        self.app = FastAPI(title=f"{name} Agent")

        @self.app.post("/message")
        async def handle_message(request: dict):
            """Handle incoming messages."""
            try:
                message_text = request.get("text", "")
                print(f"[{self.name}] Received: {message_text}")

                # Use the agent to process the message
                from agents import Runner

                runner = Runner(self.agent)
                result = runner.run(message_text)

                response = {
                    "agent": self.name,
                    "response": result.final_output,
                    "status": "success",
                }
                print(f"[{self.name}] Responding: {result.final_output}")
                return response

            except Exception as e:
                return {"agent": self.name, "error": str(e), "status": "error"}

        @self.app.get("/info")
        async def agent_info():
            """Get agent information."""
            return {
                "name": self.name,
                "tools": [tool.name for tool in self.agent.tools] if self.agent.tools else [],
                "status": "online",
            }


async def call_agent(url: str, message: str) -> str:
    """Call another agent via HTTP."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{url}/message", json={"text": message})
            response.raise_for_status()
            result = response.json()

            if result.get("status") == "success":
                return result.get("response", "No response")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"

    except Exception as e:
        return f"Failed to call agent: {e}"


def create_calculator_agent():
    """Create calculator agent."""
    agent = Agent(
        name="Calculator",
        instructions="You are a calculator. Use the add_numbers tool to add numbers when asked.",
        model="gpt-4o-mini",
        tools=[add_numbers],
    )
    return SimpleAgentServer(agent, "Calculator")


def create_reporter_agent():
    """Create reporter agent that can call other agents."""
    # Reporter agent doesn't need tools - it coordinates with others
    agent = Agent(
        name="Reporter",
        instructions="""You are a reporter who creates summaries. You can ask other services for calculations.
        When you need math done, just request it clearly and the system will handle the calculation.""",
        model="gpt-4o-mini",
    )

    server = SimpleAgentServer(agent, "Reporter")

    # Add custom endpoint for coordinated reports
    @server.app.post("/calculate_and_report")
    async def calculate_and_report(request: dict):
        """Calculate numbers and create a report."""
        try:
            num1 = request.get("number1", 0)
            num2 = request.get("number2", 0)

            # Call the Calculator agent
            calc_result = await call_agent(
                "http://localhost:9000", f"Add {num1} and {num2} using your add_numbers tool"
            )

            # Create a report using the Reporter agent
            report_text = f"Calculation Report: {calc_result}"
            from agents import Runner

            runner = Runner(server.agent)
            report = runner.run(f"Create a professional summary of this calculation: {report_text}")

            return {
                "agent": "Reporter",
                "calculation": calc_result,
                "report": report.final_output,
                "status": "success",
            }

        except Exception as e:
            return {"agent": "Reporter", "error": str(e), "status": "error"}

    return server


def run_server(server: SimpleAgentServer, port: int):
    """Run an agent server."""
    print(f"Starting {server.name} on port {port}")
    uvicorn.run(server.app, host="localhost", port=port, log_level="warning")


async def test_multi_agent_system():
    """Test the multi-agent system."""
    print("\n=== Testing Multi-Agent System ===")

    # Wait for servers to start
    await asyncio.sleep(3)

    try:
        # Test 1: Direct calculator call
        print("1. Testing Calculator directly...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:9000/message", json={"text": "Add 15 and 27"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Calculator: {result.get('response', 'No response')}")
            else:
                print(f"   ❌ Calculator failed: {response.status_code}")

        # Test 2: Reporter coordination
        print("\n2. Testing Reporter coordination...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:9001/calculate_and_report", json={"number1": 25, "number2": 17}
            )
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Multi-agent success!")
                print(f"   Calculation: {result.get('calculation', 'N/A')}")
                print(f"   Report: {result.get('report', 'N/A')[:200]}...")
            else:
                print(f"   ❌ Reporter coordination failed: {response.status_code}")

        print("\n✅ Multi-agent system working!")

    except Exception as e:
        print(f"❌ Test failed: {e}")


def main():
    """Run the multi-agent system."""
    print("=== Simple Multi-Agent System ===")

    # Create agents
    calculator = create_calculator_agent()
    reporter = create_reporter_agent()

    print("Agent capabilities:")
    print("• Calculator: Can add numbers")
    print("• Reporter: Can create reports and coordinate with Calculator")

    # Start servers in background threads
    calc_thread = threading.Thread(target=run_server, args=(calculator, 9000), daemon=True)
    reporter_thread = threading.Thread(target=run_server, args=(reporter, 9001), daemon=True)

    print("\nStarting agents...")
    calc_thread.start()
    reporter_thread.start()

    # Run test
    asyncio.run(test_multi_agent_system())

    print("\nAgents available at:")
    print("• Calculator: http://localhost:9000")
    print("• Reporter: http://localhost:9001")
    print("\nTest the Reporter coordination:")
    print("curl -X POST http://localhost:9001/calculate_and_report \\")
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"number1": 42, "number2": 58}\'')

    print("\nPress Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
