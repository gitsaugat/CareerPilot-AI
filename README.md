# 🚀 CareerPilot AI

![CareerPilot AI](https://img.shields.io/badge/Status-Beta-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Python](https://img.shields.io/badge/Python-3.9+-yellow)

**CareerPilot AI** is your intelligent career co-pilot. Built to accelerate job searches, it combines advanced AI with powerful tracking tools to help you land your dream job faster.

Stop manually tweaking resumes and tracking applications in spreadsheets. Let CareerPilot AI handle the heavy lifting.

---

## ✨ Key Features

*   **📄 AI Resume Analysis**: Get instant feedback on your resume, tailored to specific job descriptions.
*   **🎯 Job Application Tracking**: Organize all your applications in one place. Track status, salary, interview dates, and notes.
*   **✍️ Smart Cover Letter Generator**: Generate personalized, impactful cover letters in seconds.
*   **🎙️ Interview Prep**: Practice with AI-generated interview questions based on the job description.
*   **🤝 Networking Assistant**: Draft perfect outreach messages for LinkedIn and email.
*   **💼 Negotiation Coach**: Get salary negotiation scripts and strategies.
*   **📊 Insights Dashboard**: Visualize your progress with real-time stats and activity feeds.

---

## 🛠️ Tech Stack

*   **Backend**: Python, Flask, SQLAlchemy
*   **Frontend**: HTML5, Bootstrap 5, Jinja2
*   **AI Engine**: Ollama (Running local LLMs like Llama 3 or Mistral)
*   **Database**: SQLite (Development)

---

## 🚀 Getting Started

Follow these instructions to set up the project on your local machine.

### Prerequisites

*   **Python 3.9+** installed.
*   **Git** installed.
*   **Ollama** installed and running. [Download Ollama here](https://ollama.com/).

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/CareerPilot-AI.git
    cd CareerPilot-AI
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up the AI Model**
    Make sure Ollama is running, then pull the required model (default is `gpt-oss:120b-cloud` or `llama3` depending on your config in `AI/main.py`):
    ```bash
    ollama pull llama3
    ```
    *(Note: You can change the model name in `AI/main.py` if needed)*

5.  **Initialize the Database**
    ```bash
    flask db upgrade
    ```

6.  **Run the Application**
    ```bash
    python main.py
    ```

7.  **Access the App**
    Open your browser and navigate to:
    `http://127.0.0.1:5000`

---

## 📸 Screenshots

*(Add screenshots of your Dashboard and Job Board here)*

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Happy Job Hunting! 🚀**
