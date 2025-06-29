import os
import pandas as pd
from rag_engine import add_documents_to_collection

# Folder containing the role-based files
data_dir = "data"

# Mapping of roles to their corresponding files
role_files = {
    "finance": ["financial_summary.md", "quarterly_financial_report.md"],
    "marketing": ["marketing_report_2024.md", "marketing_report_q1_2024.md", "marketing_report_q2_2024.md", "marketing_report_q3_2024.md", "marketing_report_q4_2024.md"],
    "hr_collection": ["hr_data.csv"],
    "engineering": ["engineering_master_doc.md"],
    "employee": ["employee_handbook.md"]
}

# Process and ingest each role's documents
for role, files in role_files.items():
    all_docs = []
    all_metadatas = []

    for filename in files:
        filepath = os.path.join(data_dir, filename)
        data_type = role.replace("_collection", "").lower()  # Normalize e.g. 'hr_collection' → 'hr'

        if filename.endswith(".md"):
            with open(filepath, "r", encoding="utf-8") as f:
                docs = f.read().split("\n\n")  # Split into chunks (paragraphs)
                all_docs.extend(docs)
                all_metadatas.extend([{"source": filename, "data_type": data_type}] * len(docs))

        elif filename.endswith(".csv"):
            df = pd.read_csv(filepath)
            docs = df.apply(lambda row: " | ".join(map(str, row)), axis=1).tolist()
            all_docs.extend(docs)
            all_metadatas.extend([{"source": filename, "data_type": data_type}] * len(docs))

    # Add to the shared ChromaDB collection
    print(f"✅ Adding {len(all_docs)} documents to role: {role}")
    add_documents_to_collection("finsolve_knowledge_base", all_docs, all_metadatas)
