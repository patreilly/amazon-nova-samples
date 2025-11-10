# 🚀 Amazon Nova Multimodal Embedding Samples

Comprehensive sample code and tutorials for Amazon Nova's multimodal embeddings model, demonstrating how to generate embeddings from text, images, videos, and documents for real-world applications.

## 🌟 Overview

Amazon Nova provides state-of-the-art multimodal embeddings that can process and understand multiple types of content simultaneously. This repository contains practical examples, tutorials, and production-ready patterns.

## 📚 Getting Started Tutorials

| Tutorial | Content Type | Description |
|----------|-------------|-------------|
| 🔧 [`00_setup.ipynb`](getting-started/00_setup.ipynb) | Setup | Environment configuration and dependencies |
| 📝 [`01_basics_text_embeddings.ipynb`](getting-started/01_basics_text_embeddings.ipynb) | Text | Basic text processing and embedding generation |
| 🖼️ [`02_basics_image_embeddings.ipynb`](getting-started/02_basics_image_embeddings.ipynb) | Images | Image feature extraction and similarity matching |
| 🎬 [`03_basics_video_embeddings.ipynb`](getting-started/03_basics_video_embeddings.ipynb) | Video | Video content analysis and temporal embeddings |
| 🎵 [`04_basics_audio_embeddings.ipynb`](getting-started/04_basics_audio_embeddings.ipynb) | Audio | Audio content processing and feature extraction |
| 📄 [`05_example_document_embedding_retrieval.ipynb`](getting-started/05_example_document_embedding_retrieval.ipynb) | Documents | Multi-page document processing and chunking |
| 🔍 [`06_example_text_query_embeddings.ipynb`](getting-started/06_example_text_query_embeddings.ipynb) | Queries | Creating embeddings optimized for search |
| ⚡ [`07_batch_inference_sample.ipynb`](getting-started/07_batch_inference_sample.ipynb) | Batch | Batch processing for multiple embeddings |

## 🏗️ Repeatable Patterns

| Pattern | Technologies | Use Case | Description |
|---------|-------------|----------|-------------|
| 🎬 [**Video Embedding S3 Vector**](repeatable-patterns/video-embedding-s3-vector/) | Amazon Bedrock, S3 Vectors, Nova Embeddings | Video Search | Store and search video embeddings using S3 Vectors as vector database |
| 🌍 [**Multilingual Text Clustering**](repeatable-patterns/multilingual-text-clustering/) | Nova Embeddings, Clustering, Visualization | News Analysis | Cluster news articles across languages (German, Spanish, English) |
| 📚 [**Multimodal Doc Search Framework**](repeatable-patterns/multimodal-doc-search-opensource-framework/) | LangChain, LlamaIndex, FAISS | RAG Systems | Integration with open-source frameworks for document processing |
| 🛍️ [**Visual Product Search**](repeatable-patterns/visual-product-search-with-image-text-embeddings/) | OpenSearch Serverless, Berkeley Objects | E-commerce | Search products using text descriptions and images |

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **AI/ML** | Amazon Bedrock, Nova Multimodal Embeddings |
| **Vector Databases** | Amazon S3 Vectors, OpenSearch Serverless, FAISS |
| **Frameworks** | LangChain, LlamaIndex |
| **Languages** | Python, Jupyter Notebooks |
| **AWS Services** | Bedrock, S3, OpenSearch |

## 🎯 End-to-End Demo

For a complete demonstration of Nova multimodal embeddings in action, check out our comprehensive demo:

🔗 [**Sample Demo of Nova MME**](https://github.com/aws-samples/sample-demo-of-nova-mme) - Full end-to-end implementation showcasing multimodal agentic RAG

## 🚀 Quick Start

1. Start with `getting-started/00_setup.ipynb` for environment setup
2. Follow numbered tutorials in `getting-started/` to learn basics
3. Explore `repeatable-patterns/` for production use cases
4. Use patterns as templates for your applications

