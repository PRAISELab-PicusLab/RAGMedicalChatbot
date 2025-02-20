# 🩺 An *AI-Driven Medical Chatbot* Utilizing *Retrieval-Augmented Generation* for Improved Diagnostics and Patient Interaction
[![CC BY-NC 4.0][cc-by-nc-shield]][cc-by-nc]


Welcome to the repository for **RAG Medical Chatbot**, an innovative system designed to revolutionize medical diagnosis and treatment recommendations by integrating Retrieval-Augmented Generation (RAG) with advanced AI techniques, combining both retrieval systems and generative models for enhanced accuracy and user experience.

## 🎥 Demo (or GIF)
The following are some possible operational configurations of our medical chatbot.

1. #### The first use case does not involve the use of RAGs from trusted medical sources.
    <img src="https://github.com/user-attachments/assets/1a442f15-8f90-4bf1-8344-eafba7092e45" alt="NO RAG" width="600">

2. #### The second use case involves the use of Query Expansion and Reranking techniques downstream of RAG.
    <img src="https://github.com/user-attachments/assets/754053ab-fdc9-4235-9cc2-774cc1b0fb37" alt="RAG+Q+RR" width="600">

3. #### The third use case involves the use of Query Expansion, Reranking and Summarization techniques combined with a RAG approach.
    <img src="https://github.com/user-attachments/assets/a01392d5-b729-4568-b0ba-27c615309061" alt="RAG+Q+RR+S" width="600">

## 📊 Data Source
The dataset used as the knowledge base for the RAG phase was collected from *Italian medical forums* with a total of **268019 conversations** between *physicians* and *patients*. In total, there are **65 medical categories** to which discussions on these forums belong, and the most covered are certain areas such as *Psychology, Gastroenterology and Digestive Endoscopy, and Infectious Diseases*. In addition, articles from *Italian medical encyclopedias* have also been collected, with a total of **2981 articles**, most of which cover the field of *general medicine*.

## 🛠 Technologies Used
- **Python**: Core programming language ([Python](https://www.python.org/))
- **Pandas**: Data manipulation and analysis ([Pandas Documentation](https://pandas.pydata.org/))
- **MongoDB**: NoSQL database ([MongoDB Documentation](https://www.mongodb.com/docs/))
- **ChromaDB**: Vectorial database for RAG ([ChromaDB Documentation](https://docs.trychroma.com/))
- **Streamlit**: User interface development ([Streamlit Documentation](https://streamlit.io/))
- **HuggingFace**: Open-source provider of NLP technologies ([HuggingFace Documentation](https://huggingface.co/docs))
- **Nvidia NIM API**: Inference endpoint for various open-source LLMs ([Nvidia API Documentation](https://docs.api.nvidia.com/))

## 🔬 Methodological Workflow
**RAG-Med** follows a multi-step approach that ensures accurate information retrieval and generation through Query Expansion, Reranking, and Summarization:

1. **Query Expansion Phase**: User queries are enhanced using context-aware techniques, such as synonym expansion, to improve the system's ability to retrieve the most relevant medical information from a wide range of sources.
2. **Reranking + RAG Phase**: A combination of reranking algorithms (such as BM25) and the Retrieval-Augmented Generation (RAG) framework ensures that retrieved results are ranked according to their relevance, followed by a generative model that provides contextually accurate medical answers.
3. **Summarization Phase**: The system employs advanced summarization techniques to condense retrieved medical content into concise, user-friendly explanations, ensuring clarity and ease of understanding for the user.

    <img src="https://github.com/user-attachments/assets/b9b1148b-8db4-41ea-a6b5-e867d9292593" alt="Workflow" width="750">

## 🌟 Key Features
- **Query Expansion for Improved Retrieval**: Enhances user queries to ensure more accurate and contextually relevant information retrieval from medical sources.
- **RAG-Driven Responses**: Combines powerful retrieval systems with generative models to provide precise and relevant medical responses.
- **Advanced Reranking Algorithms**: Ensures that retrieved information is prioritized based on relevance, improving the quality and accuracy of results.
- **Summarization for Clarity**: Uses advanced summarization techniques to deliver concise, easy-to-understand explanations of complex medical content.
- **Enhanced Trustworthiness**: By combining query expansion, reranking, and the RAG framework, the system delivers highly reliable, contextually accurate, and trustworthy medical information, boosting confidence in the generated recommendations.

## 📂 Project Structure
The project is organized into the following folders:

- **extract**: Contains Python code for web scraping and the output data in CSV format 🕸️📊
- **transform**: Contains PySpark code for data transformations and the output data in JSON format 🔄📜
- **load**: Contains Python code for loading data into ChromaDB and MongoDB 📦🍃
- **dashboard**: Contains the Streamlit application and the databases 📊🌐

The root folder includes the `requirements.txt` file for installing dependencies. 💡  
Instructions for running the Streamlit application can be found in the `README.md` located in the corresponding folder. 📖

## 📈 Conclusions
**RAG Medical Chatbot** demonstrates the power of integrating Query Expansion, Reranking, and Retrieval-Augmented Generation (RAG) to enhance medical diagnosis and treatment suggestions. Our approach not only improves the accuracy of retrieved information but also strengthens the clarity and trustworthiness of generated responses. By separating the retrieval and generative components, we reduce bias and enhance the overall quality of decision-making, providing a more reliable and user-friendly medical AI system.

## ⚖ Ethical Considerations
**RAG Medical Chatbot** is designed to support, not replace, professional medical advice. Users should verify the chatbot's recommendations with authorised medical professionals, as the limitations of artificial intelligence may affect diagnostic accuracy. **⚠️ It is also recommended that this is only a demo for illustrative and educational purposes**. 

## 🙏 Acknowledgments
We would like to express our sincere gratitude to the creators of the Italian medical forums and encyclopedias used in this project, the developers of the Python libraries and tools that made this system possible, and our dedicated research team — *Antonio Romano, Giuseppe Riccio, Gian Marco Orlando, Diego Russo, Marco Postiglione, and Vincenzo Moscato* — for their invaluable contributions and efforts in bringing **RAG Medical Chatbot** to life.

## 📜 License

This work is licensed under a
[Creative Commons Attribution-NonCommercial 4.0 International License][cc-by-nc].

[![CC BY-NC 4.0][cc-by-nc-image]][cc-by-nc]

[cc-by-nc]: https://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-image]: https://licensebuttons.net/l/by-nc/4.0/88x31.png
[cc-by-nc-shield]: https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg
