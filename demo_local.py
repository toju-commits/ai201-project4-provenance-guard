import json
from app import app

def show_step(message):
    print()
    print("=" * 60)
    print(message)
    print("=" * 60)

def pretty(data):
    print(json.dumps(data, indent=2))

client = app.test_client()

show_step("1. Checking that Provenance Guard is running")
pretty(client.get("/").get_json())

show_step("2. Submission 1: polished AI-ish sample")
response1 = client.post("/submit", json={
    "text": "In conclusion, the modern world is a complex tapestry of innovation, creativity, and human ambition. It is important to note that technology continues to reshape the way individuals communicate, create, and imagine the future.",
    "creator_id": "creator_001"
})
data1 = response1.get_json()
pretty(data1)

show_step("3. Submission 2: rougher human-style creative sample")
response2 = client.post("/submit", json={
    "text": "I wrote the first line at 2 a.m. and hated it. Then I kept it anyway, because sometimes the ugly sentence is the only honest one in the room.",
    "creator_id": "creator_002"
})
pretty(response2.get_json())

show_step("4. Submission 3: mixed creative sample")
response3 = client.post("/submit", json={
    "text": "The city moved like a machine, but I still felt human inside it. Every window carried a small blue glow, and every street sounded like someone trying to remember their own name.",
    "creator_id": "creator_003"
})
pretty(response3.get_json())

show_step("5. Appeal workflow using the first content_id")
appeal_response = client.post("/appeal", json={
    "content_id": data1["content_id"],
    "creator_reasoning": "I wrote this myself and I believe the system may have misread my polished style as AI-generated."
})
pretty(appeal_response.get_json())

show_step("6. Structured audit log with submissions and appeal")
pretty(client.get("/log?limit=10").get_json())

show_step("7. Rate limit proof: repeated submissions until 429 appears")
for i in range(1, 13):
    rate_response = client.post("/submit", json={
        "text": f"This is rate limit test submission number {i}. It is intentionally simple.",
        "creator_id": "rate_test_user"
    })

    if rate_response.status_code == 429:
        print(f"Request {i} failed as expected with status 429")
        pretty(rate_response.get_json())
    else:
        rate_data = rate_response.get_json()
        print(f"Request {i} succeeded with confidence {rate_data.get('confidence')}")

show_step("Demo script complete")
print("You showed: /submit, different confidence scores, transparency labels, both signal scores, /appeal, /log, and rate limiting.")
