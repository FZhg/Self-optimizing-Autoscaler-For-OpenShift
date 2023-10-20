import logging

import pandas as pd


# TODO: make this class thread-safe
class KnowledgeBase:

    def __init__(self, knowledge_csv_file_path):
        self.knowledge_csv_file_path = knowledge_csv_file_path
        self.knowledge_df = pd.read_csv(knowledge_csv_file_path)

    def get_current_knowledge(self):
        return self.current_knowledge

    def write_knowledge(self, knowledge):
        self.current_knowledge = knowledge
        self.knowledge_df = pd.concat([knowledge, self.knowledge_df], ignore_index=True)
        self.knowledge_df.to_csv(self.knowledge_csv_file_path, index=False)
        logging.debug("Current Knowledge:\n " + self.current_knowledge.to_string())
