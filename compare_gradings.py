import json


def load_data(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def filter_data(data):
    return [item for item in data if item["expert_grading"]["expert_name_correct"] is not None]


def compare_gradings(pin):
    name_same = pin["name_correct"] == pin["expert_grading"]["expert_name_correct"]
    description_same = pin["description_correct"] == pin["expert_grading"]["expert_description_correct"]
    return name_same and description_same


def calculate_accuracies(data_filtered):
    compared_overall = [compare_gradings(pin) for pin in data_filtered]
    overall_accuracy = sum(compared_overall) / len(compared_overall)

    name_matches = [pin["name_correct"] == pin["expert_grading"]["expert_name_correct"] for pin in data_filtered]
    description_matches = [pin["description_correct"] == pin["expert_grading"]["expert_description_correct"] for pin in data_filtered]

    name_accuracy = sum(name_matches) / len(data_filtered)
    description_accuracy = sum(description_matches) / len(data_filtered)

    return name_accuracy, description_accuracy, overall_accuracy


def main():
    data = load_data("random_pins.json")
    data_filtered = filter_data(data)
    print(f"Using: {len(data_filtered)} / {len(data)} pins")

    name_accuracy, description_accuracy, overall_accuracy = calculate_accuracies(data_filtered)

    print(f"Name Accuracy: {name_accuracy:.4f}")
    print(f"Description Accuracy: {description_accuracy:.4f}")
    print(f"Overall Accuracy (Exact Match): {overall_accuracy:.4f}")


if __name__ == "__main__":
    main()
