from agent import HybridMemoryAgent


def seed_memories(agent: HybridMemoryAgent) -> None:
    agent.remember(
        """
        User da doc ghi chu ve Kubernetes Horizontal Pod Autoscaler. HPA autoscaling pod
        dua tren CPU, memory hoac custom metrics va phu hop khi workload tang giam nhanh.

        User da doc tai lieu ve Cluster Autoscaler, node pool, pending pods va cach scale-out
        ha tang Kubernetes khi cluster khong con du tai nguyen.
        """
    )
    agent.remember(
        """
        User quan tam den cloud security, dac biet la IAM least privilege, network policy,
        secret management va cach audit permission tren AWS/GCP.
        """
    )
    agent.remember(
        """
        User dang hoc Terraform de quan ly infrastructure as code. User thich vi du thuc hanh,
        checklist ngan, va giai thich bang tieng Viet truoc khi di vao thuat ngu English.
        """
    )
    agent.remember(
        """
        User da xem mot bai ve AI engineering pipeline: embedding, vector store, reranking va
        cach ket hop retrieval voi user profile de ca nhan hoa cau tra loi.
        """
    )


def main() -> None:
    agent = HybridMemoryAgent(top_k=3)
    seed_memories(agent)

    queries = [
        "Toi da doc gi ve Kubernetes?",
        "Recommend doc gi tiep",
        "Toi dang quan tam gi gan day?",
        "Tai lieu ve tu dong mo rong ha tang?",
        "Cho toi summary cloud security",
    ]

    for index, query in enumerate(queries, 1):
        print("=" * 80)
        print(f"Query {index}: {query}")
        print("-" * 80)
        print(agent.recall(query))


if __name__ == "__main__":
    main()
