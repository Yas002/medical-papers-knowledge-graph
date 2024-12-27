import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_constraints(session):
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Paper) REQUIRE p.paper_id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Author) REQUIRE a.full_name IS UNIQUE")


def load_json_files_to_neo4j(json_folder):
    files = [f for f in os.listdir(json_folder) if f.endswith(".json")]

    with driver.session() as session:
        create_constraints(session)

        for filename in files:
            filepath = os.path.join(json_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            paper_id = data.get("paper_id", "")
            title = data.get("title", "")
            abstract = data.get("abstract", "")
            body_text = data.get("body_text", [])
            back_matter = data.get("back_matter", [])
            
            session.run(
                """
                MERGE (p:Paper {paper_id: $paper_id})
                ON CREATE SET 
                    p.title = $title,
                    p.abstract = $abstract,
                    p.body_text = $body_text,
                    p.back_matter = $back_matter
                """,
                paper_id=paper_id,
                title=title,
                abstract=abstract,
                body_text=body_text,
                back_matter=back_matter
            )

            authors = data.get("authors", [])
            for author in authors:
                first_name = author.get("first", "")
                last_name = author.get("last", "")
                full_name = f"{first_name} {last_name}".strip()

                affiliation = author.get("affiliation", {})
                email = author.get("email", "")
                institution = affiliation.get("institution", "")
                laboratory = affiliation.get("laboratory", "")
                location = affiliation.get("location", {})
                settlement = location.get("settlement", "")
                region = location.get("region", "")

                session.run(
                    """
                    MERGE (a:Author {full_name: $full_name})
                    ON CREATE SET 
                        a.email = $email,
                        a.institution = $institution,
                        a.laboratory = $laboratory,
                        a.settlement = $settlement,
                        a.region = $region
                    MERGE (p:Paper {paper_id: $paper_id})
                    MERGE (a)-[:AUTHORED]->(p)
                    """,
                    full_name=full_name,
                    paper_id=paper_id,
                    email=email,
                    institution=institution,
                    laboratory=laboratory,
                    settlement=settlement,
                    region=region
                )

            keywords = data.get("pdf_parse_keywords", [])
            for kw in keywords:
                session.run(
                    """
                    MERGE (k:Keyword {name: $kw})
                    MERGE (p:Paper {paper_id: $paper_id})
                    MERGE (p)-[:HAS_KEYWORD]->(k)
                    """,
                    kw=kw,
                    paper_id=paper_id
                )

            # creating "has reference to" relationships
            references = data.get("bibref_titles", [])
            for ref_title in references:
                session.run(
                    """
                    MERGE (r:Reference {title: $ref_title})
                    MERGE (p:Paper {paper_id: $paper_id})
                    MERGE (p)-[:HAS_REFERENCE]->(r)
                    """,
                    ref_title=ref_title,
                    paper_id=paper_id
                )

if __name__ == "__main__":
    json_folder = r"c:/Users/Yassine/Downloads/TanitAI_RAG/data/processed"
    load_json_files_to_neo4j(json_folder)
    print("Knowledge graph created and populated with JSON files.")