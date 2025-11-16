# 🤖 RAG Chat Bot

AI-powered document analysis chatbot using Retrieval Augmented Generation (RAG).

## ✨ Features

- 📤 **Upload Documents** - Support for PDF and TXT files
- 💬 **Ask Questions** - Natural language Q&A about your documents
- ⚡ **Fast Search** - Keyword-based document retrieval
- 📱 **Beautiful UI** - Built with Streamlit for great user experience
- 💾 **Chat History** - Keep track of your conversations
- 🔐 **Privacy** - All processing done locally

## 🛠️ Tech Stack

- **Python 3.8+** - Programming language
- **Streamlit** - Web application framework
- **LangChain** - Document processing and retrieval
- **FAISS** - Vector similarity search
- **PyPDF** - PDF document handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
git clone https://github.com/AhmedEkramy/rag-chat-bot.git
cd rag-chat-bot



2. **Create a virtual environment**
python -m venv venv
venv\Scripts\activate



3. **Install dependencies**
pip install -r requirements.txt



### Usage

streamlit run app.py



Then:
1. Open browser to `http://localhost:8501`
2. Upload a PDF or TXT file in the sidebar
3. Click "Load Documents"
4. Ask questions about your document in the chat box
5. Get instant answers!

## 📝 Example

**Document Content:**
Python is a high-level programming language known for its simplicity.
It supports multiple programming paradigms and has a rich ecosystem of libraries.


**Q&A:**
Q: What is Python?
A: Found in your documents: Python is a high-level programming language
known for its simplicity. It supports multiple programming paradigms...



## 📦 Project Structure

rag-chat-bot/
├── app.py # Main Streamlit application
├── rag_bot.py # RAG Bot logic and document processing
├── requirements.txt # Python dependencies
├── .gitignore # Git ignore rules
├── README.md # This file
└── sample.txt # Sample document for testing



## 🔧 Configuration

### Optional: Add Environment Variables

Create `.env` file in the project root:
For future OpenAI integration
OPENAI_API_KEY=your_api_key_here



## 🎯 How It Works

1. **Document Upload** - Upload your PDF/TXT files
2. **Text Extraction** - Extract and parse document content
3. **Text Splitting** - Split documents into manageable chunks
4. **Keyword Search** - Search documents based on question keywords
5. **Response Generation** - Extract and display relevant content

## 📈 Future Improvements

- [ ] Add semantic search with embeddings
- [ ] Integrate OpenAI GPT-4 for better answers
- [ ] Support more file formats (DOCX, PPT, etc.)
- [ ] Export chat history to PDF
- [ ] Multi-document analysis
- [ ] Cloud deployment (AWS, Google Cloud)
- [ ] User authentication
- [ ] Database for saving conversations

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Python PyPDF Documentation](https://pypdf.readthedocs.io/)

## 🐛 Troubleshooting

### Issue: Module not found error
pip install -r requirements.txt



### Issue: Streamlit not recognized
python -m streamlit run app.py



### Issue: Large file upload
- Maximum upload size: 200MB per file
- Split large PDFs into smaller chunks

## 📄 License

MIT License - feel free to use, modify, and distribute this project!

See [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ahmed Ekramy**

- 🔗 GitHub: [@AhmedEkramy](https://github.com/AhmedEkramy)
- 💼 Upwork: [Ahmed Ekramy](https://upwork.com/freelancers/ahmedekramy)
- 📧 Email: ahmedekramy303@gmail.com
- 💻 Portfolio: [Ahmed Gaiter](https://portfolio.com/ahmedekramy)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing [GitHub Issues](https://github.com/AhmedEkramy/rag-chat-bot/issues)
3. Create a new issue with detailed description
4. Contact via email

## ⭐ Show Your Support

If you find this project helpful, please:
- Give it a ⭐ star on GitHub
- Share it with others
- Contribute improvements

---


*Last updated: November 2025*
