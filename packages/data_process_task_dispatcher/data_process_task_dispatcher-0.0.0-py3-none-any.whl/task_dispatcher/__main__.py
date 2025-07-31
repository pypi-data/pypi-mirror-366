"""
Main entry point for starting message queue consumers.
"""

from task_dispatcher.consumers.paper_match import paper_match_consumer


def main():
    """Start all message queue consumers."""
    print("hello")
    # Start all consumers
    # paper_match_consumer.start()


if __name__ == "__main__":
    main()
