import argparse

from agent_growth import AgentGrowthClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render customer support runtime guidance.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--message", default="Why was my refund rejected?")
    parser.add_argument("--agent-id", default="support_agent")
    parser.add_argument("--domain", default="customer_support")
    parser.add_argument("--intent", default="refund_question")
    parser.add_argument("--risk-level", default="medium", choices=["low", "medium", "high"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = AgentGrowthClient(args.base_url)
    guidance = client.get_guidance(
        agent_id=args.agent_id,
        domain=args.domain,
        intent=args.intent,
        context={"message": args.message},
        risk_level=args.risk_level,
    )
    print(guidance.to_prompt())


if __name__ == "__main__":
    main()
