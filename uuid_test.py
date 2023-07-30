import uuid
import base64

def generate_base64_uuid(length):
    # Generate a random UUID
    random_uuid = uuid.uuid4()

    # Convert the UUID to bytes and base64 encode it
    base64_uuid = base64.urlsafe_b64encode(random_uuid.bytes).decode('utf-8')

    # Keep only the first 5 characters
    return base64_uuid[:length]

def collision_chance(length):
    total_possible_combinations = 64 ** length
    total_generated_combinations = 10**7 # 10 million

    probability_collision = 1 - (1 - 1/total_possible_combinations) ** (total_generated_combinations * (total_generated_combinations - 1) / 2)
    print("Probability of collision:", probability_collision)

for i in range(1,10):
    print(generate_base64_uuid(7))
collision_chance(7)