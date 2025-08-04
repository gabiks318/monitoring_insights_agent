import asyncio
from agent import CloudWatchInsightsAgent

def main():
    agent = CloudWatchInsightsAgent()
    prompt = input("Enter a CloudWatch question: ")
    answer = agent.run(prompt)
    print("\nResult:\n", answer)

if __name__ == "__main__":
    main()
