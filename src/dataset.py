import json

class Dataset:
    def __init__(self, jsonl_path):
        """
        Initialize the dataset by loading the JSONL file.
        
        :param jsonl_path: Path to the JSONL file.
        """
        self.jsonl_path = jsonl_path
        self.data = self._load_data()

    def _load_data(self):
        """
        Load the JSONL file and parse its content.
        
        :return: A list of parsed JSON objects.
        """
        try:
            with open(self.jsonl_path, 'r', encoding='utf-8') as file:
                return [json.loads(line.strip()) for line in file if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at {self.jsonl_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSONL file: {e}")

    def __len__(self):
        """
        Return the total number of records in the dataset.
        
        :return: Number of records.
        """
        return len(self.data)

    def __getitem__(self, idx):
        """
        Retrieve a single record by index.
        
        :param idx: Index of the record.
        :return: The record at the specified index.
        """
        if idx < 0 or idx >= len(self.data):
            raise IndexError("Index out of range.")
        return self.data[idx]

    def get_questions(self):
        """
        Retrieve all questions from the dataset.
        
        :return: A list of questions.
        """
        return [item['question'] for item in self.data]

    def get_answers(self):
        """
        Retrieve all answers from the dataset.
        
        :return: A list of answers.
        """
        return [item['answer'] for item in self.data]

    def get_meta_info(self):
        """
        Retrieve all meta information from the dataset.
        
        :return: A list of meta information.
        """
        return [item['meta_info'] for item in self.data]

# Example usage
if __name__ == "__main__":
    # Provide the JSONL file path
    jsonl_path = "path_to_your_jsonl_file.jsonl"
    
    # Initialize the dataset
    dataset = Dataset(jsonl_path)
    
    # Example operations
    print(f"Total records: {len(dataset)}")
    print("First record:", dataset[0])
    print("All questions:", dataset.get_questions())
    print("All answers:", dataset.get_answers())