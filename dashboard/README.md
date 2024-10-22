# Dashboard Execution Instructions 🚀

To run the Streamlit application, follow these steps:

1. **Install the dependencies** specified in `requirements.txt` 🛠️
   
   ```
   pip install -r requirements.txt
   ```

2. **Start MongoDB** with the following command: 🍃

   ```
   mongod --port 27017 --dbpath C:\<project_path>\dashboard\mongodb
   ```

3. **Start ChromaDB** in the environment where it is installed with this command: 🧬

   ```
   chroma run --host localhost --port 8000 --path ./dashboard/chromadb
   ```

4. **Run Streamlit** in the environment where it is installed with this command: 🌐

   ```
   streamlit run ./dashboard/Homepage.py
   ```

Now you're ready to explore the dashboard! 🎉