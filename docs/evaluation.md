# RAG Evaluation Methodology & Metrics

This document outlines the mathematical formulas and methodology used to evaluate the Universal Multimodal RAG Assistant.

---

## 1. Retrieval Metrics

### 1.1 Recall@K
The proportion of relevant ground-truth evidence chunks retrieved within the top $K$ candidates ($K=5$):
$$\text{Recall@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{|\text{Relevant}|}$$

### 1.2 Precision@K
The fraction of retrieved chunks in top $K$ that are relevant to the query:
$$\text{Precision@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{K}$$

### 1.3 Mean Reciprocal Rank (MRR)
Measures where the first relevant document chunk appears in the ranked list:
$$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
Where $\text{rank}_i$ is the rank of the first relevant chunk for query $i$.

### 1.4 Hit Rate
The percentage of queries for which at least one correct supporting document chunk was retrieved in the top $K$:
$$\text{Hit Rate} = \frac{\sum_{i=1}^{|Q|} \mathbb{I}(\text{rank}_i \le K)}{|Q|}$$

---

## 2. Generation & Groundedness Metrics

### 2.1 Faithfulness / Groundedness
The percentage of factual statements made in the generated answer that are directly supported by the retrieved evidence chunks:
$$\text{Faithfulness} = \frac{|\text{Grounded Claims in Answer}|}{|\text{Total Claims in Answer}|}$$

### 2.2 Context Relevance
The proportion of retrieved context that is relevant to the question (measuring signal-to-noise ratio in retrieved chunks):
$$\text{Context Relevance} = \frac{|\text{Relevant Concepts in Context}|}{|\text{Total Concepts in Context}|}$$

### 2.3 Answer Relevance
Evaluates whether the response directly addresses the user query without drifting into irrelevant topics.

### 2.4 Citation Accuracy
The percentage of generated citations `[Document: Page]` that accurately point to the page containing the cited claim.
