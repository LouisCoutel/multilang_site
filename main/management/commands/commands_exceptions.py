class GeneratingDataError(Exception):
    def __init__(self, dummy_data):
        super().__init__()
        self.message = f"Error generating dummy data. Data generated: {dummy_data}"
